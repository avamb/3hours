"""
MINDSETHAPPYBOT - UserStats model
Stores aggregated statistics for each user
"""
from datetime import datetime, date, timezone
from typing import Optional

from sqlalchemy import Integer, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class UserStats(Base):
    """UserStats model - stores user statistics"""
    __tablename__ = "user_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    total_moments: Mapped[int] = mapped_column(Integer, default=0)
    total_questions_sent: Mapped[int] = mapped_column(Integer, default=0)
    total_questions_answered: Mapped[int] = mapped_column(Integer, default=0)
    last_response_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="stats")

    def __repr__(self) -> str:
        return f"<UserStats(user_id={self.user_id}, streak={self.current_streak}, moments={self.total_moments})>"
