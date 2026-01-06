"""
MINDSETHAPPYBOT - Dialog service
Manages free dialog conversations and context
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy import select, and_

from src.db.database import get_session
from src.db.models import User, Conversation
from src.services.personalization_service import PersonalizationService

logger = logging.getLogger(__name__)


class DialogService:
    """Service for managing free dialog sessions"""

    def __init__(self):
        self.personalization_service = PersonalizationService()
        # In-memory state for active dialog sessions
        self._active_dialogs: dict[int, bool] = {}  # telegram_id -> is_active

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
        Process a message in free dialog mode

        Args:
            telegram_id: User's Telegram ID
            message: User's message

        Returns:
            Bot's response
        """
        # Save user message
        await self._save_conversation(
            telegram_id=telegram_id,
            message_type="free_dialog",
            content=message,
        )

        # Get recent context
        context = await self._get_dialog_context(telegram_id)

        # Generate response
        response = await self.personalization_service.generate_dialog_response(
            telegram_id=telegram_id,
            message=message,
            context=context,
        )

        # Save bot response
        await self._save_conversation(
            telegram_id=telegram_id,
            message_type="bot_reply",
            content=response,
        )

        return response

    async def _save_conversation(
        self,
        telegram_id: int,
        message_type: str,
        content: str,
        metadata: dict = None,
    ) -> None:
        """Save a conversation message to database"""
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
                metadata=metadata,
            )
            session.add(conversation)
            await session.commit()

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

            # Get recent conversations (last hour)
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)

            result = await session.execute(
                select(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user.id,
                        Conversation.created_at >= one_hour_ago,
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
