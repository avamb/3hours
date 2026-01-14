"""
MINDSETHAPPYBOT - Blocked user middleware
Checks if a user is blocked and prevents them from interacting with the bot
"""
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from sqlalchemy import select
from src.db.database import get_session
from src.db.models.user import User

logger = logging.getLogger(__name__)


class BlockedUserMiddleware(BaseMiddleware):
    """Middleware that blocks users who have been blocked by admin"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Get the telegram user id from the event
        telegram_id = None

        if isinstance(event, Message) and event.from_user:
            telegram_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            telegram_id = event.from_user.id

        if telegram_id:
            try:
                async with get_session() as session:
                    result = await session.execute(
                        select(User.is_blocked).where(User.telegram_id == telegram_id)
                    )
                    row = result.scalar_one_or_none()

                    # If user exists and is blocked, silently ignore the update
                    if row is True:
                        logger.info(f"Blocked user {telegram_id} tried to interact with bot")
                        return None
            except Exception as e:
                # If we can't check, allow the request (fail open for user experience)
                logger.warning(f"Failed to check blocked status for {telegram_id}: {e}")

        # User is not blocked or not in database yet, proceed with handler
        return await handler(event, data)
