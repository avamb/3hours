"""
MINDSETHAPPYBOT - Social Profile Service
Manages user social profiles and interest parsing
"""
import logging
import re
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select
from openai import AsyncOpenAI

from src.config import get_settings
from src.db.database import get_session
from src.db.models import User, SocialProfile
from src.services.personalization_service import LANGUAGE_INSTRUCTION

logger = logging.getLogger(__name__)


# Social network URL patterns
SOCIAL_PATTERNS = {
    "instagram": r"(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)",
    "facebook": r"(?:https?://)?(?:www\.)?facebook\.com/([a-zA-Z0-9_.]+)",
    "twitter": r"(?:https?://)?(?:www\.)?(?:twitter|x)\.com/([a-zA-Z0-9_]+)",
    "linkedin": r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)",
    "vk": r"(?:https?://)?(?:www\.)?vk\.com/([a-zA-Z0-9_.]+)",
    "telegram": r"(?:https?://)?(?:t\.me|telegram\.me)/([a-zA-Z0-9_]+)",
    "youtube": r"(?:https?://)?(?:www\.)?youtube\.com/(?:@|c/|channel/|user/)?([a-zA-Z0-9_-]+)",
    "tiktok": r"(?:https?://)?(?:www\.)?tiktok\.com/@([a-zA-Z0-9_.]+)",
}


class SocialProfileService:
    """Service for managing user social profiles"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_analysis_model

    async def get_or_create_profile(self, telegram_id: int) -> Optional[SocialProfile]:
        """Get or create social profile for user"""
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return None

            # Check for existing profile
            result = await session.execute(
                select(SocialProfile).where(SocialProfile.user_id == user.id)
            )
            profile = result.scalar_one_or_none()

            if not profile:
                profile = SocialProfile(user_id=user.id)
                session.add(profile)
                await session.commit()
                await session.refresh(profile)

            return profile

    async def get_profile(self, telegram_id: int) -> Optional[SocialProfile]:
        """Get social profile for user"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return None

            result = await session.execute(
                select(SocialProfile).where(SocialProfile.user_id == user.id)
            )
            return result.scalar_one_or_none()

    def detect_social_network(self, url: str) -> Optional[str]:
        """Detect which social network a URL belongs to"""
        url = url.strip()
        for network, pattern in SOCIAL_PATTERNS.items():
            if re.search(pattern, url, re.IGNORECASE):
                return network
        return None

    def normalize_url(self, url: str, network: str) -> str:
        """Normalize a social network URL"""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    async def add_social_link(
        self,
        telegram_id: int,
        url: str,
    ) -> tuple[bool, str]:
        """
        Add a social network link to user's profile.
        Returns (success, message)
        """
        network = self.detect_social_network(url)
        if not network:
            return False, "Не удалось определить социальную сеть. Поддерживаются: Instagram, Facebook, Twitter/X, LinkedIn, VK, Telegram, YouTube, TikTok"

        normalized_url = self.normalize_url(url, network)

        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False, "Пользователь не найден"

            # Get or create profile
            result = await session.execute(
                select(SocialProfile).where(SocialProfile.user_id == user.id)
            )
            profile = result.scalar_one_or_none()

            if not profile:
                profile = SocialProfile(user_id=user.id)
                session.add(profile)

            # Map network to field
            field_map = {
                "instagram": "instagram_url",
                "facebook": "facebook_url",
                "twitter": "twitter_url",
                "linkedin": "linkedin_url",
                "vk": "vk_url",
                "telegram": "telegram_channel_url",
                "youtube": "youtube_url",
                "tiktok": "tiktok_url",
            }

            field_name = field_map.get(network)
            if field_name:
                setattr(profile, field_name, normalized_url)
                profile.updated_at = datetime.utcnow()
                await session.commit()

                network_names = {
                    "instagram": "Instagram",
                    "facebook": "Facebook",
                    "twitter": "Twitter/X",
                    "linkedin": "LinkedIn",
                    "vk": "ВКонтакте",
                    "telegram": "Telegram",
                    "youtube": "YouTube",
                    "tiktok": "TikTok",
                }
                return True, f"Добавлена ссылка на {network_names.get(network, network)}"

            return False, "Неизвестная ошибка"

    async def remove_social_link(
        self,
        telegram_id: int,
        network: str,
    ) -> tuple[bool, str]:
        """Remove a social network link from user's profile"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False, "Пользователь не найден"

            result = await session.execute(
                select(SocialProfile).where(SocialProfile.user_id == user.id)
            )
            profile = result.scalar_one_or_none()

            if not profile:
                return False, "Профиль не найден"

            field_map = {
                "instagram": "instagram_url",
                "facebook": "facebook_url",
                "twitter": "twitter_url",
                "linkedin": "linkedin_url",
                "vk": "vk_url",
                "telegram": "telegram_channel_url",
                "youtube": "youtube_url",
                "tiktok": "tiktok_url",
            }

            field_name = field_map.get(network.lower())
            if field_name:
                setattr(profile, field_name, None)
                profile.updated_at = datetime.utcnow()
                await session.commit()
                return True, "Ссылка удалена"

            return False, "Неизвестная социальная сеть"

    async def update_bio(
        self,
        telegram_id: int,
        bio_text: str,
    ) -> tuple[bool, str]:
        """Update user's bio text"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False, "Пользователь не найден"

            result = await session.execute(
                select(SocialProfile).where(SocialProfile.user_id == user.id)
            )
            profile = result.scalar_one_or_none()

            if not profile:
                profile = SocialProfile(user_id=user.id)
                session.add(profile)

            profile.bio_text = bio_text
            profile.updated_at = datetime.utcnow()
            await session.commit()

            return True, "Биография обновлена"

    async def parse_interests(self, telegram_id: int) -> tuple[bool, List[str]]:
        """
        Parse interests from user's bio and social links using GPT.
        Returns (success, list of interests)
        """
        profile = await self.get_profile(telegram_id)
        if not profile:
            return False, []

        # Collect all available info
        info_parts = []
        if profile.bio_text:
            info_parts.append(f"Биография: {profile.bio_text}")

        urls = profile.get_all_urls()
        active_networks = [k for k, v in urls.items() if v]
        if active_networks:
            info_parts.append(f"Социальные сети: {', '.join(active_networks)}")

        if not info_parts:
            return False, []

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""{LANGUAGE_INSTRUCTION}

You analyze the user's profile and determine their interests.
Based on the biography and social networks, identify 3-7 main interests.
Reply only with a comma-separated list of interests, without numbering or explanations.
Example: music, travel, photography, sports, books

(Russian version / Русская версия):
Ты анализируешь профиль пользователя и определяешь его интересы.
На основе биографии и социальных сетей определи 3-7 основных интересов.
Ответь только списком интересов через запятую, без нумерации и пояснений.
Например: музыка, путешествия, фотография, спорт, книги""",
                    },
                    {
                        "role": "user",
                        "content": "\n".join(info_parts),
                    },
                ],
                max_tokens=100,
                temperature=0.5,
            )

            interests_text = response.choices[0].message.content.strip()
            interests = [i.strip() for i in interests_text.split(",") if i.strip()]

            # Save parsed interests
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()

                if user:
                    result = await session.execute(
                        select(SocialProfile).where(SocialProfile.user_id == user.id)
                    )
                    profile = result.scalar_one_or_none()

                    if profile:
                        profile.interests = interests
                        profile.last_parsed_at = datetime.utcnow()
                        await session.commit()

            return True, interests

        except Exception as e:
            logger.error(f"Failed to parse interests: {e}")
            return False, []

    async def get_profile_summary(self, telegram_id: int) -> str:
        """Get a formatted summary of user's social profile"""
        profile = await self.get_profile(telegram_id)

        if not profile:
            return "Социальный профиль не настроен"

        lines = []

        # Social links
        urls = profile.get_all_urls()
        network_names = {
            "instagram": "Instagram",
            "facebook": "Facebook",
            "twitter": "Twitter/X",
            "linkedin": "LinkedIn",
            "vk": "ВКонтакте",
            "telegram_channel": "Telegram канал",
            "youtube": "YouTube",
            "tiktok": "TikTok",
        }

        active_links = [(network_names.get(k, k), v) for k, v in urls.items() if v]
        if active_links:
            lines.append("<b>Социальные сети:</b>")
            for name, url in active_links:
                lines.append(f"  • {name}")

        # Bio
        if profile.bio_text:
            lines.append(f"\n<b>О себе:</b>\n{profile.bio_text[:200]}{'...' if len(profile.bio_text) > 200 else ''}")

        # Interests
        if profile.interests:
            lines.append(f"\n<b>Интересы:</b> {', '.join(profile.interests)}")

        if not lines:
            return "Социальный профиль пуст. Добавьте ссылки на соцсети или биографию."

        return "\n".join(lines)
