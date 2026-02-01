"""
MINDSETHAPPYBOT - Start Event model
Logs each /start command for attribution tracking
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Integer, String, BigInteger, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.db.database import Base

if TYPE_CHECKING:
    from src.db.models.user import User


class StartEvent(Base):
    """Logs each /start event for attribution analytics"""
    __tablename__ = "start_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationship to User
    user: Mapped["User"] = relationship("User", back_populates="start_events")
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    
    # Raw payload exactly as received (or empty/null)
    raw_payload: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Parsed attribution fields
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="unknown", index=True)
    campaign: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    # Indexes for analytics queries
    __table_args__ = (
        Index('idx_start_events_source_created', 'source', 'created_at'),
        Index('idx_start_events_campaign_created', 'campaign', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<StartEvent(id={self.id}, user_id={self.user_id}, source={self.source}, campaign={self.campaign})>"
