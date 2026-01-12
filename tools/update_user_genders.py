#!/usr/bin/env python3
"""
Script to detect and update gender for existing users based on their names/usernames.
Run this once after adding the gender column to update existing users.
"""
import asyncio
import logging
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from src.db.database import get_session
from src.db.models import User
from src.utils.gender_detection import detect_user_gender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_all_user_genders():
    """Update gender for all existing users where gender is null or unknown."""
    async with get_session() as session:
        # Get all users with unknown or null gender
        result = await session.execute(
            select(User).where(
                (User.gender == None) | (User.gender == 'unknown') | (User.gender == '')
            )
        )
        users = result.scalars().all()

        logger.info(f"Found {len(users)} users to process")

        updated_count = 0
        for user in users:
            detected_gender = detect_user_gender(
                first_name=user.first_name,
                last_name=None,  # We don't store last_name separately yet
                username=user.username
            )

            if detected_gender != 'unknown':
                user.gender = detected_gender
                updated_count += 1
                logger.info(f"User {user.id} ({user.first_name}, @{user.username}): detected as {detected_gender}")
            else:
                user.gender = 'unknown'
                logger.info(f"User {user.id} ({user.first_name}, @{user.username}): unknown gender")

        await session.commit()
        logger.info(f"Updated {updated_count} users with detected gender")
        return updated_count


if __name__ == "__main__":
    asyncio.run(update_all_user_genders())
