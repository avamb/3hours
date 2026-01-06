"""
MINDSETHAPPYBOT - Database connection and session management
Uses SQLAlchemy 2.x with asyncpg for async PostgreSQL access
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import get_settings

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_async_session_factory = None


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


async def init_db() -> None:
    """Initialize database connection"""
    global _engine, _async_session_factory

    settings = get_settings()

    _engine = create_async_engine(
        settings.database_url,
        echo=settings.log_level == "DEBUG",
        pool_size=5,
        max_overflow=10,
    )

    _async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    logger.info("Database connection initialized")


async def close_db() -> None:
    """Close database connection"""
    global _engine

    if _engine:
        await _engine.dispose()
        logger.info("Database connection closed")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_session_factory() -> async_sessionmaker:
    """Get session factory for dependency injection"""
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _async_session_factory
