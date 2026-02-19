"""
MINDSETHAPPYBOT - User repository
Data access layer for User model
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User


class UserRepository:
    """Repository for User data access"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by internal ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Create new user"""
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: User) -> User:
        """Update user"""
        await self.session.flush()
        return user

    async def delete(self, user: User) -> None:
        """Delete user"""
        await self.session.delete(user)
        await self.session.flush()

    async def get_all_active(self) -> List[User]:
        """Get all users with notifications enabled"""
        result = await self.session.execute(
            select(User).where(User.notifications_enabled)
        )
        return list(result.scalars().all())
