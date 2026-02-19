"""
MINDSETHAPPYBOT - Social Profile Service
Manages user social profiles and interest parsing
"""
import logging
import re
import aiohttp
from typing import Optional, List, Tuple
from datetime import datetime, timezone

from sqlalchemy import select
from openai import AsyncOpenAI

from src.config import get_settings
from src.db.database import get_session
from src.db.models import User, SocialProfile
from src.services.personalization_service import LANGUAGE_INSTRUCTION
from src.utils.localization import get_system_message, get_language_code

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

    async def attempt_parse_profile_data(self, url: str, network: str) -> Tuple[bool, Optional[str]]:
        """
        Attempt to fetch and parse profile data from a social network URL.

        Due to social network API restrictions and anti-scraping measures,
        this will typically fail for most profiles. When it fails, we return
        False to indicate that the profile data couldn't be parsed.

        Args:
            url: The social network profile URL
            network: The detected social network name

        Returns:
            Tuple of (success, parsed_data_or_None)
        """
        import asyncio

        try:
            # Attempt to fetch basic page info
            # Note: Most social networks block scraping, so this will usually fail
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status != 200:
                        logger.info(f"Social profile fetch failed for {network}: HTTP {response.status}")
                        return False, None

                    # Even if we get a 200 response, social networks typically return
                    # login pages or limited data for non-authenticated requests
                    content = await response.text()

                    # Check for common indicators that we got a login/blocked page
                    blocked_indicators = [
                        "login", "sign in", "log in", "войти", "вход",
                        "not available", "page not found", "access denied"
                    ]
                    content_lower = content.lower()

                    for indicator in blocked_indicators:
                        if indicator in content_lower[:5000]:  # Check first 5KB
                            logger.info(f"Social profile parsing blocked for {network}: login/access page detected")
                            return False, None

                    # Even with content, we can't reliably extract profile data
                    # without proper API access, so we return failure
                    logger.info(f"Social profile data extraction not supported for {network}")
                    return False, None

        except aiohttp.ClientError as e:
            logger.info(f"Network error fetching social profile for {network}: {e}")
            return False, None
        except asyncio.TimeoutError:
            logger.info(f"Timeout fetching social profile for {network}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error parsing social profile for {network}: {e}")
            return False, None

    async def add_social_link(
        self,
        telegram_id: int,
        url: str,
        language_code: str = "ru",
        formal: bool = False,
    ) -> Tuple[bool, str, bool]:
        """
        Add a social network link to user's profile and attempt to parse profile data.

        Returns:
            Tuple of (success, message, profile_parse_failed)
            - success: True if the link was saved successfully
            - message: Status message (localization key or direct message)
            - profile_parse_failed: True if we attempted to parse profile data but failed
        """
        network = self.detect_social_network(url)
        if not network:
            lang = get_language_code(language_code)
            error_msg = get_system_message("unknown_social_network", lang, formal=formal)
            return False, error_msg, False

        normalized_url = self.normalize_url(url, network)

        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                lang = get_language_code(language_code)
                error_msg = get_system_message("user_not_found", lang, formal=formal)
                return False, error_msg, False

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
                profile.updated_at = datetime.now(timezone.utc)
                await session.commit()

                network_names = {
                    "instagram": "Instagram",
                    "facebook": "Facebook",
                    "twitter": "Twitter/X",
                    "linkedin": "LinkedIn",
                    "vk": "VKontakte",
                    "telegram": "Telegram",
                    "youtube": "YouTube",
                    "tiktok": "TikTok",
                }

                # Attempt to parse profile data from the social network
                parse_success, parsed_data = await self.attempt_parse_profile_data(normalized_url, network)

                # If parsing failed, we still saved the link but couldn't get profile data
                profile_parse_failed = not parse_success

                # Get localized message
                lang = get_language_code(language_code)
                network_name = network_names.get(network, network)
                success_msg = get_system_message("social_link_added", lang, formal=formal, network=network_name)

                return True, success_msg, profile_parse_failed

            lang = get_language_code(language_code)
            error_msg = get_system_message("unknown_error", lang, formal=formal)
            return False, error_msg, False

    async def remove_social_link(
        self,
        telegram_id: int,
        network: str,
        language_code: str = "ru",
        formal: bool = False,
    ) -> tuple[bool, str]:
        """Remove a social network link from user's profile"""
        lang = get_language_code(language_code)
        
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                error_msg = get_system_message("user_not_found", lang, formal=formal)
                return False, error_msg

            result = await session.execute(
                select(SocialProfile).where(SocialProfile.user_id == user.id)
            )
            profile = result.scalar_one_or_none()

            if not profile:
                error_msg = get_system_message("profile_not_found", lang, formal=formal)
                return False, error_msg

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
                profile.updated_at = datetime.now(timezone.utc)
                await session.commit()
                success_msg = get_system_message("social_link_removed", lang, formal=formal)
                return True, success_msg

            error_msg = get_system_message("unknown_social_network", lang, formal=formal)
            return False, error_msg

    async def update_bio(
        self,
        telegram_id: int,
        bio_text: str,
        language_code: str = "ru",
        formal: bool = False,
    ) -> tuple[bool, str]:
        """Update user's bio text"""
        lang = get_language_code(language_code)
        
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                error_msg = get_system_message("user_not_found", lang, formal=formal)
                return False, error_msg

            result = await session.execute(
                select(SocialProfile).where(SocialProfile.user_id == user.id)
            )
            profile = result.scalar_one_or_none()

            if not profile:
                profile = SocialProfile(user_id=user.id)
                session.add(profile)

            profile.bio_text = bio_text
            profile.updated_at = datetime.now(timezone.utc)
            await session.commit()

            success_msg = get_system_message("social_bio_updated", lang, formal=formal)
            return True, success_msg

    async def parse_interests(self, telegram_id: int, language_code: str = "ru") -> tuple[bool, List[str]]:
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
            info_parts.append(f"Biography: {profile.bio_text}")

        urls = profile.get_all_urls()
        active_networks = [k for k, v in urls.items() if v]
        if active_networks:
            info_parts.append(f"Social networks: {', '.join(active_networks)}")

        if not info_parts:
            return False, []

        # Get language name for prompt
        lang = get_language_code(language_code)
        language_names = {
            "ru": "Russian",
            "en": "English",
            "uk": "Ukrainian",
            "es": "Spanish",
            "de": "German",
            "fr": "French",
            "pt": "Portuguese",
            "it": "Italian",
            "he": "Hebrew",
            "zh": "Chinese",
            "ja": "Japanese",
        }
        lang_name = language_names.get(lang, "English")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""{LANGUAGE_INSTRUCTION}

⚠️ CRITICAL: You MUST respond ONLY in {lang_name} language. ⚠️

You analyze the user's profile and determine their interests.
Based on the biography and social networks, identify 3-7 main interests.
Reply ONLY with a comma-separated list of interests in {lang_name}, without numbering or explanations.

Examples for different languages:
- English: music, travel, photography, sports, books
- Russian: музыка, путешествия, фотография, спорт, книги
- Ukrainian: музика, подорожі, фотографія, спорт, книги
- Spanish: música, viajes, fotografía, deportes, libros
- German: Musik, Reisen, Fotografie, Sport, Bücher
- French: musique, voyage, photographie, sport, livres
- Portuguese: música, viagens, fotografia, esportes, livros
- Italian: musica, viaggi, fotografia, sport, libri
- Hebrew: מוזיקה, נסיעות, צילום, ספורט, ספרים
- Chinese: 音乐, 旅行, 摄影, 运动, 书籍
- Japanese: 音楽, 旅行, 写真, スポーツ, 本

IMPORTANT: The user's language is {lang_name}. Return interests ONLY in {lang_name}.""",
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
                        profile.last_parsed_at = datetime.now(timezone.utc)
                        await session.commit()

            return True, interests

        except Exception as e:
            logger.error(f"Failed to parse interests: {e}")
            return False, []

    async def get_profile_summary(self, telegram_id: int, language_code: str = "ru", formal: bool = False) -> str:
        """Get a formatted summary of user's social profile"""
        lang = get_language_code(language_code)
        profile = await self.get_profile(telegram_id)

        if not profile:
            return get_system_message("social_profile_not_configured", lang, formal=formal)

        lines = []

        # Social links
        urls = profile.get_all_urls()
        network_names = {
            "instagram": "Instagram",
            "facebook": "Facebook",
            "twitter": "Twitter/X",
            "linkedin": "LinkedIn",
            "vk": "VKontakte",
            "telegram_channel": "Telegram channel",
            "youtube": "YouTube",
            "tiktok": "TikTok",
        }

        active_links = [(network_names.get(k, k), v) for k, v in urls.items() if v]
        if active_links:
            networks_label = get_system_message("social_networks_label", lang, formal=formal)
            lines.append(networks_label)
            for name, url in active_links:
                lines.append(f"  • {name}")

        # Bio
        if profile.bio_text:
            about_label = get_system_message("about_me_label", lang, formal=formal)
            lines.append(f"\n{about_label}\n{profile.bio_text[:200]}{'...' if len(profile.bio_text) > 200 else ''}")

        # Interests
        if profile.interests:
            interests_label = get_system_message("interests_label", lang, formal=formal)
            lines.append(f"\n{interests_label} {', '.join(profile.interests)}")

        if not lines:
            return get_system_message("social_profile_empty", lang, formal=formal)

        return "\n".join(lines)
