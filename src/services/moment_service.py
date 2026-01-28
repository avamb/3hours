"""
MINDSETHAPPYBOT - Moment service
Business logic for managing positive moments
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import random

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.db.database import get_session
from src.db.models import Moment, User
from src.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class MomentService:
    """Service for moment-related operations"""

    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def create_moment(
        self,
        telegram_id: int,
        content: str,
        source_type: str = "text",
        voice_file_id: Optional[str] = None,
    ) -> Optional[Moment]:
        """
        Create a new moment with embedding
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.error(f"User not found: {telegram_id}")
                return None

            # Create embedding
            embedding = await self.embedding_service.create_embedding(content)

            # Analyze mood
            mood_score = await self.embedding_service.analyze_mood(content)

            # Extract topics
            topics = await self.embedding_service.extract_topics(content)

            # Create moment
            moment = Moment(
                user_id=user.id,
                content=content,
                source_type=source_type,
                original_voice_file_id=voice_file_id,
                embedding=embedding,
                mood_score=mood_score,
                topics=topics,
            )
            session.add(moment)

            # Update user stats
            from src.services.stats_service import StatsService
            stats_service = StatsService()
            await stats_service.increment_moments(session, user.id)

            await session.commit()
            logger.info(f"Created moment for user {telegram_id}: {content[:50]}...")

            return moment

    async def get_user_moments(
        self,
        telegram_id: int,
        limit: int = 10,
        offset: int = 0,
        period: Optional[str] = None,
    ) -> List[Moment]:
        """
        Get user's moments with optional filtering
        period: 'today', 'week', 'month', or None for all
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return []

            # Build query
            query = select(Moment).where(Moment.user_id == user.id)

            # Apply period filter
            now = datetime.now(timezone.utc)
            if period == "today":
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.where(Moment.created_at >= start)
            elif period == "week":
                start = now - timedelta(days=7)
                query = query.where(Moment.created_at >= start)
            elif period == "month":
                start = now - timedelta(days=30)
                query = query.where(Moment.created_at >= start)

            # Order and paginate
            query = query.order_by(Moment.created_at.desc()).offset(offset).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_user_moments_by_date(
        self,
        telegram_id: int,
        start_date: datetime,
        end_date: datetime,
        limit: int = 20,
    ) -> List[Moment]:
        """
        Get user's moments within a specific date range
        
        Args:
            telegram_id: User's Telegram ID
            start_date: Start of date range (inclusive)
            end_date: End of date range (exclusive)
            limit: Maximum number of moments to return
        
        Returns:
            List of moments within the date range, ordered by most recent first
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return []

            # Build query with date range filter
            from sqlalchemy import and_
            query = (
                select(Moment)
                .where(
                    and_(
                        Moment.user_id == user.id,
                        Moment.created_at >= start_date,
                        Moment.created_at < end_date,
                    )
                )
                .order_by(Moment.created_at.desc())
                .limit(limit)
            )

            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_random_moment(self, telegram_id: int) -> Optional[Moment]:
        """Get a random moment for the user"""
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return None

            # Count moments
            count_result = await session.execute(
                select(func.count(Moment.id)).where(Moment.user_id == user.id)
            )
            count = count_result.scalar()

            if count == 0:
                return None

            # Get random offset
            random_offset = random.randint(0, count - 1)

            result = await session.execute(
                select(Moment)
                .where(Moment.user_id == user.id)
                .offset(random_offset)
                .limit(1)
            )
            return result.scalar_one_or_none()

    async def find_similar_moments(
        self,
        telegram_id: int,
        query_text: str,
        limit: int = 5,
    ) -> List[Moment]:
        """
        Find semantically similar moments using vector search
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return []

            # Create query embedding
            query_embedding = await self.embedding_service.create_embedding(query_text)

            if query_embedding is None:
                return []

            # Vector similarity search using pgvector
            # Using cosine distance
            result = await session.execute(
                select(Moment)
                .where(Moment.user_id == user.id)
                .where(Moment.embedding.isnot(None))
                .order_by(Moment.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )

            return list(result.scalars().all())

    async def delete_moment(self, telegram_id: int, moment_id: int) -> bool:
        """Delete a specific moment"""
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False

            # Get moment (ensure it belongs to user)
            result = await session.execute(
                select(Moment)
                .where(Moment.id == moment_id)
                .where(Moment.user_id == user.id)
            )
            moment = result.scalar_one_or_none()

            if not moment:
                return False

            await session.delete(moment)
            await session.commit()

            logger.info(f"Deleted moment {moment_id} for user {telegram_id}")
            return True

    async def get_moments_count(self, telegram_id: int) -> int:
        """Get total count of user's moments"""
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return 0

            result = await session.execute(
                select(func.count(Moment.id)).where(Moment.user_id == user.id)
            )
            return result.scalar() or 0
