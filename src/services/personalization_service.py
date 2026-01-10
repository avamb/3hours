"""
MINDSETHAPPYBOT - Personalization service
Generates personalized responses using GPT-4 and user history
"""
import logging
from typing import List, Optional

from openai import AsyncOpenAI
from sqlalchemy import select

from src.config import get_settings
from src.db.database import get_session
from src.db.models import User, Moment
from src.utils.text_filters import ABROAD_PHRASE_RULE_RU, replace_abroad_phrases

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Service for generating personalized responses"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_chat_model

    async def generate_response(
        self,
        telegram_id: int,
        moment_content: str,
    ) -> str:
        """
        Generate a personalized positive response to user's moment
        """
        try:
            # Get user for personalization
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

            address = "вы" if (user and user.formal_address) else "ты"

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""Ты — тёплый и поддерживающий бот для развития позитивного мышления.
Пользователь поделился хорошим моментом из своей жизни.
Ответь коротко (1-2 предложения), тепло и поддерживающе.
Используй обращение на «{address}».
Используй подходящие эмодзи для позитива.
Не задавай вопросов, просто поддержи.

{ABROAD_PHRASE_RULE_RU}""",
                    },
                    {
                        "role": "user",
                        "content": f"Мой хороший момент: {moment_content}",
                    },
                ],
                max_tokens=150,
                temperature=0.7,
            )

            return replace_abroad_phrases(response.choices[0].message.content.strip())

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "Спасибо, что поделился! Это действительно здорово! 🌟"

    async def detect_negative_mood(self, text: str) -> bool:
        """
        Detect if user's message indicates negative mood
        """
        negative_patterns = [
            "ничего хорошего",
            "ничего не произошло",
            "плохо",
            "грустно",
            "тоскливо",
            "уныло",
            "ужасно",
            "не знаю",
            "затрудняюсь",
        ]

        text_lower = text.lower()
        for pattern in negative_patterns:
            if pattern in text_lower:
                return True

        # Use GPT for more nuanced detection
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Определи, выражает ли сообщение негативное настроение, грусть или отсутствие позитива. "
                            "Ответь только YES или NO."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=5,
                temperature=0,
            )

            result = response.choices[0].message.content.strip().upper()
            return result == "YES"

        except Exception as e:
            logger.error(f"Mood detection failed: {e}")
            return False

    async def generate_supportive_response(
        self,
        telegram_id: int,
        current_text: str,
        past_moments: List[Moment],
    ) -> str:
        """
        Generate supportive response that reminds about past positive moments
        """
        try:
            # Get user for personalization
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

            address = "вы" if (user and user.formal_address) else "ты"

            # Format past moments
            past_moments_text = "\n".join([
                f"- {m.content[:100]}" for m in past_moments[:3]
            ])

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""Ты — тёплый и эмпатичный бот для развития позитивного мышления.
Пользователь сейчас в негативном настроении. Твоя задача:
1. Проявить понимание и эмпатию
2. Мягко напомнить о прошлых хороших моментах из его истории
3. Дать надежду, что хорошие моменты будут снова

Используй обращение на «{address}».
Будь тёплым, но не навязчивым. Используй подходящие эмодзи.

{ABROAD_PHRASE_RULE_RU}

Прошлые хорошие моменты пользователя:
{past_moments_text}""",
                    },
                    {
                        "role": "user",
                        "content": current_text,
                    },
                ],
                max_tokens=250,
                temperature=0.7,
            )

            return replace_abroad_phrases(response.choices[0].message.content.strip())

        except Exception as e:
            logger.error(f"Failed to generate supportive response: {e}")
            return (
                "Понимаю, бывают такие дни. 💝 "
                "Помни, что раньше у тебя были прекрасные моменты, и они обязательно будут снова."
            )

    async def generate_empathetic_response(
        self,
        telegram_id: int,
        text: str,
    ) -> str:
        """
        Generate empathetic response when no past moments available
        """
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

            address = "вы" if (user and user.formal_address) else "ты"

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""Ты — тёплый и эмпатичный бот для развития позитивного мышления.
Пользователь делится тем, что ему сейчас не очень хорошо.
Прояви понимание и поддержку. Не навязывай позитив.
Используй обращение на «{address}».
Ответь коротко (2-3 предложения), тепло и с эмпатией.

{ABROAD_PHRASE_RULE_RU}""",
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=150,
                temperature=0.7,
            )

            return replace_abroad_phrases(response.choices[0].message.content.strip())

        except Exception as e:
            logger.error(f"Failed to generate empathetic response: {e}")
            return "Понимаю тебя. Бывают разные дни. Я здесь, если захочешь поговорить. 💝"

    async def generate_dialog_response(
        self,
        telegram_id: int,
        message: str,
        context: List[dict] = None,
    ) -> str:
        """
        Generate response for free dialog mode
        """
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

            address = "вы" if (user and user.formal_address) else "ты"

            messages = [
                {
                    "role": "system",
                    "content": f"""Ты — мудрый и эмпатичный собеседник для развития позитивного мышления.
Пользователь хочет поговорить о чём-то. Твои принципы:
1. Слушай и проявляй понимание
2. Давай взгляд со стороны, но НЕ навязывай решения
3. Явно указывай, что решение принимает сам пользователь
4. Будь тёплым и поддерживающим
5. Используй обращение на «{address}»

{ABROAD_PHRASE_RULE_RU}

Помни: ты не психолог и не даёшь профессиональных советов. Ты просто друг, который слушает.""",
                },
            ]

            if context:
                messages.extend(context)

            messages.append({"role": "user", "content": message})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300,
                temperature=0.7,
            )

            return replace_abroad_phrases(response.choices[0].message.content.strip())

        except Exception as e:
            logger.error(f"Failed to generate dialog response: {e}")
            return "Я тебя слышу. Расскажи больше, если хочешь. 💝"
