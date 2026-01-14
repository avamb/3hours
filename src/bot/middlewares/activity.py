"""
MINDSETHAPPYBOT - Activity middleware
Updates user activity and triggers activity-based campaign delivery
"""
import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery, TelegramObject

from src.services.campaign_activity_service import CampaignActivityDeliveryService

logger = logging.getLogger(__name__)

_campaign_service = CampaignActivityDeliveryService.get_instance()


class ActivityMiddleware(BaseMiddleware):
    """
    Middleware that tracks user activity and triggers campaign delivery.

    On every Message or CallbackQuery:
    1. Updates user's last_active_at timestamp
    2. Checks for activity-triggered campaigns
    3. Delivers pending messages (async, non-blocking)
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Get telegram_id from the event
        telegram_id = None

        if isinstance(event, Message) and event.from_user:
            telegram_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            telegram_id = event.from_user.id

        if telegram_id:
            try:
                # Update activity and check for campaigns (non-blocking)
                asyncio.create_task(
                    self._process_activity(telegram_id)
                )
            except Exception as e:
                # Never block message processing on activity errors
                logger.error(f"Error in activity middleware: {e}")

        # Continue to handler
        return await handler(event, data)

    async def _process_activity(self, telegram_id: int) -> None:
        """Process user activity in background"""
        try:
            # Update last_active_at
            await _campaign_service.update_user_activity(telegram_id)

            # Check and deliver activity-triggered campaigns
            sent_count = await _campaign_service.check_and_deliver_activity_campaigns(
                telegram_id,
                self.bot
            )

            if sent_count > 0:
                logger.info(
                    f"Activity trigger: Sent {sent_count} campaign message(s) to {telegram_id}"
                )

        except Exception as e:
            logger.error(f"Error processing activity for {telegram_id}: {e}")
