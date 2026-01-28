"""
MINDSETHAPPYBOT - Statistics service
Manages user statistics and streaks
"""
import logging
from typing import Optional
from datetime import datetime, date, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_session
from src.db.models import User, UserStats

logger = logging.getLogger(__name__)


class StatsService:
    """Service for managing user statistics"""

    async def get_user_stats(self, telegram_id: int) -> Optional[UserStats]:
        """Get statistics for a user"""
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return None

            # Get stats
            result = await session.execute(
                select(UserStats).where(UserStats.user_id == user.id)
            )
            return result.scalar_one_or_none()

    async def increment_moments(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> None:
        """
        Increment moment count and update streak
        Called when a new moment is created
        """
        result = await session.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        stats = result.scalar_one_or_none()

        if not stats:
            # Create stats if not exist
            stats = UserStats(user_id=user_id)
            session.add(stats)

        today = date.today()

        # Update total moments
        stats.total_moments += 1

        # Update streak
        if stats.last_response_date is None:
            # First ever response
            stats.current_streak = 1
        elif stats.last_response_date == today:
            # Already responded today, no streak change
            pass
        elif stats.last_response_date == today - timedelta(days=1):
            # Consecutive day
            stats.current_streak += 1
        else:
            # Streak broken
            stats.current_streak = 1

        # Update longest streak if needed
        if stats.current_streak > stats.longest_streak:
            stats.longest_streak = stats.current_streak

        stats.last_response_date = today
        stats.total_questions_answered += 1
        stats.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        logger.debug(f"Updated stats for user {user_id}: streak={stats.current_streak}")

    async def increment_questions_sent(self, user_id: int) -> None:
        """Increment the count of questions sent to user"""
        async with get_session() as session:
            result = await session.execute(
                select(UserStats).where(UserStats.user_id == user_id)
            )
            stats = result.scalar_one_or_none()

            if stats:
                stats.total_questions_sent += 1
                stats.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                await session.commit()

    async def get_weekly_stats(self, telegram_id: int) -> dict:
        """Get statistics for the current week"""
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return {}

            # Calculate week boundaries
            today = datetime.now(timezone.utc).replace(tzinfo=None)
            week_start = today - timedelta(days=today.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

            # Count moments this week
            from sqlalchemy import func
            from src.db.models import Moment

            result = await session.execute(
                select(func.count(Moment.id))
                .where(Moment.user_id == user.id)
                .where(Moment.created_at >= week_start)
            )
            week_moments = result.scalar() or 0

            return {
                "week_moments": week_moments,
                "week_start": week_start,
            }

    async def get_monthly_stats(self, telegram_id: int) -> dict:
        """Get statistics for the current month"""
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return {}

            # Calculate month boundaries
            today = datetime.now(timezone.utc).replace(tzinfo=None)
            month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Count moments this month
            from sqlalchemy import func
            from src.db.models import Moment

            result = await session.execute(
                select(func.count(Moment.id))
                .where(Moment.user_id == user.id)
                .where(Moment.created_at >= month_start)
            )
            month_moments = result.scalar() or 0

            return {
                "month_moments": month_moments,
                "month_start": month_start,
            }
