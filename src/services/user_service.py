"""
MINDSETHAPPYBOT - User service
Business logic for user management
"""
import logging
import re
from typing import Optional
from datetime import datetime, timedelta

from aiogram.types import User as TelegramUser
from sqlalchemy import select, and_, delete

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from src.db.database import get_session
from src.db.models import User, UserStats, ScheduledNotification
from src.utils.gender_detection import detect_user_gender

logger = logging.getLogger(__name__)


def validate_timezone(tz_str: str) -> bool:
    """
    Validate timezone string format.

    Supports:
    - IANA timezone names (e.g., "Europe/Moscow", "America/New_York")
    - UTC offset format (e.g., "+03:00", "-05:00", "+0300", "-0500")
    - "UTC" string

    Returns:
        True if valid, False otherwise
    """
    if not tz_str:
        return False

    if tz_str == "UTC":
        return True

    # Check offset format (+03:00, -05:00, +0300, -0500)
    offset_match = re.match(r'^([+-])(\d{2}):?(\d{2})$', tz_str)
    if offset_match:
        hours = int(offset_match.group(2))
        minutes = int(offset_match.group(3))
        # Validate reasonable offset range (-12:00 to +14:00)
        return hours <= 14 and minutes < 60

    # Try as IANA timezone name
    try:
        ZoneInfo(tz_str)
        return True
    except Exception:
        return False


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

                # Update gender if not set or unknown
                if not user.gender or user.gender == 'unknown':
                    detected_gender = detect_user_gender(
                        first_name=telegram_user.first_name,
                        last_name=getattr(telegram_user, 'last_name', None),
                        username=telegram_user.username
                    )
                    if detected_gender != 'unknown':
                        user.gender = detected_gender
                        logger.info(f"Updated gender for user {user.telegram_id}: {detected_gender}")

                await session.commit()
                return user

            # Detect gender from Telegram user info
            detected_gender = detect_user_gender(
                first_name=telegram_user.first_name,
                last_name=getattr(telegram_user, 'last_name', None),
                username=telegram_user.username
            )

            # Create new user
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name or "Друг",
                gender=detected_gender,
                language_code=telegram_user.language_code or "ru",
            )
            session.add(user)
            await session.flush()

            # Create user stats
            stats = UserStats(user_id=user.id)
            session.add(stats)

            await session.commit()
            logger.info(f"Created new user: {user.telegram_id} (gender: {detected_gender})")

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
                # Validate timezone format
                if not validate_timezone(timezone):
                    logger.warning(f"Invalid timezone format: {timezone}")
                    raise ValueError(f"Invalid timezone: {timezone}")

                old_timezone = user.timezone
                user.timezone = timezone

                # If timezone changed, delete pending notifications so they get rescheduled
                if old_timezone != timezone:
                    logger.info(
                        f"Timezone changed for user {telegram_id}: {old_timezone} -> {timezone}, "
                        "deleting pending notifications for reschedule"
                    )
                    await session.execute(
                        delete(ScheduledNotification).where(
                            and_(
                                ScheduledNotification.user_id == user.id,
                                ScheduledNotification.sent == False,
                            )
                        )
                    )

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
