"""
MINDSETHAPPYBOT - Speech-to-text service
Transcribes voice messages using OpenAI Whisper API
"""
import logging
import tempfile
import os
import time
from typing import Optional

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
    ) -> Optional[str]:
        """
        Download voice file and transcribe using Whisper API

        Args:
            bot: Telegram bot instance
            file_path: Telegram file path (from file.file_path)
            telegram_id: Optional Telegram user ID for tracking

        Returns:
            Transcribed text or None if failed
        """
        temp_file = None
        start_time = time.time()
        success = True
        error_msg = None
        # Whisper pricing is per minute, but we estimate based on file size
        # The API doesn't return token counts, so we use duration estimation

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
                        return None

                    # Create temp file with .ogg extension
                    temp_file = tempfile.NamedTemporaryFile(
                        suffix=".ogg",
                        delete=False,
                    )

                    file_content = await response.read()
                    async with aiofiles.open(temp_file.name, "wb") as f:
                        await f.write(file_content)

            # Transcribe using Whisper
            with open(temp_file.name, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru",  # Default to Russian, could be auto-detected
                )

            logger.info(f"Transcribed voice: {transcript.text[:50]}...")
            return transcript.text

        except Exception as e:
            logger.error(f"Voice transcription failed: {e}")
            success = False
            error_msg = str(e)
            return None

        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")

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
