"""
MINDSETHAPPYBOT - Notification scheduler
Manages periodic question delivery using APScheduler
"""
import logging
from datetime import datetime, timedelta, timezone as dt_timezone
import random
import re

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_, or_

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from src.db.database import get_session
from src.db.models import User, ScheduledNotification, QuestionTemplate, Conversation
from src.bot.keyboards.inline import get_question_keyboard
from src.services.conversation_log_service import ConversationLogService
from src.services.memory_indexer_job import index_conversation_memories, create_dialog_summaries

logger = logging.getLogger(__name__)


def parse_timezone(tz_str: str) -> dt_timezone | ZoneInfo:
    """
    Parse timezone string to timezone object.

    Supports:
    - IANA timezone names (e.g., "Europe/Moscow", "America/New_York")
    - UTC offset format (e.g., "+03:00", "-05:00", "+0300", "-0500")
    - "UTC" string

    Returns:
        timezone object (datetime.timezone for offsets, ZoneInfo for IANA names)
    """
    if not tz_str or tz_str == "UTC":
        return dt_timezone.utc

    # Try to parse as offset format (+03:00, -05:00, +0300, -0500)
    offset_match = re.match(r'^([+-])(\d{2}):?(\d{2})$', tz_str)
    if offset_match:
        sign = 1 if offset_match.group(1) == '+' else -1
        hours = int(offset_match.group(2))
        minutes = int(offset_match.group(3))
        offset = timedelta(hours=hours, minutes=minutes) * sign
        return dt_timezone(offset)

    # Try as IANA timezone name
    try:
        return ZoneInfo(tz_str)
    except Exception:
        logger.warning(f"Unknown timezone: {tz_str}, falling back to UTC")
        return dt_timezone.utc


def get_user_local_now(user_timezone: str) -> datetime:
    """Get current time in user's timezone (aware datetime)"""
    tz = parse_timezone(user_timezone)
    return datetime.now(tz)


def convert_to_utc(dt: datetime, user_timezone: str) -> datetime:
    """Convert a naive or aware datetime to UTC"""
    tz = parse_timezone(user_timezone)

    if dt.tzinfo is None:
        # Assume dt is in user's timezone if naive
        dt = dt.replace(tzinfo=tz)

    return dt.astimezone(dt_timezone.utc)


def is_within_active_hours(user: 'User') -> bool:
    """
    Check if current time in user's timezone is within their active hours.
    Uses timezone-aware comparison.
    """
    user_now = get_user_local_now(user.timezone)
    user_local_time = user_now.time()

    result = user.active_hours_start <= user_local_time <= user.active_hours_end

    logger.debug(
        f"Active hours check for user {user.telegram_id}: "
        f"tz={user.timezone}, local_now={user_local_time}, "
        f"active_range=[{user.active_hours_start}-{user.active_hours_end}], "
        f"in_range={result}"
    )

    return result

# Default question templates for Russian
# Base question templates (gender-neutral or will be adapted)
DEFAULT_QUESTIONS_INFORMAL = [
    "Что хорошего произошло сегодня? 🌟",
    "Расскажи, чему ты порадовался? ✨",  # Will be adapted: порадовался/порадовалась
    "Что приятного случилось? 😊",
    "Какой момент сегодня был особенным? 💫",
    "Что тебя сегодня вдохновило? 🌈",
    "Расскажи о маленькой радости дня! 💝",
    "Что хорошего ты заметил сегодня? 🌻",  # Will be adapted: заметил/заметила
    "Чему ты улыбнулся сегодня? 😄",  # Will be adapted: улыбнулся/улыбнулась
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


def adapt_question_for_gender(question: str, gender: str, formal: bool = False) -> str:
    """
    Adapt question text to match user's gender for Russian language.
    
    Args:
        question: Original question text
        gender: 'male', 'female', or 'unknown'
        formal: Whether using formal address (Вы vs ты)
    
    Returns:
        Question adapted for gender (if Russian and gender is known)
    """
    if gender == 'unknown' or gender not in ['male', 'female']:
        return question
    
    # Only adapt Russian questions
    if not any(cyrillic in question for cyrillic in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'):
        return question
    
    adapted = question
    
    if not formal:
        # Informal "ты" questions - adapt verb endings
        if gender == 'female':
            # Replace masculine verb endings with feminine
            replacements = [
                (r'\bты\s+заметил\b', 'ты заметила'),
                (r'\bты\s+улыбнулся\b', 'ты улыбнулась'),
                (r'\bты\s+порадовался\b', 'ты порадовалась'),
                (r'\bты\s+поделился\b', 'ты поделилась'),
                (r'\bты\s+сделал\b', 'ты сделала'),
                (r'\bты\s+почувствовал\b', 'ты почувствовала'),
                (r'\bты\s+узнал\b', 'ты узнала'),
                (r'\bты\s+вспомнил\b', 'ты вспомнила'),
            ]
            for pattern, replacement in replacements:
                adapted = re.sub(pattern, replacement, adapted, flags=re.IGNORECASE)
    
    return adapted


class NotificationScheduler:
    """Manages scheduled notifications for users"""

    _instance: 'NotificationScheduler | None' = None

    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self._last_questions: dict[int, str] = {}  # user_id -> last question
        self._conversation_log = ConversationLogService()
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

        # Check hourly for users who should receive weekly/monthly summaries
        # (timezone-aware: sends at 10:00 in each user's local timezone)
        self.scheduler.add_job(
            self._check_summary_delivery,
            trigger=IntervalTrigger(hours=1),
            id="summary_delivery_check",
            replace_existing=True,
        )

        # Fallback check for missed summaries: Monday morning and Sunday evening
        # Checks if weekly summary was missed and sends it if needed
        self.scheduler.add_job(
            self._check_missed_summaries,
            trigger=IntervalTrigger(hours=1),
            id="missed_summaries_check",
            replace_existing=True,
        )

        # Index conversation memories every 15 minutes
        # Extracts memory-worthy facts from user conversations
        self.scheduler.add_job(
            index_conversation_memories,
            trigger=IntervalTrigger(minutes=15),
            id="memory_indexer",
            replace_existing=True,
        )

        # Create dialog summaries every 2 hours
        # Compresses multiple raw memories into semantic summaries
        self.scheduler.add_job(
            create_dialog_summaries,
            trigger=IntervalTrigger(hours=2),
            id="dialog_summary_creator",
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
        # Use UTC-aware datetime, then convert to naive for DB comparison
        utc_now = datetime.now(dt_timezone.utc).replace(tzinfo=None)

        async with get_session() as session:
            # Find unsent notifications that are due
            result = await session.execute(
                select(ScheduledNotification)
                .where(
                    and_(
                        ScheduledNotification.sent == False,
                        ScheduledNotification.scheduled_time <= utc_now,
                    )
                )
                .limit(50)
            )
            notifications = result.scalars().all()

            for notification in notifications:
                try:
                    await self._send_notification(notification)
                    notification.sent = True
                    notification.sent_at = datetime.now(dt_timezone.utc).replace(tzinfo=None)
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

            # Check if user is blocked
            if user.is_blocked:
                logger.debug(f"User {user.telegram_id} is blocked, skipping notification")
                return

            # Check if within active hours (timezone-aware)
            if not is_within_active_hours(user):
                # Outside active hours, skipping this notification
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
                await self._conversation_log.log(
                    telegram_id=user.telegram_id,
                    message_type="bot_question",
                    content=question,
                    metadata={"source": "scheduled"},
                )

                # Update stats
                from src.services.stats_service import StatsService
                stats_service = StatsService()
                await stats_service.increment_questions_sent(user.id)

            except TelegramBadRequest as e:
                error_message = str(e).lower()
                
                # Handle "bot was blocked by the user" - mark user as blocked
                if "bot was blocked by the user" in error_message:
                    async with get_session() as session:
                        result = await session.execute(
                            select(User).where(User.id == user.id)
                        )
                        db_user = result.scalar_one_or_none()
                        if db_user and not db_user.is_blocked:
                            db_user.is_blocked = True
                            await session.commit()
                            logger.info(f"Marked user {user.telegram_id} as blocked (auto-detected)")
                    # Don't log as ERROR - this is expected behavior
                    logger.debug(f"User {user.telegram_id} blocked the bot")
                
                # Handle "bot can't initiate conversation" - this is normal for new users
                elif "can't initiate conversation" in error_message:
                    # This is normal - user hasn't started conversation yet
                    logger.debug(f"User {user.telegram_id} hasn't started conversation yet")
                
                # Other Telegram API errors
                else:
                    logger.warning(f"Telegram API error for user {user.telegram_id}: {e}")
            
            except TelegramAPIError as e:
                logger.warning(f"Telegram API error for user {user.telegram_id}: {e}")
            
            except Exception as e:
                logger.error(f"Failed to send message to {user.telegram_id}: {e}")

    def _get_question(self, user: User) -> str:
        """Get a random question that wasn't used last time, adapted for user's gender"""
        questions = (
            DEFAULT_QUESTIONS_FORMAL if user.formal_address else DEFAULT_QUESTIONS_INFORMAL
        )

        # Avoid repeating last question
        last_question = self._last_questions.get(user.id)
        available = [q for q in questions if q != last_question]

        if not available:
            available = questions

        question = random.choice(available)
        
        # Adapt question for user's gender (for Russian language)
        gender = user.gender if user.gender else "unknown"
        question = adapt_question_for_gender(question, gender, user.formal_address)
        
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
                await self._conversation_log.log(
                    telegram_id=telegram_id,
                    message_type="bot_question",
                    content=question,
                    metadata={"source": "onboarding"},
                )

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
                        User.is_blocked == False,
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
        """Schedule next notification for a specific user (timezone-aware)"""
        utc_now = datetime.now(dt_timezone.utc)

        # Check if there's already a pending notification
        result = await session.execute(
            select(ScheduledNotification)
            .where(
                and_(
                    ScheduledNotification.user_id == user.id,
                    ScheduledNotification.sent == False,
                    ScheduledNotification.scheduled_time > utc_now.replace(tzinfo=None),
                )
            )
            .limit(1)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Already has a scheduled notification
            return

        # Get user's current local time
        user_tz = parse_timezone(user.timezone)
        user_local_now = datetime.now(user_tz)

        # Calculate next notification time in user's local timezone
        next_time_local = user_local_now + timedelta(hours=user.notification_interval_hours)

        # Ensure it's within active hours (in user's local time)
        if next_time_local.time() < user.active_hours_start:
            # Set to start of active hours (same day)
            next_time_local = next_time_local.replace(
                hour=user.active_hours_start.hour,
                minute=user.active_hours_start.minute,
                second=0,
                microsecond=0,
            )
        elif next_time_local.time() > user.active_hours_end:
            # Schedule for next day at start of active hours
            next_time_local = next_time_local + timedelta(days=1)
            next_time_local = next_time_local.replace(
                hour=user.active_hours_start.hour,
                minute=user.active_hours_start.minute,
                second=0,
                microsecond=0,
            )

        # Convert to UTC for storage (naive datetime for DB compatibility)
        next_time_utc = next_time_local.astimezone(dt_timezone.utc).replace(tzinfo=None)

        # Create notification
        notification = ScheduledNotification(
            user_id=user.id,
            scheduled_time=next_time_utc,
        )
        session.add(notification)

        # Detailed logging
        logger.info(
            f"Scheduled notification for user {user.telegram_id}: "
            f"tz={user.timezone}, local_now={user_local_now.strftime('%Y-%m-%d %H:%M %Z')}, "
            f"utc_now={utc_now.strftime('%Y-%m-%d %H:%M %Z')}, "
            f"next_local={next_time_local.strftime('%Y-%m-%d %H:%M %Z')}, "
            f"next_utc={next_time_utc.strftime('%Y-%m-%d %H:%M')}"
        )

    async def _check_summary_delivery(self) -> None:
        """
        Check which users should receive weekly/monthly summaries based on their local timezone.

        This runs hourly and checks each user's local time:
        - Weekly summary: Sunday, not earlier than 10:00, at the start of user's active hours
        - Monthly summary: 1st of month, not earlier than 10:00, at the start of user's active hours

        If user's active hours start at 12:00, summary will be sent at 12:00 (not 10:00).
        Only sends if user is within their active hours.
        """
        logger.info("Checking for summary delivery...")

        from src.services.summary_service import SummaryService
        summary_service = SummaryService()

        async with get_session() as session:
            # Get all users with notifications enabled and onboarding completed (exclude blocked)
            result = await session.execute(
                select(User).where(
                    and_(
                        User.notifications_enabled == True,
                        User.onboarding_completed == True,
                        User.is_blocked == False,
                    )
                )
            )
            users = result.scalars().all()

            weekly_count = 0
            monthly_count = 0

            for user in users:
                try:
                    # Get user's local time
                    user_local_now = get_user_local_now(user.timezone)
                    local_hour = user_local_now.hour
                    local_minute = user_local_now.minute
                    local_day_of_week = user_local_now.weekday()  # 0=Monday, 6=Sunday
                    local_day_of_month = user_local_now.day

                    # Weekly summary: Sunday (weekday() == 6)
                    if local_day_of_week == 6:
                        # Check if it's at least 10:00 local time
                        is_after_10am = local_hour > 10 or (local_hour == 10 and local_minute >= 0)
                        
                        if not is_after_10am:
                            logger.debug(f"User {user.telegram_id} local time is {local_hour}:{local_minute:02d}, before 10:00, skipping weekly summary")
                            continue

                        # Check if within active hours
                        if not is_within_active_hours(user):
                            logger.debug(
                                f"User {user.telegram_id} on Sunday after 10:00 but outside active hours "
                                f"({user.active_hours_start}-{user.active_hours_end}), skipping weekly summary"
                            )
                            continue

                        # Check if weekly summary was already sent this week
                        was_sent = await self._was_weekly_summary_sent_this_week(user, session)
                        if was_sent:
                            logger.debug(
                                f"User {user.telegram_id} already received weekly summary this week, skipping"
                            )
                            continue

                        logger.info(
                            f"Generating weekly summary for user {user.telegram_id} "
                            f"(Sunday, local time {local_hour}:{local_minute:02d})"
                        )
                        summary = await summary_service.generate_weekly_summary(user.telegram_id)
                        if summary:
                            await self.bot.send_message(
                                chat_id=user.telegram_id,
                                text=summary,
                            )
                            # Log summary to conversation history
                            await self._conversation_log.log(
                                telegram_id=user.telegram_id,
                                message_type="bot_reply",
                                content=summary,
                                metadata={"source": "weekly_summary"},
                            )
                            weekly_count += 1
                            logger.info(
                                f"Sent weekly summary to user {user.telegram_id} "
                                f"(tz={user.timezone}, local_time={user_local_now.strftime('%Y-%m-%d %H:%M')}, "
                                f"active_hours={user.active_hours_start}-{user.active_hours_end})"
                            )
                        else:
                            logger.info(f"No weekly summary generated for user {user.telegram_id} (no moments in last 7 days)")

                    # Monthly summary: 1st of month
                    if local_day_of_month == 1:
                        # Check if it's at least 10:00 local time
                        is_after_10am = local_hour > 10 or (local_hour == 10 and local_minute >= 0)
                        
                        if not is_after_10am:
                            logger.debug(f"User {user.telegram_id} local time is {local_hour}:{local_minute:02d}, before 10:00, skipping monthly summary")
                            continue

                        # Check if within active hours
                        if not is_within_active_hours(user):
                            logger.debug(
                                f"User {user.telegram_id} on 1st of month after 10:00 but outside active hours "
                                f"({user.active_hours_start}-{user.active_hours_end}), skipping monthly summary"
                            )
                            continue

                        # Check if monthly summary was already sent this month
                        was_sent = await self._was_monthly_summary_sent_this_month(user, session)
                        if was_sent:
                            logger.debug(
                                f"User {user.telegram_id} already received monthly summary this month, skipping"
                            )
                            continue

                        logger.info(
                            f"Generating monthly summary for user {user.telegram_id} "
                            f"(1st of month, local time {local_hour}:{local_minute:02d})"
                        )
                        summary = await summary_service.generate_monthly_summary(user.telegram_id)
                        if summary:
                            await self.bot.send_message(
                                chat_id=user.telegram_id,
                                text=summary,
                            )
                            # Log summary to conversation history
                            await self._conversation_log.log(
                                telegram_id=user.telegram_id,
                                message_type="bot_reply",
                                content=summary,
                                metadata={"source": "monthly_summary"},
                            )
                            monthly_count += 1
                            logger.info(
                                f"Sent monthly summary to user {user.telegram_id} "
                                f"(tz={user.timezone}, local_time={user_local_now.strftime('%Y-%m-%d %H:%M')}, "
                                f"active_hours={user.active_hours_start}-{user.active_hours_end})"
                            )
                        else:
                            logger.info(f"No monthly summary generated for user {user.telegram_id} (no moments in last month)")

                except Exception as e:
                    logger.error(f"Failed to send summary to {user.telegram_id}: {e}")

            if weekly_count > 0 or monthly_count > 0:
                logger.info(f"Summary delivery check: {weekly_count} weekly, {monthly_count} monthly summaries sent")

    async def _was_weekly_summary_sent_this_week(self, user: User, session) -> bool:
        """
        Check if weekly summary was already sent to user this week.
        Looks for summary messages in conversation_log table using metadata.
        """
        from sqlalchemy import text
        
        # Calculate week start (last Sunday at 00:00)
        # weekday() returns 0=Monday, 1=Tuesday, ..., 6=Sunday
        user_local_now = get_user_local_now(user.timezone)
        days_since_sunday = (user_local_now.weekday() + 1) % 7  # Convert: 0=Monday -> 1, 6=Sunday -> 0
        week_start = user_local_now - timedelta(days=days_since_sunday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start_utc = convert_to_utc(week_start, user.timezone)

        # Check if there's a weekly summary message this week using metadata
        # Weekly summaries are logged with metadata={"source": "weekly_summary"}
        result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user.id)
            .where(Conversation.created_at >= week_start_utc)
            .where(Conversation.message_type == 'bot_reply')
            .where(text("metadata->>'source' = 'weekly_summary'"))
            .order_by(Conversation.created_at.desc())
            .limit(1)
        )
        summary_message = result.scalar_one_or_none()
        
        return summary_message is not None

    async def _was_monthly_summary_sent_this_month(self, user: User, session) -> bool:
        """
        Check if monthly summary was already sent to user this month.
        Looks for summary messages in conversation_log table using metadata.
        """
        from sqlalchemy import text
        
        # Calculate month start (1st day at 00:00)
        user_local_now = get_user_local_now(user.timezone)
        month_start = user_local_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start_utc = convert_to_utc(month_start, user.timezone)

        # Check if there's a monthly summary message this month using metadata
        # Monthly summaries are logged with metadata={"source": "monthly_summary"}
        result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user.id)
            .where(Conversation.created_at >= month_start_utc)
            .where(Conversation.message_type == 'bot_reply')
            .where(text("metadata->>'source' = 'monthly_summary'"))
            .order_by(Conversation.created_at.desc())
            .limit(1)
        )
        summary_message = result.scalar_one_or_none()
        
        return summary_message is not None

    async def _check_missed_summaries(self) -> None:
        """
        Fallback check for missed weekly/monthly summaries.
        
        Checks:
        - Monday morning: if weekly summary wasn't sent on Sunday, send it
        - Sunday evening (after 18:00): if summary wasn't sent during active hours, send it
        - 2nd of month: if monthly summary wasn't sent on 1st, send it
        """
        logger.debug("Checking for missed summaries...")

        from src.services.summary_service import SummaryService
        summary_service = SummaryService()

        async with get_session() as session:
            # Get all users with notifications enabled and onboarding completed (exclude blocked)
            result = await session.execute(
                select(User).where(
                    and_(
                        User.notifications_enabled == True,
                        User.onboarding_completed == True,
                        User.is_blocked == False,
                    )
                )
            )
            users = result.scalars().all()

            weekly_fallback_count = 0
            monthly_fallback_count = 0

            for user in users:
                try:
                    # Get user's local time
                    user_local_now = get_user_local_now(user.timezone)
                    local_hour = user_local_now.hour
                    local_day_of_week = user_local_now.weekday()  # 0=Monday, 6=Sunday
                    local_day_of_month = user_local_now.day

                    # Weekly summary fallback checks
                    if local_day_of_week == 0:  # Monday
                        # Monday morning (6:00-12:00): check if weekly summary was missed
                        if 6 <= local_hour < 12:
                            was_sent = await self._was_weekly_summary_sent_this_week(user, session)
                            if not was_sent:
                                logger.info(
                                    f"Fallback: Weekly summary was not sent to user {user.telegram_id} on Sunday, "
                                    f"sending on Monday morning (local time: {user_local_now.strftime('%Y-%m-%d %H:%M')})"
                                )
                                summary = await summary_service.generate_weekly_summary(user.telegram_id)
                                if summary:
                                    await self.bot.send_message(
                                        chat_id=user.telegram_id,
                                        text=summary,
                                    )
                                    # Log summary to conversation history
                                    await self._conversation_log.log(
                                        telegram_id=user.telegram_id,
                                        message_type="bot_reply",
                                        content=summary,
                                        metadata={"source": "weekly_summary_fallback"},
                                    )
                                    weekly_fallback_count += 1
                                    logger.info(
                                        f"Fallback: Sent weekly summary to user {user.telegram_id} "
                                        f"(tz={user.timezone}, local_time={user_local_now.strftime('%Y-%m-%d %H:%M')})"
                                    )
                                else:
                                    logger.info(f"Fallback: No weekly summary generated for user {user.telegram_id} (no moments in last 7 days)")

                    elif local_day_of_week == 6:  # Sunday
                        # Sunday evening (after 18:00): check if summary wasn't sent during active hours
                        if local_hour >= 18:
                            was_sent = await self._was_weekly_summary_sent_this_week(user, session)
                            if not was_sent:
                                # Check if user is within active hours now
                                if is_within_active_hours(user):
                                    logger.info(
                                        f"Fallback: Weekly summary was not sent to user {user.telegram_id} during active hours, "
                                        f"sending on Sunday evening (local time: {user_local_now.strftime('%Y-%m-%d %H:%M')})"
                                    )
                                    summary = await summary_service.generate_weekly_summary(user.telegram_id)
                                    if summary:
                                        await self.bot.send_message(
                                            chat_id=user.telegram_id,
                                            text=summary,
                                        )
                                        # Log summary to conversation history
                                        await self._conversation_log.log(
                                            telegram_id=user.telegram_id,
                                            message_type="bot_reply",
                                            content=summary,
                                            metadata={"source": "weekly_summary_fallback"},
                                        )
                                        weekly_fallback_count += 1
                                        logger.info(
                                            f"Fallback: Sent weekly summary to user {user.telegram_id} "
                                            f"(tz={user.timezone}, local_time={user_local_now.strftime('%Y-%m-%d %H:%M')})"
                                        )
                                    else:
                                        logger.info(f"Fallback: No weekly summary generated for user {user.telegram_id} (no moments in last 7 days)")

                    # Monthly summary fallback: 2nd of month, morning
                    if local_day_of_month == 2 and 6 <= local_hour < 12:
                        # Check if monthly summary was sent on 1st
                        # Calculate 1st of month start
                        month_start = user_local_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                        month_start_utc = convert_to_utc(month_start, user.timezone)
                        
                        result = await session.execute(
                            select(Conversation)
                            .where(Conversation.user_id == user.id)
                            .where(Conversation.created_at >= month_start_utc)
                            .where(
                                or_(
                                    Conversation.content.ilike('%месяц%'),
                                    Conversation.content.ilike('%месяца%'),
                                    Conversation.content.ilike('%month%')
                                )
                            )
                            .limit(1)
                        )
                        monthly_summary = result.scalar_one_or_none()
                        
                        if not monthly_summary:
                            logger.info(
                                f"Fallback: Monthly summary was not sent to user {user.telegram_id} on 1st, "
                                f"sending on 2nd morning (local time: {user_local_now.strftime('%Y-%m-%d %H:%M')})"
                            )
                            summary = await summary_service.generate_monthly_summary(user.telegram_id)
                            if summary:
                                await self.bot.send_message(
                                    chat_id=user.telegram_id,
                                    text=summary,
                                )
                                monthly_fallback_count += 1
                                logger.info(
                                    f"Fallback: Sent monthly summary to user {user.telegram_id} "
                                    f"(tz={user.timezone}, local_time={user_local_now.strftime('%Y-%m-%d %H:%M')})"
                                )

                except Exception as e:
                    logger.error(f"Failed to send fallback summary to {user.telegram_id}: {e}")

            if weekly_fallback_count > 0 or monthly_fallback_count > 0:
                logger.info(
                    f"Missed summaries check: {weekly_fallback_count} weekly, "
                    f"{monthly_fallback_count} monthly summaries sent as fallback"
                )

    async def _send_weekly_summaries(self) -> None:
        """
        DEPRECATED: Use _check_summary_delivery for timezone-aware delivery.
        Kept for backwards compatibility / manual triggering.
        """
        logger.info("Starting weekly summary distribution (legacy method)")
        await self._check_summary_delivery()

    async def _send_monthly_summaries(self) -> None:
        """
        DEPRECATED: Use _check_summary_delivery for timezone-aware delivery.
        Kept for backwards compatibility / manual triggering.
        """
        logger.info("Starting monthly summary distribution (legacy method)")
        await self._check_summary_delivery()

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
