"""
MINDSETHAPPYBOT - Conversation Memory Service
Extracts and stores memory-worthy facts from user conversations.

This service implements per-user isolated dialog vector memory:
1. Extracts "memory-worthy" content from conversations (facts, people, preferences, etc.)
2. Filters out garbage (short messages, emojis, ok/yes/no, etc.)
3. Uses LLM to classify and extract canonical facts
4. Stores with embeddings for vector retrieval
5. Ensures strict user isolation
6. Provides anti-hallucination retrieval for "remember" queries
"""
import logging
import hashlib
import re
import time
import json
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from openai import AsyncOpenAI
from sqlalchemy import select, and_, text

from src.config import get_settings
from src.db.database import get_session
from src.db.models import User, Conversation, ConversationMemory
from src.services.embedding_service import EmbeddingService
from src.services.api_usage_service import APIUsageService

logger = logging.getLogger(__name__)


# Configuration
MIN_MESSAGE_LENGTH = 12  # Minimum characters to consider
GARBAGE_PATTERNS = [
    r'^[😀-🙏💀-💯🌀-🗿🤐-🤿🥀-🥿🦀-🦿🧀-🧿🩰-🩻🪀-🪿]+$',  # Only emojis
    r'^[^\w\s]*$',  # Only punctuation
    r'^(ok|ок|да|нет|ага|угу|спс|спасибо|пожалуйста|ладно|хорошо|понял|понятно|yes|no|yeah|yep|nope|thanks|thx|ty|k|kk|okey|okay)[\s!?.,]*$',  # Common garbage
    r'^[\s\d.,!?:\-]+$',  # Only numbers/punctuation
    r'^[)(:;]+$',  # Only emoticons
]
GARBAGE_PATTERNS_COMPILED = [re.compile(p, re.IGNORECASE) for p in GARBAGE_PATTERNS]

# Memory types
MEMORY_KINDS = ['fact', 'preference', 'person', 'project', 'plan', 'constraint', 'achievement', 'event']
RAW_DIALOG_KIND = "dialog_raw"  # Raw user message stored as vector memory
DIALOG_SUMMARY_KIND = "dialog_summary"  # Compressed summary of multiple messages

# Similarity threshold for deduplication
DEDUP_SIMILARITY_THRESHOLD = 0.92

# Retrieval configuration
MEMORY_TOP_K = 5
MEMORY_SIMILARITY_THRESHOLD = 0.40

# Summary compression configuration
SUMMARY_BATCH_SIZE = 12  # Number of messages to compress into one summary
SUMMARY_MIN_MESSAGES = 8  # Minimum messages required to trigger summary
SUMMARY_MAX_AGE_HOURS = 24  # Create summary if oldest unsummarized message is older than this


@dataclass
class ExtractedMemory:
    """An extracted memory-worthy fact from conversation"""
    content: str
    kind: str
    confidence: float
    original_text: str
    conversation_id: int


@dataclass
class RetrievedMemory:
    """A memory retrieved from vector search"""
    id: int
    content: str
    kind: str
    similarity: float
    created_at: datetime


class ConversationMemoryService:
    """Service for extracting and retrieving conversation memories"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.analysis_model = settings.openai_analysis_model
        self.embedding_service = EmbeddingService()

    @staticmethod
    def is_garbage_message(content: str) -> bool:
        """
        Check if message is garbage that should be skipped.
        Uses cheap heuristics before expensive LLM classification.
        """
        if not content:
            return True

        # Check length
        if len(content.strip()) < MIN_MESSAGE_LENGTH:
            return True

        # Check against garbage patterns
        content_stripped = content.strip()
        for pattern in GARBAGE_PATTERNS_COMPILED:
            if pattern.match(content_stripped):
                return True

        return False

    @staticmethod
    def compute_fingerprint(text: str) -> str:
        """
        Compute fingerprint for deduplication.
        Normalizes text (lowercase, remove punctuation/whitespace) then hashes.
        """
        if not text:
            return ""

        # Normalize: lowercase, remove punctuation and extra whitespace
        normalized = text.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        normalized = re.sub(r'\s+', ' ', normalized).strip()  # Normalize whitespace

        # Hash the normalized text
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:32]

    @staticmethod
    def _is_user_message(message_type: str) -> bool:
        return message_type in ("free_dialog", "user_response")

    async def classify_and_extract(
        self,
        content: str,
        conversation_id: int,
    ) -> List[ExtractedMemory]:
        """
        Use LLM to classify if message is memory-worthy and extract facts.

        Returns list of extracted memories (can be 0-3 facts per message).
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
                        "content": """You analyze user messages to extract memory-worthy facts.

TASK: Extract personal facts that the user explicitly stated. Do NOT infer or assume.

EXTRACT THESE TYPES:
- fact: Personal facts (name, job, hobby, location, etc.)
- person: People mentioned (family, friends, colleagues with names)
- preference: Preferences and likes/dislikes
- project: Projects or work the user is doing
- plan: Future plans or intentions
- achievement: Accomplishments or milestones
- event: Important events or experiences

RULES:
1. Only extract what the user EXPLICITLY said
2. Do NOT make assumptions or add information
3. Keep each fact short (1 sentence)
4. Write in canonical form: "User said: [fact]" or "User's [X] is [Y]"
5. Skip greetings, pleasantries, questions, and vague statements
6. If nothing memory-worthy, return empty array

Respond with JSON:
{
  "keep": true/false,
  "memories": [
    {"content": "...", "kind": "fact|person|preference|...", "confidence": 0.0-1.0}
  ]
}

If message is just greeting/pleasantry/question with no personal facts, return:
{"keep": false, "memories": []}"""
                    },
                    {"role": "user", "content": content}
                ],
                max_tokens=300,
                temperature=0,
                response_format={"type": "json_object"},
            )

            if response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)

            if not result.get("keep", False):
                return []

            memories = []
            for mem in result.get("memories", []):
                if mem.get("content") and mem.get("kind") in MEMORY_KINDS:
                    memories.append(ExtractedMemory(
                        content=mem["content"],
                        kind=mem["kind"],
                        confidence=mem.get("confidence", 0.8),
                        original_text=content[:200],  # Keep snippet for traceability
                        conversation_id=conversation_id,
                    ))

            logger.debug(f"Extracted {len(memories)} memories from message: {content[:50]}...")
            return memories

        except Exception as e:
            logger.error(f"Memory extraction failed: {e}")
            success = False
            error_msg = str(e)
            return []

        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            await APIUsageService.log_usage(
                api_provider="openai",
                model=self.analysis_model,
                operation_type="memory_extraction",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                success=success,
                error_message=error_msg,
            )

    async def check_duplicate(
        self,
        user_id: int,
        fingerprint: str,
        embedding: List[float],
    ) -> bool:
        """
        Check if memory already exists (by fingerprint or high similarity).
        Returns True if duplicate found.
        """
        async with get_session() as session:
            # Check fingerprint match
            result = await session.execute(
                select(ConversationMemory)
                .where(
                    and_(
                        ConversationMemory.user_id == user_id,
                        ConversationMemory.fingerprint == fingerprint,
                    )
                )
                .limit(1)
            )
            if result.scalar_one_or_none():
                return True

            # Check vector similarity
            if embedding:
                embedding_literal = "'" + "[" + ",".join(f"{x:.10g}" for x in embedding) + "]'::vector"
                result = await session.execute(
                    text(f"""
                        SELECT id, 1 - (embedding <=> {embedding_literal}) as similarity
                        FROM conversation_memories
                        WHERE user_id = :user_id
                        AND embedding IS NOT NULL
                        ORDER BY embedding <=> {embedding_literal}
                        LIMIT 1
                    """),
                    {"user_id": user_id}
                )
                row = result.fetchone()
                if row and float(row.similarity) > DEDUP_SIMILARITY_THRESHOLD:
                    logger.debug(f"Found duplicate by similarity: {row.similarity:.4f}")
                    return True

        return False

    async def store_memory(
        self,
        user_id: int,
        memory: ExtractedMemory,
        embedding: List[float],
    ) -> Optional[int]:
        """
        Store extracted memory in database.
        Returns memory ID if stored, None if skipped (duplicate).
        """
        fingerprint = self.compute_fingerprint(memory.content)

        # Check for duplicates
        if await self.check_duplicate(user_id, fingerprint, embedding):
            logger.debug(f"Skipping duplicate memory: {memory.content[:50]}...")
            return None

        async with get_session() as session:
            conv_memory = ConversationMemory(
                user_id=user_id,
                source_conversation_ids=[memory.conversation_id],
                content=memory.content,
                embedding=embedding,
                kind=memory.kind,
                importance=memory.confidence,
                fingerprint=fingerprint,
                memory_metadata={
                    "original_text": memory.original_text,
                    "confidence": memory.confidence,
                },
            )
            session.add(conv_memory)
            await session.commit()
            await session.refresh(conv_memory)

            logger.info(f"Stored memory #{conv_memory.id} for user {user_id}: {memory.content[:50]}...")
            return conv_memory.id

    async def store_raw_memory(
        self,
        user_id: int,
        conversation: Conversation,
        embedding: List[float],
    ) -> Optional[int]:
        """
        Store raw user message as vector memory for long-term dialog recall.
        """
        fingerprint = self.compute_fingerprint(conversation.content)

        if await self.check_duplicate(user_id, fingerprint, embedding):
            logger.debug(f"Skipping duplicate raw memory: {conversation.content[:50]}...")
            return None

        async with get_session() as session:
            conv_memory = ConversationMemory(
                user_id=user_id,
                source_conversation_ids=[conversation.id],
                content=conversation.content,
                embedding=embedding,
                kind=RAW_DIALOG_KIND,
                importance=0.5,
                fingerprint=fingerprint,
                memory_metadata={
                    "source": "dialog_raw",
                    "message_type": conversation.message_type,
                },
            )
            session.add(conv_memory)
            await session.commit()
            await session.refresh(conv_memory)

            logger.info(
                f"Stored raw dialog memory #{conv_memory.id} for user {user_id}: "
                f"{conversation.content[:50]}..."
            )
            return conv_memory.id

    async def process_conversation(
        self,
        user_id: int,
        conversation: Conversation,
    ) -> int:
        """
        Process a single conversation and extract memories.
        Returns number of memories stored.
        """
        # Skip non-user messages
        if not self._is_user_message(conversation.message_type):
            return 0

        stored_count = 0

        # Skip garbage
        if self.is_garbage_message(conversation.content):
            return 0

        # Store raw dialog memory (full user message) for long-term recall
        raw_embedding = await self.embedding_service.create_embedding(conversation.content)
        if raw_embedding:
            raw_id = await self.store_raw_memory(user_id, conversation, raw_embedding)
            if raw_id:
                stored_count += 1

        # Extract memories
        memories = await self.classify_and_extract(
            conversation.content,
            conversation.id,
        )

        if not memories:
            return 0

        # Store each memory
        for memory in memories:
            # Create embedding
            embedding = await self.embedding_service.create_embedding(memory.content)
            if not embedding:
                continue

            # Store
            memory_id = await self.store_memory(user_id, memory, embedding)
            if memory_id:
                stored_count += 1

        return stored_count

    async def index_user_conversations(
        self,
        telegram_id: int,
        full_reindex: bool = False,
    ) -> Tuple[int, int]:
        """
        Index new conversations for a user.

        Args:
            telegram_id: User's Telegram ID
            full_reindex: If True, reindex all conversations (ignore last_indexed marker)

        Returns:
            Tuple of (conversations_processed, memories_stored)
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                logger.warning(f"User not found: {telegram_id}")
                return (0, 0)

            # Get conversations to process
            query = (
                select(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user.id,
                        Conversation.message_type.in_(['free_dialog', 'user_response']),
                    )
                )
                .order_by(Conversation.id)
            )

            if not full_reindex:
                query = query.where(
                    Conversation.id > user.last_memory_indexed_conversation_id
                )

            result = await session.execute(query)
            conversations = result.scalars().all()

            if not conversations:
                logger.debug(f"No new conversations to index for user {telegram_id}")
                return (0, 0)

            logger.info(f"Indexing {len(conversations)} conversations for user {telegram_id}")

            # Process each conversation
            total_stored = 0
            max_conv_id = user.last_memory_indexed_conversation_id

            for conv in conversations:
                stored = await self.process_conversation(user.id, conv)
                total_stored += stored
                max_conv_id = max(max_conv_id, conv.id)

            # Update tracking marker
            if not full_reindex and max_conv_id > user.last_memory_indexed_conversation_id:
                await session.execute(
                    text("""
                        UPDATE users
                        SET last_memory_indexed_conversation_id = :max_id
                        WHERE id = :user_id
                    """),
                    {"max_id": max_conv_id, "user_id": user.id}
                )
                await session.commit()

            logger.info(
                f"Indexed {len(conversations)} conversations for user {telegram_id}, "
                f"stored {total_stored} memories"
            )
            return (len(conversations), total_stored)

    async def index_all_users(self, full_reindex: bool = False) -> Dict[str, int]:
        """
        Index conversations for all users.

        Returns:
            Dict with stats: users_processed, conversations_processed, memories_stored
        """
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.onboarding_completed == True)
            )
            users = result.scalars().all()

        total_users = 0
        total_convs = 0
        total_memories = 0

        for user in users:
            try:
                convs, memories = await self.index_user_conversations(
                    user.telegram_id,
                    full_reindex=full_reindex,
                )
                if convs > 0:
                    total_users += 1
                total_convs += convs
                total_memories += memories
            except Exception as e:
                logger.error(f"Failed to index user {user.telegram_id}: {e}")

        logger.info(
            f"Indexing complete: {total_users} users, "
            f"{total_convs} conversations, {total_memories} memories stored"
        )
        return {
            "users_processed": total_users,
            "conversations_processed": total_convs,
            "memories_stored": total_memories,
        }

    async def search_memories(
        self,
        telegram_id: int,
        query_embedding: List[float],
        limit: int = MEMORY_TOP_K,
        threshold: float = MEMORY_SIMILARITY_THRESHOLD,
        kinds: Optional[List[str]] = None,
    ) -> List[RetrievedMemory]:
        """
        Search user's memories with vector similarity.
        CRITICAL: Always filters by user_id for isolation.
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return []

            # Vector search with user isolation
            embedding_literal = "'" + "[" + ",".join(f"{x:.10g}" for x in query_embedding) + "]'::vector"
            fetch_limit = limit * 2  # Get extra to filter by threshold

            kind_filter = ""
            params = {"user_id": user.id, "limit": fetch_limit}
            if kinds:
                kind_filter = "AND kind = ANY(:kinds)"
                params["kinds"] = kinds

            result = await session.execute(
                text(f"""
                    SELECT
                        id,
                        content,
                        kind,
                        created_at,
                        1 - (embedding <=> {embedding_literal}) as similarity
                    FROM conversation_memories
                    WHERE user_id = :user_id
                    AND embedding IS NOT NULL
                    {kind_filter}
                    ORDER BY embedding <=> {embedding_literal}
                    LIMIT :limit
                """),
                params
            )
            rows = result.fetchall()

            # Filter by threshold
            memories = []
            for row in rows:
                similarity = float(row.similarity)
                if similarity < threshold:
                    continue

                memories.append(RetrievedMemory(
                    id=row.id,
                    content=row.content,
                    kind=row.kind,
                    similarity=similarity,
                    created_at=row.created_at,
                ))

            logger.debug(f"Retrieved {len(memories)} memories for user {telegram_id}")
            return memories[:limit]

    async def get_user_memory_count(self, telegram_id: int) -> int:
        """Get count of stored memories for a user."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return 0

            result = await session.execute(
                text("SELECT COUNT(*) FROM conversation_memories WHERE user_id = :user_id"),
                {"user_id": user.id}
            )
            return result.scalar() or 0

    async def delete_user_memories(self, telegram_id: int) -> int:
        """Delete all memories for a user (GDPR compliance)."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return 0

            result = await session.execute(
                text("DELETE FROM conversation_memories WHERE user_id = :user_id RETURNING id"),
                {"user_id": user.id}
            )
            deleted_ids = result.fetchall()
            await session.commit()

            logger.info(f"Deleted {len(deleted_ids)} memories for user {telegram_id}")
            return len(deleted_ids)

    async def get_unsummarized_raw_memories(
        self,
        user_id: int,
    ) -> Tuple[List[ConversationMemory], datetime]:
        """
        Get raw dialog memories that haven't been summarized yet.
        Returns tuple of (memories, oldest_memory_time).
        """
        async with get_session() as session:
            # Get raw dialog memories not yet included in any summary
            # Check by conversation ID (not memory ID) since summaries store conversation IDs
            result = await session.execute(
                text("""
                    SELECT cm.*
                    FROM conversation_memories cm
                    WHERE cm.user_id = :user_id
                    AND cm.kind = :raw_kind
                    AND NOT EXISTS (
                        SELECT 1 FROM conversation_memories s
                        WHERE s.user_id = :user_id
                        AND s.kind = :summary_kind
                        AND cm.source_conversation_ids && s.source_conversation_ids
                    )
                    ORDER BY cm.created_at ASC
                """),
                {
                    "user_id": user_id,
                    "raw_kind": RAW_DIALOG_KIND,
                    "summary_kind": DIALOG_SUMMARY_KIND,
                }
            )
            rows = result.fetchall()

            if not rows:
                return [], datetime.utcnow()

            # Map to ConversationMemory objects
            memories = []
            oldest_time = datetime.utcnow()

            for row in rows:
                mem = ConversationMemory(
                    id=row.id,
                    user_id=row.user_id,
                    content=row.content,
                    kind=row.kind,
                    created_at=row.created_at,
                    source_conversation_ids=row.source_conversation_ids,
                )
                memories.append(mem)
                if row.created_at < oldest_time:
                    oldest_time = row.created_at

            return memories, oldest_time

    async def should_create_summary(
        self,
        user_id: int,
    ) -> Tuple[bool, List[ConversationMemory]]:
        """
        Check if we should create a summary for this user.
        Returns (should_create, memories_to_summarize).

        Triggers:
        1. At least SUMMARY_MIN_MESSAGES raw memories exist
        2. Either have SUMMARY_BATCH_SIZE messages OR oldest is > SUMMARY_MAX_AGE_HOURS old
        """
        memories, oldest_time = await self.get_unsummarized_raw_memories(user_id)

        if len(memories) < SUMMARY_MIN_MESSAGES:
            return False, []

        # Check if we have enough messages
        if len(memories) >= SUMMARY_BATCH_SIZE:
            # Take the first SUMMARY_BATCH_SIZE messages
            return True, memories[:SUMMARY_BATCH_SIZE]

        # Check if oldest message is old enough
        age_hours = (datetime.utcnow() - oldest_time).total_seconds() / 3600
        if age_hours >= SUMMARY_MAX_AGE_HOURS:
            return True, memories

        return False, []

    async def generate_summary_text(
        self,
        memories: List[ConversationMemory],
    ) -> Optional[str]:
        """
        Use LLM to generate a compressed summary of multiple user messages.
        """
        if not memories:
            return None

        start_time = time.time()
        success = True
        error_msg = None
        input_tokens = 0
        output_tokens = 0

        try:
            # Build message content from memories
            messages_text = "\n".join([
                f"- {m.content}" for m in memories
            ])

            response = await self.client.chat.completions.create(
                model=self.analysis_model,
                messages=[
                    {
                        "role": "system",
                        "content": """You compress multiple user messages into a concise summary.

TASK: Create a summary that captures:
1. Key facts mentioned by the user
2. Topics they discussed
3. Any preferences, plans, or achievements mentioned
4. People or projects mentioned
5. Emotional themes (positive moments, concerns, etc.)

RULES:
1. Keep the summary concise (3-5 sentences)
2. Write in third person: "The user mentioned...", "They talked about..."
3. Preserve important details and names
4. Don't add interpretations or assumptions
5. Focus on information useful for future conversation context

OUTPUT: A single paragraph summarizing the user's messages."""
                    },
                    {
                        "role": "user",
                        "content": f"Summarize these user messages:\n\n{messages_text}"
                    }
                ],
                max_tokens=300,
                temperature=0,
            )

            if response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary from {len(memories)} messages: {summary[:100]}...")
            return summary

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            success = False
            error_msg = str(e)
            return None

        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            await APIUsageService.log_usage(
                api_provider="openai",
                model=self.analysis_model,
                operation_type="dialog_summary_generation",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                success=success,
                error_message=error_msg,
            )

    async def store_summary(
        self,
        user_id: int,
        summary_text: str,
        source_conversation_ids: List[int],
        embedding: List[float],
    ) -> Optional[int]:
        """
        Store a dialog summary in the database.
        
        Args:
            source_conversation_ids: List of conversation IDs (not memory IDs) that were summarized
        """
        fingerprint = self.compute_fingerprint(summary_text)

        async with get_session() as session:
            conv_memory = ConversationMemory(
                user_id=user_id,
                source_conversation_ids=source_conversation_ids,
                content=summary_text,
                embedding=embedding,
                kind=DIALOG_SUMMARY_KIND,
                importance=1.5,  # Higher importance than raw messages
                fingerprint=fingerprint,
                memory_metadata={
                    "source": "dialog_summary",
                    "summarized_conversations_count": len(source_conversation_ids),
                },
            )
            session.add(conv_memory)
            await session.commit()
            await session.refresh(conv_memory)

            logger.info(
                f"Stored dialog summary #{conv_memory.id} for user {user_id}, "
                f"summarized {len(source_conversation_ids)} conversations"
            )
            return conv_memory.id

    async def create_user_summary(
        self,
        telegram_id: int,
    ) -> Optional[int]:
        """
        Create a dialog summary for a user if conditions are met.
        Returns the summary ID if created, None otherwise.
        """
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return None

        # Check if we should create a summary
        should_create, memories = await self.should_create_summary(user.id)
        if not should_create:
            logger.debug(f"No summary needed for user {telegram_id}")
            return None

        # Generate summary text
        summary_text = await self.generate_summary_text(memories)
        if not summary_text:
            return None

        # Create embedding for summary
        embedding = await self.embedding_service.create_embedding(summary_text)
        if not embedding:
            logger.error(f"Failed to create embedding for summary")
            return None

        # Store summary
        # Collect conversation IDs from source memories (not memory IDs)
        # Each raw memory has source_conversation_ids=[conversation.id]
        conversation_ids = []
        for mem in memories:
            if mem.source_conversation_ids:
                conversation_ids.extend(mem.source_conversation_ids)
        # Deduplicate
        conversation_ids = list(set(conversation_ids))
        summary_id = await self.store_summary(user.id, summary_text, conversation_ids, embedding)

        return summary_id

    async def create_summaries_for_all_users(self) -> Dict[str, int]:
        """
        Create dialog summaries for all users who need them.
        Returns dict with stats: users_processed, summaries_created.
        """
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.onboarding_completed == True)
            )
            users = result.scalars().all()

        total_users = 0
        total_summaries = 0

        for user in users:
            try:
                summary_id = await self.create_user_summary(user.telegram_id)
                if summary_id:
                    total_summaries += 1
                    total_users += 1
            except Exception as e:
                logger.error(f"Failed to create summary for user {user.telegram_id}: {e}")

        logger.info(
            f"Summary creation complete: {total_users} users, "
            f"{total_summaries} summaries created"
        )
        return {
            "users_processed": total_users,
            "summaries_created": total_summaries,
        }

    async def get_user_summary_count(self, telegram_id: int) -> int:
        """Get count of stored summaries for a user."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return 0

            result = await session.execute(
                text("""
                    SELECT COUNT(*) FROM conversation_memories
                    WHERE user_id = :user_id AND kind = :summary_kind
                """),
                {"user_id": user.id, "summary_kind": DIALOG_SUMMARY_KIND}
            )
            return result.scalar() or 0
