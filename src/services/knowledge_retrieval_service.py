"""
MINDSETHAPPYBOT - Knowledge Retrieval Service
Hybrid RAG implementation with 3 sources:
1. User Memory (moments) - personal history
2. Knowledge Base (knowledge_chunks) - uploaded documents
3. Model parametric knowledge - always available fallback

Features:
- Query type classification (A/B/C routing)
- Vector similarity search with thresholds
- Recency boosting for moments
- Usage count tracking for KB
- Anti-repetition fingerprinting
"""
import logging
import hashlib
import re
import time
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from openai import AsyncOpenAI
from sqlalchemy import text, select, and_

from src.config import get_settings
from src.db.database import get_session
from src.db.models import User, Moment, Conversation
from src.services.embedding_service import EmbeddingService
from src.services.api_usage_service import APIUsageService

logger = logging.getLogger(__name__)


# Configuration constants
MOMENTS_TOP_K = 4
KB_TOP_K = 5
SIMILARITY_THRESHOLD = 0.40  # Below this, don't include source (lowered for Russian text)
MAX_CONTEXT_CHARS = 4500  # ~1200-1500 tokens
RECENCY_BOOST_DAYS = 7  # Moments within this period get boosted
RECENCY_BOOST_FACTOR = 0.05  # How much to boost recent moments
FINGERPRINT_HISTORY_LIMIT = 50  # How many past bot replies to check for repetition


@dataclass
class RetrievedMoment:
    """A moment retrieved from vector search with metadata"""
    id: int
    content: str
    similarity: float
    created_at: datetime
    boosted_score: float  # After recency boost


@dataclass
class RetrievedChunk:
    """A knowledge chunk retrieved from vector search"""
    id: int
    knowledge_base_id: int
    content: str
    similarity: float


@dataclass
class RAGContext:
    """Complete RAG context for response generation"""
    query_type: str  # 'A', 'B', 'C'
    moments: List[RetrievedMoment]
    kb_chunks: List[RetrievedChunk]
    moment_ids: List[int]
    moment_scores: List[float]
    kb_chunk_ids: List[int]
    kb_item_ids: List[int]
    kb_scores: List[float]
    recent_fingerprints: List[str]
    recent_responses: List[str]  # Short excerpts for anti-repetition


class KnowledgeRetrievalService:
    """Service for hybrid RAG retrieval"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.embedding_service = EmbeddingService()
        self.analysis_model = settings.openai_analysis_model

    async def classify_query_type(self, query: str) -> str:
        """
        Classify query into types:
        - Type A: About user / emotions / progress - moments required, KB optional
        - Type B: How to support / formulate / practices - KB required, moments optional
        - Type C: General questions - KB if available, otherwise model-only
        """
        start_time = time.time()
        success = True
        error_msg = None
        input_tokens = 0
        output_tokens = 0

        try:
            response = await self.client.chat.completions.create(
                model=self.analysis_model,
                messages=[
                    {
                        "role": "system",
                        "content": """Classify the user's message into one of three types:
A - Personal/emotional: The user shares feelings, talks about themselves, their progress, mood, or personal experiences.
B - Seeking advice/techniques: The user asks how to do something, requests support formulations, practices, or techniques.
C - General/other: General questions, greetings, unclear intent.

Reply with ONLY a single letter: A, B, or C."""
                    },
                    {"role": "user", "content": query}
                ],
                max_tokens=5,
                temperature=0,
            )

            if response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            result = response.choices[0].message.content.strip().upper()
            if result not in ['A', 'B', 'C']:
                result = 'C'  # Default to general

            logger.debug(f"Query classified as type {result}: {query[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Query classification failed: {e}")
            success = False
            error_msg = str(e)
            return 'C'  # Default to general on error

        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            await APIUsageService.log_usage(
                api_provider="openai",
                model=self.analysis_model,
                operation_type="query_classification",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                success=success,
                error_message=error_msg,
            )

    async def search_moments(
        self,
        telegram_id: int,
        query_embedding: List[float],
        limit: int = MOMENTS_TOP_K,
    ) -> List[RetrievedMoment]:
        """
        Search user's moments with vector similarity and recency boost
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return []

            # Build embedding string for pgvector (must be embedded in SQL for asyncpg)
            embedding_literal = "'" + "[" + ",".join(f"{x:.10g}" for x in query_embedding) + "]'::vector"
            fetch_limit = limit * 2  # Get extra to filter by threshold

            # Vector search with cosine distance
            # Note: Using f-string for embedding literal because asyncpg doesn't support ::vector cast with params
            result = await session.execute(
                text(f"""
                    SELECT
                        id,
                        content,
                        created_at,
                        1 - (embedding <=> {embedding_literal}) as similarity
                    FROM moments
                    WHERE user_id = :user_id
                    AND embedding IS NOT NULL
                    ORDER BY embedding <=> {embedding_literal}
                    LIMIT :limit
                """),
                {
                    "user_id": user.id,
                    "limit": fetch_limit,
                }
            )
            rows = result.fetchall()

            # Filter by threshold and apply recency boost
            moments = []
            now = datetime.utcnow()
            recency_cutoff = now - timedelta(days=RECENCY_BOOST_DAYS)

            for row in rows:
                similarity = float(row.similarity)
                if similarity < SIMILARITY_THRESHOLD:
                    continue

                # Apply recency boost
                boosted_score = similarity
                if row.created_at > recency_cutoff:
                    # Days since creation (0 = today, 7 = week ago)
                    days_old = (now - row.created_at).days
                    # Boost decreases linearly with age
                    boost = RECENCY_BOOST_FACTOR * (1 - days_old / RECENCY_BOOST_DAYS)
                    boosted_score = min(1.0, similarity + boost)

                moments.append(RetrievedMoment(
                    id=row.id,
                    content=row.content,
                    similarity=similarity,
                    created_at=row.created_at,
                    boosted_score=boosted_score,
                ))

            # Sort by boosted score and limit
            moments.sort(key=lambda m: m.boosted_score, reverse=True)
            return moments[:limit]

    async def search_knowledge_base(
        self,
        query_embedding: List[float],
        limit: int = KB_TOP_K,
    ) -> List[RetrievedChunk]:
        """
        Search knowledge base chunks with vector similarity
        """
        async with get_session() as session:
            # Build embedding literal for pgvector (must be embedded in SQL for asyncpg)
            embedding_literal = "'" + "[" + ",".join(f"{x:.10g}" for x in query_embedding) + "]'::vector"
            fetch_limit = limit * 2  # Get extra to filter by threshold

            # Vector search with cosine distance
            # Note: Using f-string for embedding literal because asyncpg doesn't support ::vector cast with params
            result = await session.execute(
                text(f"""
                    SELECT
                        kc.id,
                        kc.knowledge_base_id,
                        kc.content,
                        1 - (kc.embedding <=> {embedding_literal}) as similarity
                    FROM knowledge_chunks kc
                    JOIN knowledge_base kb ON kc.knowledge_base_id = kb.id
                    WHERE kc.embedding IS NOT NULL
                    AND kb.indexing_status = 'indexed'
                    ORDER BY kc.embedding <=> {embedding_literal}
                    LIMIT :limit
                """),
                {
                    "limit": fetch_limit,
                }
            )
            rows = result.fetchall()

            # Filter by threshold
            chunks = []
            for row in rows:
                similarity = float(row.similarity)
                if similarity < SIMILARITY_THRESHOLD:
                    continue

                chunks.append(RetrievedChunk(
                    id=row.id,
                    knowledge_base_id=row.knowledge_base_id,
                    content=row.content,
                    similarity=similarity,
                ))

            return chunks[:limit]

    async def get_recent_fingerprints(
        self,
        telegram_id: int,
        limit: int = FINGERPRINT_HISTORY_LIMIT,
    ) -> Tuple[List[str], List[str]]:
        """
        Get fingerprints and short excerpts of recent bot replies for anti-repetition
        Returns: (fingerprints, short_excerpts)
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return [], []

            # Get recent bot replies
            result = await session.execute(
                select(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user.id,
                        Conversation.message_type == "bot_reply",
                    )
                )
                .order_by(Conversation.created_at.desc())
                .limit(limit)
            )
            conversations = result.scalars().all()

            fingerprints = []
            excerpts = []

            for conv in conversations:
                # Get fingerprint from metadata or compute it
                fp = None
                if conv.message_metadata and "answer_fingerprint" in conv.message_metadata:
                    fp = conv.message_metadata["answer_fingerprint"]
                else:
                    fp = self.compute_fingerprint(conv.content)

                fingerprints.append(fp)
                # Short excerpt for context (first 100 chars)
                excerpts.append(conv.content[:100] if conv.content else "")

            return fingerprints, excerpts

    @staticmethod
    def compute_fingerprint(text: str) -> str:
        """
        Compute fingerprint for text to detect repetition.
        Normalizes text (lowercase, remove punctuation/whitespace) then hashes.
        """
        if not text:
            return ""

        # Normalize: lowercase, remove punctuation and extra whitespace
        normalized = text.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        normalized = re.sub(r'\s+', ' ', normalized).strip()  # Normalize whitespace

        # Hash the normalized text
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]

    async def retrieve_context(
        self,
        telegram_id: int,
        query: str,
    ) -> RAGContext:
        """
        Main retrieval method - gets all relevant context for response generation.

        Returns RAGContext with:
        - Classified query type
        - Retrieved moments (user memory)
        - Retrieved KB chunks (knowledge base)
        - IDs and scores for logging
        - Recent fingerprints for anti-repetition
        """
        # Step 1: Classify query type
        query_type = await self.classify_query_type(query)

        # Step 2: Create query embedding
        query_embedding = await self.embedding_service.create_embedding(query)
        if query_embedding is None:
            logger.warning("Failed to create query embedding")
            return RAGContext(
                query_type=query_type,
                moments=[],
                kb_chunks=[],
                moment_ids=[],
                moment_scores=[],
                kb_chunk_ids=[],
                kb_item_ids=[],
                kb_scores=[],
                recent_fingerprints=[],
                recent_responses=[],
            )

        # Step 3: Search based on query type
        moments = []
        kb_chunks = []

        if query_type == 'A':
            # Personal/emotional - moments required, KB optional
            moments = await self.search_moments(telegram_id, query_embedding)
            kb_chunks = await self.search_knowledge_base(query_embedding, limit=3)
        elif query_type == 'B':
            # Seeking advice - KB required, moments optional
            kb_chunks = await self.search_knowledge_base(query_embedding)
            moments = await self.search_moments(telegram_id, query_embedding, limit=2)
        else:
            # General - try both, prefer KB
            kb_chunks = await self.search_knowledge_base(query_embedding, limit=4)
            moments = await self.search_moments(telegram_id, query_embedding, limit=2)

        # Step 4: Get anti-repetition data
        fingerprints, excerpts = await self.get_recent_fingerprints(telegram_id)

        # Step 5: Truncate context if too long
        total_chars = sum(len(m.content) for m in moments) + sum(len(c.content) for c in kb_chunks)
        if total_chars > MAX_CONTEXT_CHARS:
            # Prioritize based on query type
            if query_type == 'A':
                # Keep moments, truncate KB
                kb_chars = sum(len(c.content) for c in kb_chunks)
                while kb_chars > MAX_CONTEXT_CHARS // 3 and kb_chunks:
                    kb_chunks.pop()
                    kb_chars = sum(len(c.content) for c in kb_chunks)
            elif query_type == 'B':
                # Keep KB, truncate moments
                moment_chars = sum(len(m.content) for m in moments)
                while moment_chars > MAX_CONTEXT_CHARS // 4 and moments:
                    moments.pop()
                    moment_chars = sum(len(m.content) for m in moments)

        return RAGContext(
            query_type=query_type,
            moments=moments,
            kb_chunks=kb_chunks,
            moment_ids=[m.id for m in moments],
            moment_scores=[m.boosted_score for m in moments],
            kb_chunk_ids=[c.id for c in kb_chunks],
            kb_item_ids=list(set(c.knowledge_base_id for c in kb_chunks)),
            kb_scores=[c.similarity for c in kb_chunks],
            recent_fingerprints=fingerprints,
            recent_responses=excerpts,
        )

    async def increment_kb_usage(self, kb_item_ids: List[int]) -> None:
        """
        Increment usage_count for knowledge base items that were used in a response.
        """
        if not kb_item_ids:
            return

        async with get_session() as session:
            for kb_id in set(kb_item_ids):  # Dedupe
                await session.execute(
                    text("""
                        UPDATE knowledge_base
                        SET usage_count = usage_count + 1,
                            updated_at = NOW()
                        WHERE id = :id
                    """),
                    {"id": kb_id}
                )
            await session.commit()
            logger.debug(f"Incremented usage_count for KB items: {kb_item_ids}")

    def build_context_prompt(self, context: RAGContext) -> str:
        """
        Build the context section of the prompt from RAG results.
        """
        parts = []

        # User memory section
        if context.moments:
            parts.append("=== USER'S PERSONAL HISTORY (from their previous positive moments) ===")
            for i, m in enumerate(context.moments, 1):
                # Truncate very long moments
                content = m.content[:300] + "..." if len(m.content) > 300 else m.content
                parts.append(f"{i}. {content}")
            parts.append("")

        # Knowledge base section
        if context.kb_chunks:
            parts.append("=== KNOWLEDGE BASE (reference material for supportive responses) ===")
            for i, c in enumerate(context.kb_chunks, 1):
                # Truncate very long chunks
                content = c.content[:400] + "..." if len(c.content) > 400 else c.content
                parts.append(f"{i}. {content}")
            parts.append("")

        if not parts:
            return ""

        return "\n".join(parts)

    def build_anti_repetition_instruction(self, context: RAGContext) -> str:
        """
        Build instruction to avoid repeating recent responses.
        """
        if not context.recent_responses:
            return ""

        # Only include first 10 recent excerpts to not bloat the prompt
        recent = context.recent_responses[:10]
        if not recent:
            return ""

        excerpts = "\n".join([f"- {r[:60]}..." for r in recent if r])

        return f"""
=== ANTI-REPETITION RULE ===
Do NOT repeat these recent response patterns:
{excerpts}

Generate a fresh, unique response. Same meaning is OK, but different wording required.
"""

    def build_rag_metadata(
        self,
        context: RAGContext,
        response_text: str,
    ) -> Dict[str, Any]:
        """
        Build metadata dict to store with the conversation record.
        """
        return {
            "rag_mode": context.query_type,
            "moment_ids": context.moment_ids,
            "moment_scores": [round(s, 4) for s in context.moment_scores],
            "kb_chunk_ids": context.kb_chunk_ids,
            "kb_item_ids": context.kb_item_ids,
            "kb_scores": [round(s, 4) for s in context.kb_scores],
            "answer_fingerprint": self.compute_fingerprint(response_text),
            "retrieval_used": bool(context.moments or context.kb_chunks),
            "moments_count": len(context.moments),
            "kb_chunks_count": len(context.kb_chunks),
        }
