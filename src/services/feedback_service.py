"""
MINDSETHAPPYBOT - Feedback service
Business logic for handling user feedback and suggestions
"""
import logging
from typing import Optional, List

from sqlalchemy import select

from src.db.database import get_session
from src.db.models import User, Feedback

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for handling user feedback"""

    async def submit_feedback(
        self,
        telegram_id: int,
        content: str,
        category: str = "suggestion"
    ) -> Optional[Feedback]:
        """
        Submit new feedback from a user

        Args:
            telegram_id: The Telegram ID of the user
            content: The feedback content
            category: Type of feedback (suggestion, bug, complaint, other)

        Returns:
            The created Feedback object or None if failed
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.error(f"User not found: telegram_id={telegram_id}")
                return None

            # Create feedback
            feedback = Feedback(
                user_id=user.id,
                content=content,
                category=category,
                status="new"
            )
            session.add(feedback)
            await session.commit()
            await session.refresh(feedback)

            logger.info(f"Feedback submitted by user {telegram_id}: {content[:50]}...")
            return feedback

    async def get_user_feedback(
        self,
        telegram_id: int,
        limit: int = 10
    ) -> List[Feedback]:
        """Get feedback submitted by a user"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return []

            result = await session.execute(
                select(Feedback)
                .where(Feedback.user_id == user.id)
                .order_by(Feedback.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    async def get_all_feedback(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Feedback]:
        """Get all feedback (for admin panel)"""
        async with get_session() as session:
            query = select(Feedback).order_by(Feedback.created_at.desc())

            if status:
                query = query.where(Feedback.status == status)

            query = query.limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_feedback_count(self, status: Optional[str] = None) -> int:
        """Get count of feedback items"""
        async with get_session() as session:
            from sqlalchemy import func
            query = select(func.count(Feedback.id))

            if status:
                query = query.where(Feedback.status == status)

            result = await session.execute(query)
            return result.scalar() or 0
