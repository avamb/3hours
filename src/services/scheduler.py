"""
MINDSETHAPPYBOT - Notification scheduler
Manages periodic question delivery using APScheduler
"""
import logging
from datetime import datetime, timedelta
import random

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_

from src.db.database import get_session
from src.db.models import User, ScheduledNotification, QuestionTemplate
from src.bot.keyboards.inline import get_question_keyboard

logger = logging.getLogger(__name__)

# Default question templates for Russian
DEFAULT_QUESTIONS_INFORMAL = [
    "Что хорошего произошло сегодня? 🌟",
    "Расскажи, чему ты порадовался? ✨",
    "Что приятного случилось? 😊",
    "Какой момент сегодня был особенным? 💫",
    "Что тебя сегодня вдохновило? 🌈",
    "Расскажи о маленькой радости дня! 💝",
    "Что хорошего ты заметил сегодня? 🌻",
    "Чему ты улыбнулся сегодня? 😄",
]

DEFAULT_QUESTIONS_FORMAL = [
    "Что хорошего произошло сегодня? 🌟",
    "Расскажите, чему Вы порадовались? ✨",
    "Что приятного случилось? 😊",
    "Какой момент сегодня был особенным? 💫",
    "Что Вас сегодня вдохновило? 🌈",
    "Расскажите о маленькой радости дня! 💝",
    "Что хорошего Вы заметили сегодня? 🌻",
    "Чему Вы улыбнулись сегодня? 😄",
]


class NotificationScheduler:
    """Manages scheduled notifications for users"""

    _instance: 'NotificationScheduler | None' = None

    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self._last_questions: dict[int, str] = {}  # user_id -> last question
        NotificationScheduler._instance = self

    @classmethod
    def get_instance(cls) -> 'NotificationScheduler | None':
        """Get the singleton instance of NotificationScheduler"""
        return cls._instance

    async def start(self) -> None:
        """Start the scheduler"""
        # Add job to check for pending notifications every minute
        self.scheduler.add_job(
            self._process_notifications,
            trigger=IntervalTrigger(minutes=1),
            id="process_notifications",
            replace_existing=True,
        )

        # Add job to schedule next notifications for users
        self.scheduler.add_job(
            self._schedule_user_notifications,
            trigger=IntervalTrigger(hours=1),
            id="schedule_notifications",
            replace_existing=True,
        )

        # Add job to send weekly summaries (every Sunday at 10:00)
        self.scheduler.add_job(
            self._send_weekly_summaries,
            trigger=CronTrigger(day_of_week='sun', hour=10, minute=0),
            id="weekly_summaries",
            replace_existing=True,
        )

        # Add job to send monthly summaries (first day of month at 10:00)
        self.scheduler.add_job(
            self._send_monthly_summaries,
            trigger=CronTrigger(day=1, hour=10, minute=0),
            id="monthly_summaries",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("Notification scheduler started")

        # Initial scheduling
        await self._schedule_user_notifications()

    async def stop(self) -> None:
        """Stop the scheduler"""
        self.scheduler.shutdown(wait=False)
        logger.info("Notification scheduler stopped")

    async def _process_notifications(self) -> None:
        """Process pending notifications that are due"""
        now = datetime.utcnow()

        async with get_session() as session:
            # Find unsent notifications that are due
            result = await session.execute(
                select(ScheduledNotification)
                .where(
                    and_(
                        ScheduledNotification.sent == False,
                        ScheduledNotification.scheduled_time <= now,
                    )
                )
                .limit(50)
            )
            notifications = result.scalars().all()

            for notification in notifications:
                try:
                    await self._send_notification(notification)
                    notification.sent = True
                    notification.sent_at = datetime.utcnow()
                except Exception as e:
                    logger.error(f"Failed to send notification {notification.id}: {e}")

            await session.commit()

    async def _send_notification(self, notification: ScheduledNotification) -> None:
        """Send a single notification to user"""
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.id == notification.user_id)
            )
            user = result.scalar_one_or_none()

            if not user or not user.notifications_enabled:
                return

            # Check if within active hours
            now = datetime.utcnow()
            current_time = now.time()

            if not (user.active_hours_start <= current_time <= user.active_hours_end):
                # Outside active hours, reschedule
                logger.debug(f"User {user.telegram_id} outside active hours, skipping")
                return

            # Get question text
            question = self._get_question(user)

            # Send message
            try:
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=question,
                    reply_markup=get_question_keyboard(),
                )
                logger.info(f"Sent question to user {user.telegram_id}")

                # Update stats
                from src.services.stats_service import StatsService
                stats_service = StatsService()
                await stats_service.increment_questions_sent(user.id)

            except Exception as e:
                logger.error(f"Failed to send message to {user.telegram_id}: {e}")

    def _get_question(self, user: User) -> str:
        """Get a random question that wasn't used last time"""
        questions = (
            DEFAULT_QUESTIONS_FORMAL if user.formal_address else DEFAULT_QUESTIONS_INFORMAL
        )

        # Avoid repeating last question
        last_question = self._last_questions.get(user.id)
        available = [q for q in questions if q != last_question]

        if not available:
            available = questions

        question = random.choice(available)
        self._last_questions[user.id] = question

        return question

    async def send_first_question_after_onboarding(self, telegram_id: int) -> bool:
        """
        Send the first question immediately after onboarding completion.

        Args:
            telegram_id: The Telegram ID of the user

        Returns:
            True if question was sent successfully, False otherwise
        """
        try:
            async with get_session() as session:
                # Get user from database
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.error(f"User not found: telegram_id={telegram_id}")
                    return False

                # Check if notifications are enabled
                if not user.notifications_enabled:
                    logger.info(f"Notifications disabled for user {telegram_id}")
                    return False

                # Get a question
                question = self._get_question(user)

                # Send the message
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=question,
                    reply_markup=get_question_keyboard(),
                )
                logger.info(f"Sent first question after onboarding to user {telegram_id}")

                # Update stats
                from src.services.stats_service import StatsService
                stats_service = StatsService()
                await stats_service.increment_questions_sent(user.id)

                # Schedule the next notification
                await self._schedule_next_notification(session, user)
                await session.commit()

                return True

        except Exception as e:
            logger.error(f"Failed to send first question to {telegram_id}: {e}")
            return False


    async def _schedule_user_notifications(self) -> None:
        """Schedule upcoming notifications for all active users"""
        async with get_session() as session:
            # Get all users with notifications enabled
            result = await session.execute(
                select(User).where(
                    and_(
                        User.notifications_enabled == True,
                        User.onboarding_completed == True,
                    )
                )
            )
            users = result.scalars().all()

            for user in users:
                await self._schedule_next_notification(session, user)

            await session.commit()

    async def _schedule_next_notification(
        self,
        session,
        user: User,
    ) -> None:
        """Schedule next notification for a specific user"""
        now = datetime.utcnow()

        # Check if there's already a pending notification
        result = await session.execute(
            select(ScheduledNotification)
            .where(
                and_(
                    ScheduledNotification.user_id == user.id,
                    ScheduledNotification.sent == False,
                    ScheduledNotification.scheduled_time > now,
                )
            )
            .limit(1)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Already has a scheduled notification
            return

        # Calculate next notification time
        next_time = now + timedelta(hours=user.notification_interval_hours)

        # Ensure it's within active hours
        if next_time.time() < user.active_hours_start:
            # Set to start of active hours
            next_time = next_time.replace(
                hour=user.active_hours_start.hour,
                minute=user.active_hours_start.minute,
            )
        elif next_time.time() > user.active_hours_end:
            # Schedule for next day
            next_time = next_time + timedelta(days=1)
            next_time = next_time.replace(
                hour=user.active_hours_start.hour,
                minute=user.active_hours_start.minute,
            )

        # Create notification
        notification = ScheduledNotification(
            user_id=user.id,
            scheduled_time=next_time,
        )
        session.add(notification)

        logger.info(f"Scheduled notification for user {user.telegram_id} at {next_time}")

    async def _send_weekly_summaries(self) -> None:
        """Send weekly summaries to all active users"""
        logger.info("Starting weekly summary distribution")

        from src.services.summary_service import SummaryService
        summary_service = SummaryService()

        async with get_session() as session:
            # Get all users with notifications enabled and onboarding completed
            result = await session.execute(
                select(User).where(
                    and_(
                        User.notifications_enabled == True,
                        User.onboarding_completed == True,
                    )
                )
            )
            users = result.scalars().all()

            sent_count = 0
            for user in users:
                try:
                    # Check if within active hours
                    now = datetime.utcnow()
                    current_time = now.time()

                    if not (user.active_hours_start <= current_time <= user.active_hours_end):
                        logger.debug(f"User {user.telegram_id} outside active hours, skipping weekly summary")
                        continue

                    # Generate summary
                    summary = await summary_service.generate_weekly_summary(user.telegram_id)

                    if summary:
                        await self.bot.send_message(
                            chat_id=user.telegram_id,
                            text=summary,
                        )
                        sent_count += 1
                        logger.info(f"Sent weekly summary to user {user.telegram_id}")

                except Exception as e:
                    logger.error(f"Failed to send weekly summary to {user.telegram_id}: {e}")

        logger.info(f"Weekly summary distribution completed: {sent_count} summaries sent")

    async def _send_monthly_summaries(self) -> None:
        """Send monthly summaries to all active users"""
        logger.info("Starting monthly summary distribution")

        from src.services.summary_service import SummaryService
        summary_service = SummaryService()

        async with get_session() as session:
            # Get all users with notifications enabled and onboarding completed
            result = await session.execute(
                select(User).where(
                    and_(
                        User.notifications_enabled == True,
                        User.onboarding_completed == True,
                    )
                )
            )
            users = result.scalars().all()

            sent_count = 0
            for user in users:
                try:
                    # Check if within active hours
                    now = datetime.utcnow()
                    current_time = now.time()

                    if not (user.active_hours_start <= current_time <= user.active_hours_end):
                        logger.debug(f"User {user.telegram_id} outside active hours, skipping monthly summary")
                        continue

                    # Generate summary
                    summary = await summary_service.generate_monthly_summary(user.telegram_id)

                    if summary:
                        await self.bot.send_message(
                            chat_id=user.telegram_id,
                            text=summary,
                        )
                        sent_count += 1
                        logger.info(f"Sent monthly summary to user {user.telegram_id}")

                except Exception as e:
                    logger.error(f"Failed to send monthly summary to {user.telegram_id}: {e}")

        logger.info(f"Monthly summary distribution completed: {sent_count} summaries sent")

    async def send_summary_to_user(self, telegram_id: int, summary_type: str = "weekly") -> bool:
        """
        Manually send a summary to a specific user (for testing or on-demand)

        Args:
            telegram_id: The Telegram ID of the user
            summary_type: "weekly" or "monthly"

        Returns:
            True if summary was sent successfully, False otherwise
        """
        try:
            from src.services.summary_service import SummaryService
            summary_service = SummaryService()

            if summary_type == "weekly":
                summary = await summary_service.generate_weekly_summary(telegram_id)
            else:
                summary = await summary_service.generate_monthly_summary(telegram_id)

            if summary:
                await self.bot.send_message(
                    chat_id=telegram_id,
                    text=summary,
                )
                logger.info(f"Sent {summary_type} summary to user {telegram_id}")
                return True
            else:
                logger.info(f"No moments to summarize for user {telegram_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to send {summary_type} summary to {telegram_id}: {e}")
            return False
