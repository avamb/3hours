"""
MINDSETHAPPYBOT - Dialog service
Manages free dialog conversations and context
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, and_

from src.db.database import get_session
from src.db.models import User, Conversation
from src.services.personalization_service import PersonalizationService
from src.services.semantic_antirepeat_service import get_semantic_antirepeat_service
from src.services.immediate_indexer import trigger_immediate_indexing, should_index_immediately

logger = logging.getLogger(__name__)

# Maximum retry attempts for semantic anti-repeat
MAX_SEMANTIC_RETRY_ATTEMPTS = 2


class DialogService:
    """Service for managing free dialog sessions"""

    _instance: "DialogService | None" = None

    def __init__(self):
        self.personalization_service = PersonalizationService()
        self.semantic_antirepeat = get_semantic_antirepeat_service()
        # In-memory state for active dialog sessions
        self._active_dialogs: dict[int, bool] = {}  # telegram_id -> is_active

    @classmethod
    def get_instance(cls) -> "DialogService":
        """Get singleton instance to preserve in-memory dialog state within process."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def is_in_dialog(self, telegram_id: int) -> bool:
        """Check if user is in free dialog mode"""
        return self._active_dialogs.get(telegram_id, False)

    def start_dialog(self, telegram_id: int) -> None:
        """Start free dialog mode for user"""
        self._active_dialogs[telegram_id] = True
        logger.info(f"Started dialog for user {telegram_id}")

    def end_dialog(self, telegram_id: int) -> None:
        """End free dialog mode for user"""
        self._active_dialogs[telegram_id] = False
        logger.info(f"Ended dialog for user {telegram_id}")

    async def process_dialog_message(
        self,
        telegram_id: int,
        message: str,
    ) -> str:
        """
        Process a message in free dialog mode with Hybrid RAG.

        Uses Knowledge Base + User Memory + Semantic Anti-Repeat for better responses.

        Args:
            telegram_id: User's Telegram ID
            message: User's message

        Returns:
            Bot's response
        """
        logger.info(f"Processing dialog message from user {telegram_id}: {message[:100]}")
        # Save user message
        await self._save_conversation(
            telegram_id=telegram_id,
            message_type="free_dialog",
            content=message,
        )

        # Get recent context
        context = await self._get_dialog_context(telegram_id)

        # Generate response with Hybrid RAG
        response, rag_metadata = await self.personalization_service.generate_dialog_response_with_rag(
            telegram_id=telegram_id,
            message=message,
            context=context,
        )

        # Apply semantic anti-repeat check with retries
        retry_count = 0
        while retry_count < MAX_SEMANTIC_RETRY_ATTEMPTS:
            is_repetitive = await self.semantic_antirepeat.is_repetitive(
                telegram_id=telegram_id,
                new_response=response,
            )

            if not is_repetitive:
                break

            retry_count += 1
            logger.warning(f"Repetitive response detected (attempt {retry_count}/{MAX_SEMANTIC_RETRY_ATTEMPTS})")

            if retry_count < MAX_SEMANTIC_RETRY_ATTEMPTS:
                # Regenerate response
                response, rag_metadata = await self.personalization_service.generate_dialog_response_with_rag(
                    telegram_id=telegram_id,
                    message=message,
                    context=context,
                )

        # Save bot response with RAG metadata
        await self._save_conversation(
            telegram_id=telegram_id,
            message_type="bot_reply",
            content=response,
            metadata=rag_metadata,
        )

        # Detailed RAG logging
        rag_mode = rag_metadata.get('rag_mode', '?')
        kb_count = rag_metadata.get('kb_chunks_count', 0)
        moments_count = rag_metadata.get('moments_count', 0)
        mem_count = len(rag_metadata.get('dialog_memory_ids', []))
        summary_count = len(rag_metadata.get('dialog_summary_ids', []))
        snippet_count = len(rag_metadata.get('dialog_snippet_ids', []))
        
        # Log summary
        logger.info(f"Dialog response with RAG: user={telegram_id}, mode={rag_mode}, "
                   f"kb_chunks={kb_count}, moments={moments_count}, "
                   f"memories={mem_count}, summaries={summary_count}, snippets={snippet_count}, "
                   f"semantic_retries={retry_count}")
        
        # Log details if RAG was used
        if rag_metadata.get('retrieval_used'):
            moment_ids = rag_metadata.get('moment_ids', [])
            kb_ids = rag_metadata.get('kb_chunk_ids', [])
            if moment_ids:
                moment_scores = rag_metadata.get('moment_scores', [])
                logger.debug(f"RAG moments used: ids={moment_ids[:5]}, scores={moment_scores[:5]}")
            if kb_ids:
                kb_scores = rag_metadata.get('kb_scores', [])
                logger.debug(f"RAG KB chunks used: ids={kb_ids[:5]}, scores={kb_scores[:5]}")
        else:
            logger.debug(f"RAG: No retrieval used for user {telegram_id} (mode={rag_mode})")

        return response

    async def _save_conversation(
        self,
        telegram_id: int,
        message_type: str,
        content: str,
        metadata: dict = None,
    ) -> None:
        """Save a conversation message to database with immediate indexing for user messages"""
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.error(f"User not found: {telegram_id}")
                return

            conversation = Conversation(
                user_id=user.id,
                message_type=message_type,
                content=content,
                message_metadata=metadata,
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)  # Get the ID

            # Trigger immediate indexing for user messages (fire-and-forget)
            if await should_index_immediately(message_type, content):
                await trigger_immediate_indexing(user.id, conversation)

    async def _get_dialog_context(
        self,
        telegram_id: int,
        limit: int = 10,
    ) -> List[dict]:
        """
        Get recent dialog context for GPT

        Returns list of messages in OpenAI format
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return []

            # Get recent conversations (last 24 hours for better context)
            # Extended from 1 hour to 24 hours to avoid empty context after restarts
            one_day_ago = datetime.now(timezone.utc) - timedelta(hours=24)

            result = await session.execute(
                select(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user.id,
                        Conversation.created_at >= one_day_ago,
                        Conversation.message_type.in_(["free_dialog", "bot_reply"]),
                    )
                )
                .order_by(Conversation.created_at.desc())
                .limit(limit)
            )
            conversations = result.scalars().all()

            # Convert to OpenAI format (reverse to chronological order)
            context = []
            for conv in reversed(conversations):
                role = "user" if conv.message_type == "free_dialog" else "assistant"
                context.append({
                    "role": role,
                    "content": conv.content,
                })

            return context
