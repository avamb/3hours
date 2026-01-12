"""
MINDSETHAPPYBOT - Configuration module
Loads and validates environment variables using pydantic-settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Telegram Bot Configuration
    telegram_bot_token: str = Field(..., description="Telegram Bot Token from @BotFather")

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API Key")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model"
    )
    openai_chat_model: str = Field(
        default="gpt-4o",
        description="OpenAI chat completion model (user-facing responses)"
    )
    openai_analysis_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model for cheap classification/extraction (non user-facing)"
    )

    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/mindsethappybot",
        description="PostgreSQL connection URL"
    )

    # Application Settings
    default_timezone: str = Field(default="UTC", description="Default timezone for users")
    log_level: str = Field(default="INFO", description="Logging level")

    # Notification Settings
    default_notification_interval_hours: int = Field(
        default=3,
        description="Default interval between questions in hours"
    )
    default_active_hours_start: str = Field(
        default="09:00",
        description="Default active hours start time"
    )
    default_active_hours_end: str = Field(
        default="21:00",
        description="Default active hours end time"
    )

    # Vector Search Settings
    vector_similarity_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for vector search results"
    )
    max_similar_moments: int = Field(
        default=5,
        description="Maximum number of similar moments to retrieve"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
