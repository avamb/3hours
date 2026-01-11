"""
MINDSETHAPPYBOT - Speech-to-text service
Transcribes voice messages using OpenAI Whisper API
"""
import logging
import tempfile
import os
from typing import Optional

from aiogram import Bot
from openai import AsyncOpenAI
import aiofiles
import aiohttp

from src.config import get_settings

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
    ) -> Optional[str]:
        """
        Download voice file and transcribe using Whisper API

        Args:
            bot: Telegram bot instance
            file_path: Telegram file path (from file.file_path)

        Returns:
            Transcribed text or None if failed
        """
        temp_file = None

        try:
            # Build download URL from file path
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

            # Download to temp file
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download voice: HTTP {response.status}")
                        return None

                    # Create temp file with .ogg extension
                    temp_file = tempfile.NamedTemporaryFile(
                        suffix=".ogg",
                        delete=False,
                    )

                    async with aiofiles.open(temp_file.name, "wb") as f:
                        await f.write(await response.read())

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
            return None

        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")
