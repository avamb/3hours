"""
MINDSETHAPPYBOT - Social Profile model
Stores user's social network profiles and parsed interests
"""
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class SocialProfile(Base):
    """Social profile model - stores user's social network links and interests"""
    __tablename__ = "social_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Social network URLs
    instagram_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    facebook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    twitter_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    vk_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    telegram_channel_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    youtube_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tiktok_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Bio and interests
    bio_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interests: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    communication_style: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Timestamps
    last_parsed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    user = relationship("User", back_populates="social_profile")

    def __repr__(self) -> str:
        return f"<SocialProfile(id={self.id}, user_id={self.user_id})>"

    def get_all_urls(self) -> dict:
        """Get all social network URLs as a dictionary"""
        return {
            "instagram": self.instagram_url,
            "facebook": self.facebook_url,
            "twitter": self.twitter_url,
            "linkedin": self.linkedin_url,
            "vk": self.vk_url,
            "telegram_channel": self.telegram_channel_url,
            "youtube": self.youtube_url,
            "tiktok": self.tiktok_url,
        }

    def has_any_url(self) -> bool:
        """Check if any social URL is set"""
        urls = self.get_all_urls()
        return any(url for url in urls.values())
