"""
MINDSETHAPPYBOT - API Usage model
Tracks token usage and costs for all API calls
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from sqlalchemy import Integer, String, Text, DateTime, Boolean, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class APIUsage(Base):
    """API Usage model - tracks token usage and costs"""
    __tablename__ = "api_usage"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # API details
    api_provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # openai, whisper, etc.
    model: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # gpt-4o-mini, whisper-1, etc.
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # chat, transcription, embedding, etc.

    # Token usage
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)

    # Cost tracking
    cost_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=10, scale=6), nullable=True, default=0)

    # Performance metrics
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Additional data
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    user = relationship("User", backref="api_usage")

    def __repr__(self) -> str:
        return f"<APIUsage(id={self.id}, provider={self.api_provider}, model={self.model}, tokens={self.total_tokens})>"
