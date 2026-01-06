"""
MINDSETHAPPYBOT - User service
Business logic for user management
"""
import logging
from typing import Optional
from datetime import datetime

from aiogram.types import User as TelegramUser
from sqlalchemy import select

from src.db.database import get_session
from src.db.models import User, UserStats

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related operations"""

    async def get_or_create_user(self, telegram_user: TelegramUser) -> User:
        """
        Get existing user or create new one from Telegram user object
        """
        async with get_session() as session:
            # Try to find existing user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_user.id)
            )
            user = result.scalar_one_or_none()

            if user:
                # Update last active
                user.last_active_at = datetime.utcnow()
                await session.commit()
                return user

            # Create new user
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name or "Друг",
                language_code=telegram_user.language_code or "ru",
            )
            session.add(user)
            await session.flush()

            # Create user stats
            stats = UserStats(user_id=user.id)
            session.add(stats)

            await session.commit()
            logger.info(f"Created new user: {user.telegram_id}")

            return user

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()

    async def update_user_settings(
        self,
        telegram_id: int,
        formal_address: Optional[bool] = None,
        active_hours_start: Optional[str] = None,
        active_hours_end: Optional[str] = None,
        notification_interval_hours: Optional[int] = None,
        notifications_enabled: Optional[bool] = None,
        language_code: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> Optional[User]:
        """Update user settings"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return None

            if formal_address is not None:
                user.formal_address = formal_address

            if active_hours_start is not None:
                from datetime import time
                h, m = map(int, active_hours_start.split(":"))
                user.active_hours_start = time(h, m)

            if active_hours_end is not None:
                from datetime import time
                h, m = map(int, active_hours_end.split(":"))
                user.active_hours_end = time(h, m)

            if notification_interval_hours is not None:
                user.notification_interval_hours = notification_interval_hours

            if notifications_enabled is not None:
                user.notifications_enabled = notifications_enabled

            if language_code is not None:
                user.language_code = language_code

            if timezone is not None:
                user.timezone = timezone

            user.updated_at = datetime.utcnow()
            await session.commit()

            logger.info(f"Updated settings for user {telegram_id}")
            return user

    async def complete_onboarding(self, telegram_id: int) -> bool:
        """Mark user onboarding as completed"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False

            user.onboarding_completed = True
            user.updated_at = datetime.utcnow()
            await session.commit()

            logger.info(f"Onboarding completed for user {telegram_id}")
            return True

    async def reset_settings_to_defaults(self, telegram_id: int) -> bool:
        """Reset all user settings to default values"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False

            from datetime import time

            user.formal_address = False
            user.active_hours_start = time(9, 0)
            user.active_hours_end = time(21, 0)
            user.notification_interval_hours = 3
            user.notifications_enabled = True
            user.updated_at = datetime.utcnow()

            await session.commit()
            logger.info(f"Reset settings for user {telegram_id}")
            return True
