"""
MINDSETHAPPYBOT - Summary service
Generates weekly and monthly summaries of user's positive moments
"""
import logging
import time
from typing import Optional, List
from datetime import datetime, timedelta
from collections import Counter

from openai import AsyncOpenAI
from sqlalchemy import select, func, and_

from src.config import get_settings
from src.db.database import get_session
from src.db.models import User, Moment, UserStats
from src.utils.text_filters import (
    ABROAD_PHRASE_RULE_RU,
    FORBIDDEN_SYMBOLS_RULE_RU,
    apply_all_filters,
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

    async def generate_weekly_summary(
        self,
        telegram_id: int,
    ) -> Optional[str]:
        """
        Generate a weekly summary of user's positive moments
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

                # Calculate week boundaries (last 7 days)
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=7)

                # Get moments for the period
                moments = await self.get_moments_for_period(user.id, start_date, end_date)

                if not moments:
                    return None

                # Get user stats
                result = await session.execute(
                    select(UserStats).where(UserStats.user_id == user.id)
                )
                stats = result.scalar_one_or_none()

                address = "вы" if user.formal_address else "ты"
                name = user.first_name or "друг"
                gender = user.gender if user.gender else "unknown"
                gender_instruction = get_gender_instruction(gender)

                # Collect topics from moments
                all_topics = []
                for m in moments:
                    if m.topics:
                        all_topics.extend(m.topics)

                # Get most common topics
                topic_counts = Counter(all_topics)
                top_topics = [topic for topic, _ in topic_counts.most_common(5)]

                # Format moments for GPT
                moments_text = "\n".join([
                    f"- {m.content}" for m in moments[:15]  # Limit to 15 most recent
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
Create a brief and inspiring weekly summary of the user's good moments.

Summary structure:
1. Warm greeting with name ({name})
2. How many good moments there were this week ({len(moments)})
3. Main themes of joy (if any)
4. 2-3 brightest moments
5. Inspiring conclusion

Use appropriate emojis for positivity.
Be brief but warm (maximum 5-7 sentences).

(Russian version / Русская версия):
Ты — тёплый и поддерживающий бот для развития позитивного мышления.
Создай краткое и вдохновляющее еженедельное саммари хороших моментов пользователя.

Структура саммари:
1. Тёплое приветствие с именем ({name})
2. Сколько хороших моментов было за неделю ({len(moments)})
3. Основные темы радости (если есть)
4. 2-3 самых ярких момента
5. Вдохновляющее завершение

Используй обращение на «{address}».
Используй эмодзи для позитива.
Будь кратким, но тёплым (максимум 5-7 предложений).

{ABROAD_PHRASE_RULE_RU}

{FORBIDDEN_SYMBOLS_RULE_RU}""",
                        },
                        {
                            "role": "user",
                            "content": f"Here are the good moments for the week / Вот хорошие моменты за неделю:\n{moments_text}",
                        },
                    ],
                    max_tokens=400,
                    temperature=0.7,
                )

                # Extract token usage
                if response.usage:
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens

                summary = apply_all_filters(response.choices[0].message.content.strip())

                # Add header
                header = "📅 Еженедельное саммари\n\n"
                return header + summary

        except Exception as e:
            logger.error(f"Failed to generate weekly summary: {e}")
            success = False
            error_msg = str(e)
            return None

        finally:
            # Log API usage
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
        Generate a monthly summary of user's positive moments
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

                # Calculate month boundaries (last 30 days)
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)

                # Get moments for the period
                moments = await self.get_moments_for_period(user.id, start_date, end_date)

                if not moments:
                    return None

                # Get user stats
                result = await session.execute(
                    select(UserStats).where(UserStats.user_id == user.id)
                )
                stats = result.scalar_one_or_none()

                address = "вы" if user.formal_address else "ты"
                name = user.first_name or "друг"
                gender = user.gender if user.gender else "unknown"
                gender_instruction = get_gender_instruction(gender)

                # Collect topics from moments
                all_topics = []
                for m in moments:
                    if m.topics:
                        all_topics.extend(m.topics)

                # Get most common topics
                topic_counts = Counter(all_topics)
                top_topics = [topic for topic, _ in topic_counts.most_common(7)]

                # Calculate average mood if available
                moods = [m.mood_score for m in moments if m.mood_score is not None]
                avg_mood = sum(moods) / len(moods) if moods else None

                # Format moments for GPT (sample representative moments)
                # Take first 5, last 5, and 5 random from middle
                sample_moments = moments[:20]  # Limit to 20 moments for context
                moments_text = "\n".join([
                    f"- {m.content}" for m in sample_moments
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
Create an inspiring monthly summary of the user's good moments.

Summary structure:
1. Celebratory greeting with name ({name}) - this is the month's summary!
2. Statistics: {len(moments)} good moments this month
3. Main themes of joy for the month (what brought joy most often)
4. 3-4 most memorable moments
5. Motivating conclusion with wishes for the next month

Use celebratory emojis.
Make this summary special and inspiring.

(Russian version / Русская версия):
Ты — тёплый и поддерживающий бот для развития позитивного мышления.
Создай вдохновляющее месячное саммари хороших моментов пользователя.

Структура саммари:
1. Праздничное приветствие с именем ({name}) - это итог месяца!
2. Статистика: {len(moments)} хороших моментов за месяц
3. Главные темы радости за месяц (что чаще всего радовало)
4. 3-4 самых запоминающихся момента
5. Мотивирующее завершение с пожеланиями на следующий месяц

Используй обращение на «{address}».
Используй эмодзи для праздничного настроения.
Сделай это саммари особенным и вдохновляющим.

{ABROAD_PHRASE_RULE_RU}

{FORBIDDEN_SYMBOLS_RULE_RU}""",
                        },
                        {
                            "role": "user",
                            "content": f"Here are the good moments for the month / Вот хорошие моменты за месяц:\n{moments_text}\n\nMain themes of joy / Основные темы радости: {', '.join(top_topics) if top_topics else 'various/разнообразные'}",
                        },
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )

                # Extract token usage
                if response.usage:
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens

                summary = apply_all_filters(response.choices[0].message.content.strip())

                # Add header with stats
                streak_text = f"🔥 Текущий стрик: {stats.current_streak} дней" if stats and stats.current_streak > 0 else ""
                header = f"🗓 Месячное саммари\n{streak_text}\n\n" if streak_text else "🗓 Месячное саммари\n\n"
                return header + summary

        except Exception as e:
            logger.error(f"Failed to generate monthly summary: {e}")
            success = False
            error_msg = str(e)
            return None

        finally:
            # Log API usage
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
