"""
MINDSETHAPPYBOT - User model
Stores Telegram user information and settings
"""
from datetime import datetime, time, timezone
from typing import Optional

from sqlalchemy import BigInteger, Boolean, String, Time, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class User(Base):
    """User model - stores Telegram user info and preferences"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="unknown")  # male, female, unknown
    language_code: Mapped[str] = mapped_column(String(10), default="ru")
    formal_address: Mapped[bool] = mapped_column(Boolean, default=False)  # True = вы, False = ты
    active_hours_start: Mapped[time] = mapped_column(Time, default=time(9, 0))
    active_hours_end: Mapped[time] = mapped_column(Time, default=time(21, 0))
    notification_interval_hours: Mapped[int] = mapped_column(Integer, default=3)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    notifications_paused_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    is_in_dialog: Mapped[bool] = mapped_column(Boolean, default=False)  # Track dialog state in DB

    # Tracking field for incremental memory indexing
    last_memory_indexed_conversation_id: Mapped[int] = mapped_column(Integer, default=0)

    # Track last pending scheduled prompt for deletion (prevents message accumulation)
    last_pending_prompt_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, default=None)

    # Attribution tracking (first-touch)
    first_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default=None)
    first_campaign: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default=None)
    first_start_payload: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, default=None)
    first_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    # Attribution tracking (last-touch)
    last_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default=None)
    last_campaign: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default=None)
    last_start_payload: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, default=None)
    last_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    # Relationships
    moments = relationship("Moment", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan")
    scheduled_notifications = relationship("ScheduledNotification", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    social_profile = relationship("SocialProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    conversation_memories = relationship("ConversationMemory", back_populates="user", cascade="all, delete-orphan")
    start_events = relationship("StartEvent", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
