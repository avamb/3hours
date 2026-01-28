"""
MINDSETHAPPYBOT - Feedback model
Stores user feedback and suggestions for new features
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, Text, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Feedback(Base):
    """Feedback model - stores user feedback and suggestions"""
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'suggestion', 'bug', 'complaint', 'other'
    status: Mapped[str] = mapped_column(String(20), default="new")  # 'new', 'reviewed', 'implemented', 'rejected'
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, user_id={self.user_id}, status={self.status})>"
