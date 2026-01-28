"""
MINDSETHAPPYBOT - ScheduledNotification model
Stores scheduled question notifications
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class ScheduledNotification(Base):
    """ScheduledNotification model - stores scheduled notifications"""
    __tablename__ = "scheduled_notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    question_template_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="scheduled_notifications")

    def __repr__(self) -> str:
        return f"<ScheduledNotification(id={self.id}, user_id={self.user_id}, time={self.scheduled_time})>"
