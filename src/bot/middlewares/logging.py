"""
MINDSETHAPPYBOT - Logging middleware
Logs all incoming messages and callback queries
"""
import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from src.services.system_log_service import SystemLogService

logger = logging.getLogger(__name__)

_system_logs = SystemLogService()


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging all incoming updates"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Best-effort structured logging into DB
        try:
            if isinstance(event, Message):
                user = event.from_user
                if event.text:
                    msg = f"Message from {user.id} (@{user.username}): {event.text[:200]}"
                    logger.info(f"LoggingMiddleware: {msg}")  # Добавляем логирование в stdout
                    asyncio.create_task(_system_logs.log(
                        level="INFO",
                        source="bot.message",
                        message=msg,
                        details={"telegram_id": user.id, "username": user.username, "kind": "text"},
                    ))
                elif event.voice:
                    msg = f"Voice message from {user.id} (@{user.username})"
                    asyncio.create_task(_system_logs.log(
                        level="INFO",
                        source="bot.message",
                        message=msg,
                        details={"telegram_id": user.id, "username": user.username, "kind": "voice"},
                    ))
                else:
                    msg = f"Other message from {user.id} (@{user.username})"
                    asyncio.create_task(_system_logs.log(
                        level="INFO",
                        source="bot.message",
                        message=msg,
                        details={"telegram_id": user.id, "username": user.username, "kind": "other"},
                    ))

            elif isinstance(event, CallbackQuery):
                user = event.from_user
                msg = f"Callback from {user.id} (@{user.username}): {event.data}"
                asyncio.create_task(_system_logs.log(
                    level="INFO",
                    source="bot.callback",
                    message=msg,
                    details={"telegram_id": user.id, "username": user.username, "data": event.data},
                ))
        except Exception:
            # Never block update processing on logging failures
            pass

        try:
            return await handler(event, data)
        except Exception as e:
            # Log exception and rethrow
            try:
                details = {"error": str(e)}
                if isinstance(event, Message) and event.from_user:
                    details["telegram_id"] = event.from_user.id
                if isinstance(event, CallbackQuery) and event.from_user:
                    details["telegram_id"] = event.from_user.id
                    details["callback_data"] = event.data
                asyncio.create_task(_system_logs.log(
                    level="ERROR",
                    source="bot.exception",
                    message="Unhandled exception while handling update",
                    details=details,
                ))
            except Exception:
                pass
            raise
