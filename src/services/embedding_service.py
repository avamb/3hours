"""
MINDSETHAPPYBOT - Embedding service
Creates vector embeddings using OpenAI API
"""
import logging
from typing import List, Optional

from openai import AsyncOpenAI

from src.config import get_settings

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
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.model,
            )
            embedding = response.data[0].embedding
            logger.debug(f"Created embedding for text: {text[:50]}...")
            return embedding
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            return None

    async def analyze_mood(self, text: str) -> Optional[float]:
        """
        Analyze mood of text using GPT
        Returns score from -1 (very negative) to 1 (very positive)
        """
        try:
            settings = get_settings()
            response = await self.client.chat.completions.create(
                model=settings.openai_chat_model,
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
            score_str = response.choices[0].message.content.strip()
            score = float(score_str)
            return max(-1, min(1, score))  # Clamp to [-1, 1]
        except Exception as e:
            logger.error(f"Failed to analyze mood: {e}")
            return None

    async def extract_topics(self, text: str) -> Optional[List[str]]:
        """
        Extract topics/themes from text using GPT
        Returns list of topic keywords
        """
        try:
            settings = get_settings()
            response = await self.client.chat.completions.create(
                model=settings.openai_chat_model,
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
            topics_str = response.choices[0].message.content.strip()
            topics = [t.strip() for t in topics_str.split(",") if t.strip()]
            return topics[:5]  # Limit to 5 topics
        except Exception as e:
            logger.error(f"Failed to extract topics: {e}")
            return None
