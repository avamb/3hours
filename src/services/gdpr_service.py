"""
MINDSETHAPPYBOT - GDPR service
Handles data export and deletion for GDPR compliance
"""
import logging
import json
from datetime import datetime
from typing import Optional
import io

from aiogram.types import BufferedInputFile
from sqlalchemy import select, delete

from src.db.database import get_session
from src.db.models import User, Moment, Conversation, UserStats, ScheduledNotification

logger = logging.getLogger(__name__)


class GDPRService:
    """Service for GDPR compliance - data export and deletion"""

    async def export_user_data(self, telegram_id: int) -> Optional[BufferedInputFile]:
        """
        Export all user data as JSON file

        Returns:
            BufferedInputFile for sending to user, or None if user not found
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return None

            # Collect all data
            export_data = {
                "export_date": datetime.utcnow().isoformat(),
                "user": {
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "language_code": user.language_code,
                    "formal_address": user.formal_address,
                    "active_hours_start": str(user.active_hours_start),
                    "active_hours_end": str(user.active_hours_end),
                    "notification_interval_hours": user.notification_interval_hours,
                    "notifications_enabled": user.notifications_enabled,
                    "timezone": user.timezone,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat(),
                },
                "moments": [],
                "conversations": [],
                "statistics": None,
            }

            # Get moments
            result = await session.execute(
                select(Moment).where(Moment.user_id == user.id).order_by(Moment.created_at)
            )
            moments = result.scalars().all()

            for moment in moments:
                export_data["moments"].append({
                    "content": moment.content,
                    "source_type": moment.source_type,
                    "mood_score": moment.mood_score,
                    "topics": moment.topics,
                    "created_at": moment.created_at.isoformat(),
                })

            # Get conversations
            result = await session.execute(
                select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.created_at)
            )
            conversations = result.scalars().all()

            for conv in conversations:
                export_data["conversations"].append({
                    "message_type": conv.message_type,
                    "content": conv.content,
                    "metadata": conv.metadata,
                    "created_at": conv.created_at.isoformat(),
                })

            # Get stats
            result = await session.execute(
                select(UserStats).where(UserStats.user_id == user.id)
            )
            stats = result.scalar_one_or_none()

            if stats:
                export_data["statistics"] = {
                    "current_streak": stats.current_streak,
                    "longest_streak": stats.longest_streak,
                    "total_moments": stats.total_moments,
                    "total_questions_sent": stats.total_questions_sent,
                    "total_questions_answered": stats.total_questions_answered,
                    "last_response_date": stats.last_response_date.isoformat() if stats.last_response_date else None,
                }

            # Create JSON file
            json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
            file_bytes = json_data.encode("utf-8")

            filename = f"mindsethappybot_data_{telegram_id}_{datetime.utcnow().strftime('%Y%m%d')}.json"

            return BufferedInputFile(file_bytes, filename=filename)

    async def delete_all_user_data(self, telegram_id: int) -> bool:
        """
        Delete all user data (GDPR right to be forgotten)

        Returns:
            True if deletion was successful, False if user not found
        """
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False

            user_id = user.id

            # Delete in order (respecting foreign keys)
            # Note: With ON DELETE CASCADE, we only need to delete the user

            # But let's be explicit for logging purposes
            logger.info(f"Deleting all data for user {telegram_id}")

            # Delete scheduled notifications
            await session.execute(
                delete(ScheduledNotification).where(ScheduledNotification.user_id == user_id)
            )
            logger.debug(f"Deleted scheduled notifications for user {user_id}")

            # Delete stats
            await session.execute(
                delete(UserStats).where(UserStats.user_id == user_id)
            )
            logger.debug(f"Deleted stats for user {user_id}")

            # Delete conversations
            await session.execute(
                delete(Conversation).where(Conversation.user_id == user_id)
            )
            logger.debug(f"Deleted conversations for user {user_id}")

            # Delete moments (including embeddings)
            await session.execute(
                delete(Moment).where(Moment.user_id == user_id)
            )
            logger.debug(f"Deleted moments for user {user_id}")

            # Finally delete user
            await session.execute(
                delete(User).where(User.id == user_id)
            )

            await session.commit()
            logger.info(f"Successfully deleted all data for user {telegram_id}")

            return True
