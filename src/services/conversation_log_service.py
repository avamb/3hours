"""
MINDSETHAPPYBOT - Conversation logging service
Writes messages to the conversations table for admin visibility and context.
Integrates immediate memory indexing for user messages.
"""

import logging
from typing import Optional, Dict, Any, Tuple

from sqlalchemy import select

from src.db.database import get_session
from src.db.models import User, Conversation
from src.services.immediate_indexer import trigger_immediate_indexing, should_index_immediately

logger = logging.getLogger(__name__)


class ConversationLogService:
    """Persist conversation rows (best-effort; never throws to caller)."""

    async def log(
        self,
        telegram_id: int,
        message_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Tuple[int, Conversation]]:
        """
        Log a conversation message.

        Returns:
            Optional tuple of (user_id, Conversation) if successful, None otherwise.
        """
        try:
            async with get_session() as session:
                result = await session.execute(select(User).where(User.telegram_id == telegram_id))
                user = result.scalar_one_or_none()
                if not user:
                    return None

                row = Conversation(
                    user_id=user.id,
                    message_type=message_type,
                    content=content,
                    message_metadata=metadata,
                )
                session.add(row)
                await session.commit()
                await session.refresh(row)  # Get the ID and other fields

                # Trigger immediate indexing for user messages (fire-and-forget)
                if await should_index_immediately(message_type, content):
                    await trigger_immediate_indexing(user.id, row)

                return (user.id, row)
        except Exception as e:
            logger.warning(f"Failed to log conversation (tg={telegram_id}, type={message_type}): {e}")
            return None
