"""
MINDSETHAPPYBOT - Logging middleware
Logs all incoming messages and callback queries
"""
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging all incoming updates"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Log based on event type
        if isinstance(event, Message):
            user = event.from_user
            if event.text:
                logger.info(
                    f"Message from {user.id} (@{user.username}): {event.text[:50]}"
                )
            elif event.voice:
                logger.info(f"Voice message from {user.id} (@{user.username})")
            else:
                logger.info(f"Other message from {user.id} (@{user.username})")

        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(
                f"Callback from {user.id} (@{user.username}): {event.data}"
            )

        # Call the actual handler
        return await handler(event, data)
