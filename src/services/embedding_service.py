"""
MINDSETHAPPYBOT - Embedding service
Creates vector embeddings using OpenAI API
"""
import logging
import time
from typing import List, Optional

from openai import AsyncOpenAI

from src.config import get_settings
from src.services.api_usage_service import APIUsageService

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for creating and managing embeddings"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model

    async def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Create embedding vector for text using OpenAI API
        Returns 1536-dimensional vector for text-embedding-3-small
        """
        start_time = time.time()
        success = True
        error_msg = None
        input_tokens = 0

        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.model,
            )

            # Extract token usage (embeddings only have input tokens)
            if response.usage:
                input_tokens = response.usage.total_tokens

            embedding = response.data[0].embedding
            logger.debug(f"Created embedding for text: {text[:50]}...")
            return embedding
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            success = False
            error_msg = str(e)
            return None

        finally:
            # Log API usage
            duration_ms = int((time.time() - start_time) * 1000)
            await APIUsageService.log_usage(
                api_provider="openai",
                model=self.model,
                operation_type="embedding",
                input_tokens=input_tokens,
                output_tokens=0,
                duration_ms=duration_ms,
                success=success,
                error_message=error_msg,
            )

    async def analyze_mood(self, text: str) -> Optional[float]:
        """
        Analyze mood of text using GPT
        Returns score from -1 (very negative) to 1 (very positive)
        """
        start_time = time.time()
        success = True
        error_msg = None
        input_tokens = 0
        output_tokens = 0

        try:
            settings = get_settings()
            response = await self.client.chat.completions.create(
                model=settings.openai_analysis_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a mood analyzer. Analyze the emotional tone of the text "
                            "and return ONLY a number between -1 and 1, where:\n"
                            "-1 = very negative\n"
                            "0 = neutral\n"
                            "1 = very positive\n"
                            "Return only the number, nothing else."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=10,
                temperature=0,
            )

            # Extract token usage
            if response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            score_str = response.choices[0].message.content.strip()
            score = float(score_str)
            return max(-1, min(1, score))  # Clamp to [-1, 1]
        except Exception as e:
            logger.error(f"Failed to analyze mood: {e}")
            success = False
            error_msg = str(e)
            return None

        finally:
            # Log API usage
            duration_ms = int((time.time() - start_time) * 1000)
            settings = get_settings()
            await APIUsageService.log_usage(
                api_provider="openai",
                model=settings.openai_analysis_model,
                operation_type="mood_analysis",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                success=success,
                error_message=error_msg,
            )

    async def extract_topics(self, text: str) -> Optional[List[str]]:
        """
        Extract topics/themes from text using GPT
        Returns list of topic keywords
        """
        start_time = time.time()
        success = True
        error_msg = None
        input_tokens = 0
        output_tokens = 0

        try:
            settings = get_settings()
            response = await self.client.chat.completions.create(
                model=settings.openai_analysis_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract 1-5 main topics/themes from the text. "
                            "Return them as a comma-separated list of keywords in the same language as the text. "
                            "Example: семья, ужин, праздник"
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=100,
                temperature=0,
            )

            # Extract token usage
            if response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            topics_str = response.choices[0].message.content.strip()
            topics = [t.strip() for t in topics_str.split(",") if t.strip()]
            return topics[:5]  # Limit to 5 topics
        except Exception as e:
            logger.error(f"Failed to extract topics: {e}")
            success = False
            error_msg = str(e)
            return None

        finally:
            # Log API usage
            duration_ms = int((time.time() - start_time) * 1000)
            settings = get_settings()
            await APIUsageService.log_usage(
                api_provider="openai",
                model=settings.openai_analysis_model,
                operation_type="topic_extraction",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                success=success,
                error_message=error_msg,
            )
