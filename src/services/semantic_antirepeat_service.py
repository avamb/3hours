"""
MINDSETHAPPYBOT - Semantic Anti-Repeat Service
Compares new bot replies with recent replies using embeddings to prevent
semantically similar repeats.

Features:
- Stores embeddings of bot replies in conversation metadata
- Compares new reply embeddings with recent reply embeddings using cosine similarity
- Regenerates reply if similarity exceeds configurable threshold
- Logs metrics about semantic repetitions
"""
import logging
import math
import time
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from sqlalchemy import select, and_

from src.config import get_settings
from src.db.database import get_session
from src.db.models import User, Conversation
from src.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


# Configuration constants
SEMANTIC_ANTIREPEAT_THRESHOLD = 0.85  # Cosine similarity threshold (0.85 = very similar)
SEMANTIC_ANTIREPEAT_HISTORY_LIMIT = 10  # How many recent replies to check
EMBEDDING_DIMENSION = 1536  # OpenAI text-embedding-3-small dimension


@dataclass
class SemanticRepeatCheckResult:
    """Result of semantic repeat check"""
    is_repeat: bool
    max_similarity: float
    similar_reply_id: Optional[int]
    similar_reply_excerpt: Optional[str]
    embeddings_checked: int
    check_time_ms: int


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    Returns value between -1 and 1, where 1 means identical direction.
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


class SemanticAntirepeatService:
    """Service for semantic anti-repeat using embeddings"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        settings = get_settings()
        # Load threshold from settings, use default if not set
        self.similarity_threshold = getattr(
            settings,
            'semantic_antirepeat_threshold',
            SEMANTIC_ANTIREPEAT_THRESHOLD
        )
        self.history_limit = SEMANTIC_ANTIREPEAT_HISTORY_LIMIT

    async def get_recent_reply_embeddings(
        self,
        telegram_id: int,
        limit: int = None,
    ) -> List[Tuple[int, List[float], str]]:
        """
        Get embeddings of recent bot replies from conversation metadata.

        Returns list of tuples: (conversation_id, embedding, content_excerpt)
        Only returns replies that have embeddings stored in metadata.
        """
        if limit is None:
            limit = self.history_limit

        try:
            async with get_session() as session:
                # Get user
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    return []

                # Get recent bot replies with embeddings
                result = await session.execute(
                    select(Conversation)
                    .where(
                        and_(
                            Conversation.user_id == user.id,
                            Conversation.message_type == "bot_reply",
                        )
                    )
                    .order_by(Conversation.created_at.desc())
                    .limit(limit * 2)  # Get extra in case some don't have embeddings
                )
                conversations = result.scalars().all()

                embeddings = []
                for conv in conversations:
                    if conv.message_metadata and "reply_embedding" in conv.message_metadata:
                        embedding = conv.message_metadata["reply_embedding"]
                        if isinstance(embedding, list) and len(embedding) == EMBEDDING_DIMENSION:
                            excerpt = conv.content[:100] if conv.content else ""
                            embeddings.append((conv.id, embedding, excerpt))
                            if len(embeddings) >= limit:
                                break

                return embeddings

        except Exception as e:
            logger.error(f"Failed to get recent reply embeddings: {e}")
            return []

    async def check_semantic_repeat(
        self,
        telegram_id: int,
        new_reply_text: str,
        new_reply_embedding: Optional[List[float]] = None,
    ) -> SemanticRepeatCheckResult:
        """
        Check if a new reply is semantically similar to recent replies.

        Args:
            telegram_id: User's Telegram ID
            new_reply_text: The new reply text to check
            new_reply_embedding: Pre-computed embedding (optional, will compute if not provided)

        Returns:
            SemanticRepeatCheckResult with similarity info
        """
        start_time = time.time()

        # Get embedding for new reply if not provided
        if new_reply_embedding is None:
            new_reply_embedding = await self.embedding_service.create_embedding(new_reply_text)
            if new_reply_embedding is None:
                logger.warning("Failed to create embedding for semantic repeat check")
                return SemanticRepeatCheckResult(
                    is_repeat=False,
                    max_similarity=0.0,
                    similar_reply_id=None,
                    similar_reply_excerpt=None,
                    embeddings_checked=0,
                    check_time_ms=int((time.time() - start_time) * 1000),
                )

        # Get recent reply embeddings
        recent_embeddings = await self.get_recent_reply_embeddings(telegram_id)

        if not recent_embeddings:
            return SemanticRepeatCheckResult(
                is_repeat=False,
                max_similarity=0.0,
                similar_reply_id=None,
                similar_reply_excerpt=None,
                embeddings_checked=0,
                check_time_ms=int((time.time() - start_time) * 1000),
            )

        # Calculate similarities
        max_similarity = 0.0
        most_similar_id = None
        most_similar_excerpt = None

        for conv_id, embedding, excerpt in recent_embeddings:
            similarity = cosine_similarity(new_reply_embedding, embedding)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_id = conv_id
                most_similar_excerpt = excerpt

        is_repeat = max_similarity >= self.similarity_threshold
        check_time_ms = int((time.time() - start_time) * 1000)

        if is_repeat:
            logger.info(
                f"Semantic repeat detected for user {telegram_id}: "
                f"similarity={max_similarity:.4f} (threshold={self.similarity_threshold}), "
                f"similar_to_conv={most_similar_id}"
            )
        else:
            logger.debug(
                f"Semantic repeat check passed for user {telegram_id}: "
                f"max_similarity={max_similarity:.4f} (threshold={self.similarity_threshold})"
            )

        return SemanticRepeatCheckResult(
            is_repeat=is_repeat,
            max_similarity=max_similarity,
            similar_reply_id=most_similar_id,
            similar_reply_excerpt=most_similar_excerpt,
            embeddings_checked=len(recent_embeddings),
            check_time_ms=check_time_ms,
        )

    async def create_reply_embedding(self, reply_text: str) -> Optional[List[float]]:
        """
        Create embedding for a reply text.
        Wrapper around embedding service for convenience.
        """
        return await self.embedding_service.create_embedding(reply_text)

    async def is_repetitive(
        self,
        telegram_id: int,
        new_response: str,
    ) -> bool:
        """
        Simple convenience method to check if a response is repetitive.

        Creates embedding and checks semantic similarity with recent replies.
        Returns True if the response is too similar to recent replies.

        Args:
            telegram_id: User's Telegram ID
            new_response: The new response text to check

        Returns:
            True if the response is semantically repetitive, False otherwise
        """
        try:
            embedding = await self.create_reply_embedding(new_response)
            if embedding is None:
                return False  # Can't check, assume not repetitive

            check_result = await self.check_semantic_repeat(
                telegram_id=telegram_id,
                new_reply_text=new_response,
                new_reply_embedding=embedding,
            )
            return check_result.is_repeat
        except Exception as e:
            logger.error(f"Error in is_repetitive check: {e}")
            return False

    def build_embedding_metadata(
        self,
        embedding: List[float],
        repeat_check_result: Optional[SemanticRepeatCheckResult] = None,
    ) -> Dict[str, Any]:
        """
        Build metadata dict containing embedding and repeat check info.
        This should be merged with existing conversation metadata.
        """
        metadata = {
            "reply_embedding": embedding,
        }

        if repeat_check_result:
            metadata["semantic_repeat_check"] = {
                "was_repeat": repeat_check_result.is_repeat,
                "max_similarity": round(repeat_check_result.max_similarity, 4),
                "similar_reply_id": repeat_check_result.similar_reply_id,
                "embeddings_checked": repeat_check_result.embeddings_checked,
                "check_time_ms": repeat_check_result.check_time_ms,
            }

        return metadata


# Singleton instance for reuse
_service_instance: Optional[SemanticAntirepeatService] = None


def get_semantic_antirepeat_service() -> SemanticAntirepeatService:
    """Get singleton instance of SemanticAntirepeatService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = SemanticAntirepeatService()
    return _service_instance
