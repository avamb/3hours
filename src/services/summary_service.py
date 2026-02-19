"""
MINDSETHAPPYBOT - Summary service
Generates weekly and monthly summaries of user's positive moments

Uses calendar-based date ranges:
- Weekly: Monday 00:00 through Sunday 23:59 (current calendar week)
- Monthly: 1st through last day of current month
- Today: 00:00 through 23:59 of current day

All ranges are timezone-aware and respect user's timezone setting.
"""
import logging
import time
from typing import Optional, List
from datetime import datetime
from collections import Counter

from openai import AsyncOpenAI
from sqlalchemy import select, and_

from src.config import get_settings
from src.db.database import get_session
from src.db.models import User, Moment, UserStats
from src.utils.text_filters import (
    ABROAD_PHRASE_RULE_RU,
    FORBIDDEN_SYMBOLS_RULE_RU,
    apply_all_filters,
)
from src.utils.date_ranges import (
    get_today_range,
    get_week_range,
    get_previous_week_range,
    get_month_range,
    format_summary_header,
)
from src.services.personalization_service import LANGUAGE_INSTRUCTION, PROMPT_PROTECTION, get_gender_instruction
from src.services.api_usage_service import APIUsageService

logger = logging.getLogger(__name__)


class SummaryService:
    """Service for generating periodic summaries of user's moments"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_chat_model

    async def get_moments_for_period(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Moment]:
        """Get all moments for a user within a date range"""
        async with get_session() as session:
            result = await session.execute(
                select(Moment)
                .where(
                    and_(
                        Moment.user_id == user_id,
                        Moment.created_at >= start_date,
                        Moment.created_at < end_date,
                    )
                )
                .order_by(Moment.created_at.desc())
            )
            return list(result.scalars().all())

    async def generate_today_summary(
        self,
        telegram_id: int,
    ) -> Optional[str]:
        """
        Generate a summary of user's positive moments for today.
        Uses calendar-based range: today 00:00 to 23:59 in user's timezone.
        """
        start_time = time.time()
        success = True
        error_msg = None
        input_tokens = 0
        output_tokens = 0

        try:
            async with get_session() as session:
                # Get user
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.error(f"User not found: {telegram_id}")
                    return None

                # Calculate today's boundaries using user's timezone (calendar-based)
                date_range = get_today_range(user.timezone)
                start_date = date_range.start_utc
                end_date = date_range.end_utc

                logger.info(
                    f"generate_today_summary: user={telegram_id}, tz={user.timezone}, "
                    f"range={date_range.format_range()}, "
                    f"start_utc={start_date}, end_utc={end_date}"
                )

                # Get moments for the period
                moments = await self.get_moments_for_period(user.id, start_date, end_date)

                if not moments:
                    logger.info(f"No moments found for today's summary for user {telegram_id}")
                    return None

                address = "вы" if user.formal_address else "ты"
                name = user.first_name or "друг"
                gender = user.gender if user.gender else "unknown"
                gender_instruction = get_gender_instruction(gender)

                # Format moments for GPT
                moments_text = "\n".join([
                    f"- {m.content}" for m in moments[:10]
                ])

                # Generate summary with GPT
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": f"""{LANGUAGE_INSTRUCTION}

{PROMPT_PROTECTION}

{gender_instruction}

You are a warm and supportive bot for developing positive thinking.
Create a brief summary of today's good moments.

Summary structure:
1. Warm greeting with name ({name})
2. How many good moments there were today ({len(moments)})
3. Brief highlight of the day's moments
4. Encouraging closing thought

Use appropriate emojis for positivity.
Be brief but warm (maximum 3-4 sentences).

(Russian version):
Ты - теплый и поддерживающий бот для развития позитивного мышления.
Создай краткое саммари сегодняшних хороших моментов.

Структура саммари:
1. Теплое приветствие с именем ({name})
2. Сколько хороших моментов было сегодня ({len(moments)})
3. Краткий обзор моментов дня
4. Ободряющее завершение

Используй обращение на "{address}".
Используй эмодзи для позитива.
Будь кратким, но теплым (максимум 3-4 предложения).

{ABROAD_PHRASE_RULE_RU}

{FORBIDDEN_SYMBOLS_RULE_RU}""",
                        },
                        {
                            "role": "user",
                            "content": f"Here are today's good moments:\n{moments_text}",
                        },
                    ],
                    max_tokens=300,
                    temperature=0.7,
                )

                if response.usage:
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens

                summary = apply_all_filters(response.choices[0].message.content.strip())

                header = format_summary_header(date_range, "today", user.language_code)
                return f"{header}\n\n{summary}"

        except Exception as e:
            logger.error(f"Failed to generate today's summary: {e}")
            success = False
            error_msg = str(e)
            return None

        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            await APIUsageService.log_usage(
                api_provider="openai",
                model=self.model,
                operation_type="today_summary",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                telegram_id=telegram_id,
                success=success,
                error_message=error_msg,
            )

    async def generate_weekly_summary(
        self,
        telegram_id: int,
        use_previous_week: bool = False,
    ) -> Optional[str]:
        """
        Generate a weekly summary of user's positive moments.
        Uses calendar-based range in user's timezone:
        - current week (Mon-Sun) by default
        - previous week (Mon-Sun) when use_previous_week=True
        """
        start_time = time.time()
        success = True
        error_msg = None
        input_tokens = 0
        output_tokens = 0

        try:
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.error(f"User not found: {telegram_id}")
                    return None

                # Calculate week boundaries using user's timezone (calendar-based: Mon-Sun)
                date_range = (
                    get_previous_week_range(user.timezone)
                    if use_previous_week
                    else get_week_range(user.timezone)
                )
                start_date = date_range.start_utc
                end_date = date_range.end_utc

                logger.info(
                    f"generate_weekly_summary: user={telegram_id}, tz={user.timezone}, "
                    f"range={date_range.format_range()}, "
                    f"start_utc={start_date}, end_utc={end_date}"
                )

                moments = await self.get_moments_for_period(user.id, start_date, end_date)

                if not moments:
                    logger.info(f"No moments found for weekly summary for user {telegram_id}")
                    return None

                address = "вы" if user.formal_address else "ты"
                name = user.first_name or "друг"
                gender = user.gender if user.gender else "unknown"
                gender_instruction = get_gender_instruction(gender)

                moments_text = "\n".join([
                    f"- {m.content}" for m in moments[:15]
                ])

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": f"""{LANGUAGE_INSTRUCTION}

{PROMPT_PROTECTION}

{gender_instruction}

You are a warm and supportive bot for developing positive thinking.
Create a brief and inspiring weekly summary of the user's good moments.

Summary structure:
1. Warm greeting with name ({name})
2. How many good moments there were this week ({len(moments)})
3. Main themes of joy (if any)
4. 2-3 brightest moments
5. Inspiring conclusion

Use appropriate emojis for positivity.
Be brief but warm (maximum 5-7 sentences).

(Russian version):
Ты - теплый и поддерживающий бот для развития позитивного мышления.
Создай краткое и вдохновляющее еженедельное саммари хороших моментов пользователя.

Структура саммари:
1. Теплое приветствие с именем ({name})
2. Сколько хороших моментов было за неделю ({len(moments)})
3. Основные темы радости (если есть)
4. 2-3 самых ярких момента
5. Вдохновляющее завершение

Используй обращение на "{address}".
Используй эмодзи для позитива.
Будь кратким, но теплым (максимум 5-7 предложений).

{ABROAD_PHRASE_RULE_RU}

{FORBIDDEN_SYMBOLS_RULE_RU}""",
                        },
                        {
                            "role": "user",
                            "content": f"Here are the good moments for the week:\n{moments_text}",
                        },
                    ],
                    max_tokens=400,
                    temperature=0.7,
                )

                if response.usage:
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens

                summary = apply_all_filters(response.choices[0].message.content.strip())

                header = format_summary_header(date_range, "weekly", user.language_code)
                return f"{header}\n\n{summary}"

        except Exception as e:
            logger.error(f"Failed to generate weekly summary: {e}")
            success = False
            error_msg = str(e)
            return None

        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            await APIUsageService.log_usage(
                api_provider="openai",
                model=self.model,
                operation_type="weekly_summary",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                telegram_id=telegram_id,
                success=success,
                error_message=error_msg,
            )

    async def generate_monthly_summary(
        self,
        telegram_id: int,
    ) -> Optional[str]:
        """
        Generate a monthly summary of user's positive moments.
        Uses calendar-based range: 1st day 00:00 to last day 23:59 in user's timezone.
        """
        start_time = time.time()
        success = True
        error_msg = None
        input_tokens = 0
        output_tokens = 0

        try:
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.error(f"User not found: {telegram_id}")
                    return None

                # Calculate month boundaries using user's timezone (calendar-based)
                date_range = get_month_range(user.timezone)
                start_date = date_range.start_utc
                end_date = date_range.end_utc

                logger.info(
                    f"generate_monthly_summary: user={telegram_id}, tz={user.timezone}, "
                    f"range={date_range.format_range()}, "
                    f"start_utc={start_date}, end_utc={end_date}"
                )

                moments = await self.get_moments_for_period(user.id, start_date, end_date)

                if not moments:
                    logger.info(f"No moments found for monthly summary for user {telegram_id}")
                    return None

                result = await session.execute(
                    select(UserStats).where(UserStats.user_id == user.id)
                )
                stats = result.scalar_one_or_none()

                address = "вы" if user.formal_address else "ты"
                name = user.first_name or "друг"
                gender = user.gender if user.gender else "unknown"
                gender_instruction = get_gender_instruction(gender)

                all_topics = []
                for m in moments:
                    if m.topics:
                        all_topics.extend(m.topics)

                topic_counts = Counter(all_topics)
                top_topics = [topic for topic, _ in topic_counts.most_common(7)]

                sample_moments = moments[:20]
                moments_text = "\n".join([
                    f"- {m.content}" for m in sample_moments
                ])

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": f"""{LANGUAGE_INSTRUCTION}

{PROMPT_PROTECTION}

{gender_instruction}

You are a warm and supportive bot for developing positive thinking.
Create an inspiring monthly summary of the user's good moments.

Summary structure:
1. Celebratory greeting with name ({name}) - this is the month's summary!
2. Statistics: {len(moments)} good moments this month
3. Main themes of joy for the month (what brought joy most often)
4. 3-4 most memorable moments
5. Motivating conclusion with wishes for the next month

Use celebratory emojis.
Make this summary special and inspiring.

(Russian version):
Ты - теплый и поддерживающий бот для развития позитивного мышления.
Создай вдохновляющее месячное саммари хороших моментов пользователя.

Структура саммари:
1. Праздничное приветствие с именем ({name}) - это итог месяца!
2. Статистика: {len(moments)} хороших моментов за месяц
3. Главные темы радости за месяц (что чаще всего радовало)
4. 3-4 самых запоминающихся момента
5. Мотивирующее завершение с пожеланиями на следующий месяц

Используй обращение на "{address}".
Используй эмодзи для праздничного настроения.
Сделай это саммари особенным и вдохновляющим.

{ABROAD_PHRASE_RULE_RU}

{FORBIDDEN_SYMBOLS_RULE_RU}""",
                        },
                        {
                            "role": "user",
                            "content": f"Here are the good moments for the month:\n{moments_text}\n\nMain themes of joy: {', '.join(top_topics) if top_topics else 'various'}",
                        },
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )

                if response.usage:
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens

                summary = apply_all_filters(response.choices[0].message.content.strip())

                streak_text = f"\n🔥 Текущий стрик: {stats.current_streak} дней" if stats and stats.current_streak > 0 else ""
                header = format_summary_header(date_range, "monthly", user.language_code)
                return f"{header}{streak_text}\n\n{summary}"

        except Exception as e:
            logger.error(f"Failed to generate monthly summary: {e}")
            success = False
            error_msg = str(e)
            return None

        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            await APIUsageService.log_usage(
                api_provider="openai",
                model=self.model,
                operation_type="monthly_summary",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                telegram_id=telegram_id,
                success=success,
                error_message=error_msg,
            )
