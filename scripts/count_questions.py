#!/usr/bin/env python3
"""Count questions in database by language."""
import asyncio
import os
from sqlalchemy import select, func, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.db.models import QuestionTemplate


@asynccontextmanager
async def get_db_session():
    """Simple database session."""
    db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/mindsethappybot')
    engine = create_async_engine(db_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def main():
    async with get_db_session() as session:
        # Total count
        result = await session.execute(
            select(func.count()).select_from(QuestionTemplate)
        )
        total = result.scalar()
        print(f"\n{'='*50}")
        print(f"TOTAL QUESTIONS IN DATABASE: {total}")
        print(f"{'='*50}\n")
        
        # By language
        result = await session.execute(
            select(
                QuestionTemplate.language_code, 
                func.count()
            )
            .select_from(QuestionTemplate)
            .group_by(QuestionTemplate.language_code)
            .order_by(QuestionTemplate.language_code)
        )
        
        print("BY LANGUAGE:")
        for lang, count in result.all():
            print(f"  {lang.upper()}: {count}")
        
        # By category
        result = await session.execute(
            select(
                QuestionTemplate.category, 
                func.count()
            )
            .select_from(QuestionTemplate)
            .group_by(QuestionTemplate.category)
            .order_by(QuestionTemplate.category)
        )
        
        print("\nBY CATEGORY:")
        for category, count in result.all():
            print(f"  {category}: {count}")
        print()


if __name__ == '__main__':
    asyncio.run(main())
