"""
MINDSETHAPPYBOT - Conversation logging service
Writes messages to the conversations table for admin visibility and context.
"""

import logging
from typing import Optional, Dict, Any

from sqlalchemy import select

from src.db.database import get_session
from src.db.models import User, Conversation

logger = logging.getLogger(__name__)


class ConversationLogService:
    """Persist conversation rows (best-effort; never throws to caller)."""

    async def log(
        self,
        telegram_id: int,
        message_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            async with get_session() as session:
                result = await session.execute(select(User).where(User.telegram_id == telegram_id))
                user = result.scalar_one_or_none()
                if not user:
                    return

                row = Conversation(
                    user_id=user.id,
                    message_type=message_type,
                    content=content,
                    message_metadata=metadata,
                )
                session.add(row)
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to log conversation (tg={telegram_id}, type={message_type}): {e}")


