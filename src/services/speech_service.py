"""
MINDSETHAPPYBOT - Speech-to-text service
Transcribes voice messages using OpenAI Whisper API
"""
import logging
import tempfile
import time
from typing import Optional, Tuple

from aiogram import Bot
from openai import AsyncOpenAI
import aiofiles
import aiohttp

from src.config import get_settings
from src.services.api_usage_service import APIUsageService

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """Service for transcribing voice messages"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def transcribe_voice(
        self,
        bot: Bot,
        file_path: str,
        telegram_id: int = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Download voice file and transcribe using Whisper API.
        Auto-detects the language of the voice message.

        Args:
            bot: Telegram bot instance
            file_path: Telegram file path (from file.file_path)
            telegram_id: Optional Telegram user ID for tracking

        Returns:
            Tuple of (transcribed_text, detected_language_code) or (None, None) if failed
            Language code is ISO 639-1 format (e.g., "ru", "en", "uk")
        """
        start_time = time.time()
        success = True
        error_msg = None
        # Whisper pricing is per minute, but we estimate based on file size
        # The API doesn't return token counts, so we use duration estimation

        # Use context manager for automatic cleanup
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=True) as temp_file:
            try:
                # Build download URL from file path
                file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

                # Download to temp file
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_url) as response:
                        if response.status != 200:
                            logger.error(f"Failed to download voice: HTTP {response.status}")
                            success = False
                            error_msg = f"HTTP {response.status}"
                            return None, None

                        file_content = await response.read()
                        async with aiofiles.open(temp_file.name, "wb") as f:
                            await f.write(file_content)

                # Transcribe using Whisper with auto-language detection
                # Using verbose_json response format to get the detected language
                with open(temp_file.name, "rb") as audio_file:
                    transcript = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        # No language parameter - let Whisper auto-detect
                    )

                # Extract detected language from response
                detected_language = getattr(transcript, 'language', None)
                transcribed_text = transcript.text

                # Map Whisper language names to ISO codes if needed
                language_map = {
                    'russian': 'ru',
                    'english': 'en',
                    'ukrainian': 'uk',
                    'spanish': 'es',
                    'german': 'de',
                    'french': 'fr',
                    'italian': 'it',
                    'portuguese': 'pt',
                    'chinese': 'zh',
                    'japanese': 'ja',
                    'korean': 'ko',
                }

                # Normalize the detected language to ISO code
                if detected_language:
                    detected_language = detected_language.lower()
                    # If it's already a 2-letter code, use it
                    if len(detected_language) == 2:
                        lang_code = detected_language
                    else:
                        # Try to map from full name to code
                        lang_code = language_map.get(detected_language, detected_language[:2] if len(detected_language) >= 2 else 'ru')
                else:
                    lang_code = 'ru'  # Fallback to Russian

                logger.info(f"Transcribed voice (lang={lang_code}): {transcribed_text[:50]}...")
                return transcribed_text, lang_code

            except Exception as e:
                logger.error(f"Voice transcription failed: {e}", exc_info=True)
                success = False
                error_msg = str(e)
                return None, None

            finally:
                # Log API usage
                # Whisper pricing is $0.006/minute, we log as a single request
                # with duration converted to estimate tokens (approx 150 tokens/sec for speech)
                duration_ms = int((time.time() - start_time) * 1000)
                await APIUsageService.log_usage(
                    api_provider="openai",
                    model="whisper-1",
                    operation_type="transcription",
                    input_tokens=0,  # Whisper doesn't use token counts
                    output_tokens=0,
                    duration_ms=duration_ms,
                    telegram_id=telegram_id,
                    success=success,
                    error_message=error_msg,
                )
