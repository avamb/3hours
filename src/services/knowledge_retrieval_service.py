"""
MINDSETHAPPYBOT - Knowledge Retrieval Service
Hybrid RAG implementation with 4 sources:
1. Dialog Memory (conversation_memories) - extracted facts from conversations
2. User Memory (moments) - personal history
3. Knowledge Base (knowledge_chunks) - uploaded documents
4. Model parametric knowledge - always available fallback

Features:
- Query type classification (A/B/C/R routing)
- Vector similarity search with thresholds
- Recency boosting for moments
- Usage count tracking for KB
- Anti-repetition fingerprinting
- Anti-hallucination for "remember" queries (type R)
"""
import logging
import hashlib
import re
import time
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from openai import AsyncOpenAI
from sqlalchemy import text, select, and_

from src.config import get_settings
from src.db.database import get_session
from src.db.models import User, Conversation
from src.services.embedding_service import EmbeddingService
from src.services.api_usage_service import APIUsageService
from src.services.conversation_memory_service import (
    ConversationMemoryService,
    RetrievedMemory,
    RAW_DIALOG_KIND,
    DIALOG_SUMMARY_KIND,
    MEMORY_KINDS,
)

logger = logging.getLogger(__name__)


# Configuration constants
MOMENTS_TOP_K = 4
KB_TOP_K = 5
DIALOG_MEMORY_TOP_K = 5  # Extracted facts from dialog
DIALOG_SNIPPETS_TOP_K = 6  # Raw user messages for long-term recall
DIALOG_SUMMARIES_TOP_K = 3  # Compressed summaries of dialog history
SIMILARITY_THRESHOLD = 0.40  # Below this, don't include source (lowered for Russian text)
MAX_CONTEXT_CHARS = 4500  # ~1200-1500 tokens
RECENCY_BOOST_DAYS = 7  # Moments within this period get boosted
RECENCY_BOOST_FACTOR = 0.05  # How much to boost recent moments
FINGERPRINT_HISTORY_LIMIT = 50  # How many past bot replies to check for repetition

# Patterns to detect "remember" queries (anti-hallucination required)
REMEMBER_PATTERNS = [
    r'\bпомн[иь]шь\b',  # помнишь (Russian - remember?)
    r'\bя\s+говорил[аи]?\b',  # я говорил/а (Russian - I told you)
    r'\bя\s+рассказывал[аи]?\b',  # я рассказывал/а (Russian - I told you about)
    r'\bты\s+знаешь\b',  # ты знаешь (Russian - you know)
    r'\bмы\s+обсуждали\b',  # мы обсуждали (Russian - we discussed)
    r'\bчто\s+мы\s+обсуждали\b',  # что мы обсуждали (Russian - what we discussed)
    r'\bнапомни\s+.*разговор\b',  # напомни...разговор (Russian - remind me...conversation)
    r'\bтемы\s+.*разговор\b',  # темы...разговор (Russian - topics...conversation)
    r'\bосновные\s+темы\b',  # основные темы (Russian - main topics)
    r'\bremember\b',  # English - remember
    r'\bi\s+told\s+you\b',  # English - I told you
    r'\bi\s+mentioned\b',  # English - I mentioned
    r'\bwe\s+discussed\b',  # English - we discussed
    r'\bwhat\s+did\s+we\s+discuss\b',  # English - what did we discuss
    r'\bwhat\s+we\s+discussed\b',  # English - what we discussed
    r'\bremind\s+.*conversation\b',  # English - remind...conversation
    r'\bremind\s+.*topics\b',  # English - remind...topics
    r'\bmain\s+topics\b',  # English - main topics
    r'\btopics\s+.*talk\b',  # English - topics...talk
    r'\byou\s+know\b',  # English - you know
    r'\bчто\s+я\s+.*сказал[аи]?\b',  # что я сказал/а (Russian - what I said)
]
REMEMBER_PATTERNS_COMPILED = [re.compile(p, re.IGNORECASE) for p in REMEMBER_PATTERNS]


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
    query_type: str  # 'A', 'B', 'C', 'R'
    moments: List[RetrievedMoment]
    kb_chunks: List[RetrievedChunk]
    dialog_snippets: List[RetrievedMemory]
    moment_ids: List[int]
    moment_scores: List[float]
    kb_chunk_ids: List[int]
    kb_item_ids: List[int]
    kb_scores: List[float]
    recent_fingerprints: List[str]
    recent_responses: List[str]  # Short excerpts for anti-repetition
    # Fields for dialog memory
    dialog_memories: List[RetrievedMemory] = field(default_factory=list)
    dialog_memory_ids: List[int] = field(default_factory=list)
    dialog_memory_scores: List[float] = field(default_factory=list)
    dialog_snippet_ids: List[int] = field(default_factory=list)
    dialog_snippet_scores: List[float] = field(default_factory=list)
    # New fields for dialog summaries (compressed memory)
    dialog_summaries: List[RetrievedMemory] = field(default_factory=list)
    dialog_summary_ids: List[int] = field(default_factory=list)
    dialog_summary_scores: List[float] = field(default_factory=list)
    is_remember_query: bool = False  # Anti-hallucination flag


class KnowledgeRetrievalService:
    """Service for hybrid RAG retrieval"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.embedding_service = EmbeddingService()
        self.analysis_model = settings.openai_analysis_model
        self.memory_service = ConversationMemoryService()

    @staticmethod
    def is_remember_query(query: str) -> bool:
        """
        Check if query is asking about something the user previously told the bot.
        These queries require anti-hallucination behavior.
        """
        for pattern in REMEMBER_PATTERNS_COMPILED:
            if pattern.search(query):
                return True
        return False

    async def classify_query_type(self, query: str) -> str:
        """
        Classify query into types:
        - Type A: About user / emotions / progress - moments required, KB optional
        - Type B: How to support / formulate / practices - KB required, moments optional
        - Type C: General questions - KB if available, otherwise model-only
        - Type R: Remember queries - dialog memory + moments only, anti-hallucination
        """
        # Check for remember query first (cheap heuristic)
        if self.is_remember_query(query):
            logger.debug(f"Query classified as type R (remember): {query[:50]}...")
            return 'R'

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

    async def search_dialog_memories(
        self,
        telegram_id: int,
        query_embedding: List[float],
        limit: int = DIALOG_MEMORY_TOP_K,
    ) -> List[RetrievedMemory]:
        """
        Search user's extracted dialog memories (facts, people, preferences) with vector similarity.
        Uses ConversationMemoryService for user-isolated retrieval.
        """
        return await self.memory_service.search_memories(
            telegram_id=telegram_id,
            query_embedding=query_embedding,
            limit=limit,
            kinds=MEMORY_KINDS,
        )

    async def search_dialog_snippets(
        self,
        telegram_id: int,
        query_embedding: List[float],
        limit: int = DIALOG_SNIPPETS_TOP_K,
    ) -> List[RetrievedMemory]:
        """
        Search user's raw dialog messages with vector similarity.
        These are full user messages stored for long-term recall.
        """
        return await self.memory_service.search_memories(
            telegram_id=telegram_id,
            query_embedding=query_embedding,
            limit=limit,
            kinds=[RAW_DIALOG_KIND],
        )

    async def search_dialog_summaries(
        self,
        telegram_id: int,
        query_embedding: List[float],
        limit: int = DIALOG_SUMMARIES_TOP_K,
    ) -> List[RetrievedMemory]:
        """
        Search user's dialog summaries with vector similarity.
        Summaries are compressed representations of multiple messages and
        should be prioritized over raw snippets for context efficiency.
        """
        return await self.memory_service.search_memories(
            telegram_id=telegram_id,
            query_embedding=query_embedding,
            limit=limit,
            kinds=[DIALOG_SUMMARY_KIND],
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
            now = datetime.now(timezone.utc)
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
        - Classified query type (A/B/C/R)
        - Retrieved dialog memories (extracted facts from conversations)
        - Retrieved moments (user memory)
        - Retrieved KB chunks (knowledge base)
        - IDs and scores for logging
        - Recent fingerprints for anti-repetition
        - Anti-hallucination flag for remember queries
        """
        # Step 1: Classify query type
        query_type = await self.classify_query_type(query)
        is_remember = query_type == 'R'
        logger.info(f"RAG query classification for user {telegram_id}: type={query_type}, query='{query[:100]}'")

        # Step 2: Create query embedding
        query_embedding = await self.embedding_service.create_embedding(query)
        if query_embedding is None:
            logger.warning("Failed to create query embedding")
            return RAGContext(
                query_type=query_type,
                moments=[],
                kb_chunks=[],
                dialog_snippets=[],
                moment_ids=[],
                moment_scores=[],
                kb_chunk_ids=[],
                kb_item_ids=[],
                kb_scores=[],
                recent_fingerprints=[],
                recent_responses=[],
                dialog_memories=[],
                dialog_memory_ids=[],
                dialog_memory_scores=[],
                dialog_snippet_ids=[],
                dialog_snippet_scores=[],
                dialog_summaries=[],
                dialog_summary_ids=[],
                dialog_summary_scores=[],
                is_remember_query=is_remember,
            )

        # Step 3: Search based on query type
        # Always search for summaries first - they're higher quality and more efficient
        moments = []
        kb_chunks = []
        dialog_memories = []
        dialog_snippets = []
        dialog_summaries = []

        if query_type == 'R':
            # Remember query - dialog memory + summaries + snippets + moments, NO KB (anti-hallucination)
            dialog_memories = await self.search_dialog_memories(telegram_id, query_embedding)
            dialog_summaries = await self.search_dialog_summaries(telegram_id, query_embedding)
            dialog_snippets = await self.search_dialog_snippets(telegram_id, query_embedding)
            moments = await self.search_moments(telegram_id, query_embedding)
            # DO NOT search KB for remember queries - prevents hallucination
            logger.info(f"RAG search (R-remember) for user {telegram_id}: "
                       f"memories={len(dialog_memories)}, summaries={len(dialog_summaries)}, "
                       f"snippets={len(dialog_snippets)}, moments={len(moments)}")
        elif query_type == 'A':
            # Personal/emotional - dialog memory + summaries + moments required, KB optional
            dialog_memories = await self.search_dialog_memories(telegram_id, query_embedding, limit=3)
            dialog_summaries = await self.search_dialog_summaries(telegram_id, query_embedding, limit=2)
            # Reduce raw snippets if summaries are available (compression saves tokens)
            snippet_limit = 2 if dialog_summaries else 4
            dialog_snippets = await self.search_dialog_snippets(telegram_id, query_embedding, limit=snippet_limit)
            moments = await self.search_moments(telegram_id, query_embedding)
            kb_chunks = await self.search_knowledge_base(query_embedding, limit=3)
            logger.info(f"RAG search (A-personal) for user {telegram_id}: "
                       f"memories={len(dialog_memories)}, summaries={len(dialog_summaries)}, "
                       f"snippets={len(dialog_snippets)}, moments={len(moments)}, kb_chunks={len(kb_chunks)}")
        elif query_type == 'B':
            # Seeking advice - KB required, dialog memory + summaries + moments optional
            kb_chunks = await self.search_knowledge_base(query_embedding)
            dialog_memories = await self.search_dialog_memories(telegram_id, query_embedding, limit=2)
            dialog_summaries = await self.search_dialog_summaries(telegram_id, query_embedding, limit=2)
            dialog_snippets = await self.search_dialog_snippets(telegram_id, query_embedding, limit=2)
            moments = await self.search_moments(telegram_id, query_embedding, limit=2)
            logger.info(f"RAG search (B-advice) for user {telegram_id}: "
                       f"kb_chunks={len(kb_chunks)}, memories={len(dialog_memories)}, "
                       f"summaries={len(dialog_summaries)}, snippets={len(dialog_snippets)}, moments={len(moments)}")
        else:
            # General - try all, prefer KB
            kb_chunks = await self.search_knowledge_base(query_embedding, limit=4)
            dialog_memories = await self.search_dialog_memories(telegram_id, query_embedding, limit=2)
            dialog_summaries = await self.search_dialog_summaries(telegram_id, query_embedding, limit=2)
            dialog_snippets = await self.search_dialog_snippets(telegram_id, query_embedding, limit=2)
            moments = await self.search_moments(telegram_id, query_embedding, limit=2)
            logger.info(f"RAG search (C-general) for user {telegram_id}: "
                       f"kb_chunks={len(kb_chunks)}, memories={len(dialog_memories)}, "
                       f"summaries={len(dialog_summaries)}, snippets={len(dialog_snippets)}, moments={len(moments)}")

        # Log summary usage
        if dialog_summaries:
            logger.info(f"Using {len(dialog_summaries)} dialog summaries for user {telegram_id}")

        # Step 4: Get anti-repetition data
        fingerprints, excerpts = await self.get_recent_fingerprints(telegram_id)

        # Step 5: Truncate context if too long
        total_chars = (
            sum(len(m.content) for m in moments) +
            sum(len(c.content) for c in kb_chunks) +
            sum(len(d.content) for d in dialog_memories) +
            sum(len(s.content) for s in dialog_snippets) +
            sum(len(s.content) for s in dialog_summaries)
        )
        if total_chars > MAX_CONTEXT_CHARS:
            # Prioritize based on query type
            if query_type in ('A', 'R'):
                # Keep dialog memories, summaries, and moments; truncate KB and raw snippets
                kb_chars = sum(len(c.content) for c in kb_chunks)
                while kb_chars > MAX_CONTEXT_CHARS // 5 and kb_chunks:
                    kb_chunks.pop()
                    kb_chars = sum(len(c.content) for c in kb_chunks)
                # If summaries exist, reduce raw snippets (redundant)
                if dialog_summaries:
                    while len(dialog_snippets) > 2 and dialog_snippets:
                        dialog_snippets.pop()
            elif query_type == 'B':
                # Keep KB, truncate dialog memories, summaries, and moments
                mem_chars = (
                    sum(len(m.content) for m in moments) +
                    sum(len(d.content) for d in dialog_memories) +
                    sum(len(s.content) for s in dialog_snippets) +
                    sum(len(s.content) for s in dialog_summaries)
                )
                while mem_chars > MAX_CONTEXT_CHARS // 4 and (moments or dialog_memories or dialog_snippets):
                    if dialog_snippets:
                        dialog_snippets.pop()
                    elif moments:
                        moments.pop()
                    elif dialog_memories:
                        dialog_memories.pop()
                    mem_chars = (
                        sum(len(m.content) for m in moments) +
                        sum(len(d.content) for d in dialog_memories) +
                        sum(len(s.content) for s in dialog_snippets) +
                        sum(len(s.content) for s in dialog_summaries)
                    )
            else:
                # General query (type C) - balance all sources, prefer KB
                kb_chars = sum(len(c.content) for c in kb_chunks)
                while kb_chars > MAX_CONTEXT_CHARS // 3 and kb_chunks:
                    kb_chunks.pop()
                    kb_chars = sum(len(c.content) for c in kb_chunks)

                mem_chars = (
                    sum(len(m.content) for m in moments) +
                    sum(len(d.content) for d in dialog_memories) +
                    sum(len(s.content) for s in dialog_snippets) +
                    sum(len(s.content) for s in dialog_summaries)
                )
                while mem_chars > MAX_CONTEXT_CHARS // 3 and (moments or dialog_memories or dialog_snippets or dialog_summaries):
                    if dialog_snippets:
                        dialog_snippets.pop()
                    elif moments:
                        moments.pop()
                    elif dialog_summaries:
                        dialog_summaries.pop()
                    elif dialog_memories:
                        dialog_memories.pop()
                    mem_chars = (
                        sum(len(m.content) for m in moments) +
                        sum(len(d.content) for d in dialog_memories) +
                        sum(len(s.content) for s in dialog_snippets) +
                        sum(len(s.content) for s in dialog_summaries)
                    )

        return RAGContext(
            query_type=query_type,
            moments=moments,
            kb_chunks=kb_chunks,
            dialog_snippets=dialog_snippets,
            moment_ids=[m.id for m in moments],
            moment_scores=[m.boosted_score for m in moments],
            kb_chunk_ids=[c.id for c in kb_chunks],
            kb_item_ids=list(set(c.knowledge_base_id for c in kb_chunks)),
            kb_scores=[c.similarity for c in kb_chunks],
            recent_fingerprints=fingerprints,
            recent_responses=excerpts,
            dialog_memories=dialog_memories,
            dialog_memory_ids=[d.id for d in dialog_memories],
            dialog_memory_scores=[d.similarity for d in dialog_memories],
            dialog_snippet_ids=[s.id for s in dialog_snippets],
            dialog_snippet_scores=[s.similarity for s in dialog_snippets],
            dialog_summaries=dialog_summaries,
            dialog_summary_ids=[s.id for s in dialog_summaries],
            dialog_summary_scores=[s.similarity for s in dialog_summaries],
            is_remember_query=is_remember,
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
        Summaries are prioritized over raw snippets for better context efficiency.
        """
        parts = []

        # Dialog memory section (highest priority - what user told us)
        if context.dialog_memories:
            parts.append("=== FACTS USER TOLD YOU (from previous conversations) ===")
            for i, d in enumerate(context.dialog_memories, 1):
                # Truncate very long facts
                content = d.content[:300] + "..." if len(d.content) > 300 else d.content
                parts.append(f"{i}. {content}")
            parts.append("")

        # Dialog summaries section (compressed conversation history - HIGH priority)
        if context.dialog_summaries:
            parts.append("=== CONVERSATION SUMMARIES (compressed dialog history) ===")
            for i, s in enumerate(context.dialog_summaries, 1):
                content = s.content[:500] + "..." if len(s.content) > 500 else s.content
                parts.append(f"{i}. {content}")
            parts.append("")

        # Raw dialog snippets (only if no summaries or few summaries available)
        if context.dialog_snippets:
            parts.append("=== RELEVANT USER MESSAGES (semantic recall) ===")
            for i, s in enumerate(context.dialog_snippets, 1):
                content = s.content[:300] + "..." if len(s.content) > 300 else s.content
                parts.append(f"{i}. {content}")
            parts.append("")

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

    def build_anti_hallucination_instruction(self, context: RAGContext) -> str:
        """
        Build instruction to prevent hallucination on "remember" queries.
        Only used when is_remember_query is True.
        """
        if not context.is_remember_query:
            return ""

        has_memories = bool(
            context.dialog_memories or context.dialog_summaries or
            context.dialog_snippets or context.moments
        )

        if has_memories:
            return """
=== ANTI-HALLUCINATION RULE ===
The user is asking about something they told you before.
ONLY use facts from "FACTS USER TOLD YOU", "CONVERSATION SUMMARIES", "RELEVANT USER MESSAGES", and "USER'S PERSONAL HISTORY" sections above.
If the information is not in those sections, say: "I don't see that in our conversation history. Could you tell me about it again?" (EN) or "Я не вижу этого в нашей истории разговоров. Можешь рассказать об этом снова?" (RU)
NEVER say "I can't recall" or "I don't remember" - always reference checking the history.
DO NOT invent or assume facts the user didn't tell you.
"""
        else:
            return """
=== ANTI-HALLUCINATION RULE ===
The user is asking about something they told you before.
You have NO stored information about what the user mentioned.
Say: "I don't see that in our conversation history. Could you tell me about it again?" (EN)
or "Я не вижу этого в нашей истории разговоров. Можешь рассказать об этом снова?" (RU)
DO NOT say "I can't recall" or "I don't remember" - always reference checking the history.
DO NOT invent or assume facts the user didn't tell you.
"""

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
            "dialog_memory_ids": context.dialog_memory_ids,
            "dialog_memory_scores": [round(s, 4) for s in context.dialog_memory_scores],
            "dialog_snippet_ids": context.dialog_snippet_ids,
            "dialog_snippet_scores": [round(s, 4) for s in context.dialog_snippet_scores],
            "dialog_summary_ids": context.dialog_summary_ids,
            "dialog_summary_scores": [round(s, 4) for s in context.dialog_summary_scores],
            "answer_fingerprint": self.compute_fingerprint(response_text),
            "retrieval_used": bool(
                context.moments or context.kb_chunks or context.dialog_memories or
                context.dialog_snippets or context.dialog_summaries
            ),
            "moments_count": len(context.moments),
            "kb_chunks_count": len(context.kb_chunks),
            "dialog_memories_count": len(context.dialog_memories),
            "dialog_snippets_count": len(context.dialog_snippets),
            "dialog_summaries_count": len(context.dialog_summaries),
            "is_remember_query": context.is_remember_query,
        }
