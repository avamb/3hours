"""
MINDSETHAPPYBOT - Moment model
Stores user's positive moments with vector embeddings
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Integer, String, Text, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from src.db.database import Base


class Moment(Base):
    """Moment model - stores user's positive moments with embeddings"""
    __tablename__ = "moments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), default="text")  # 'text' or 'voice'
    original_voice_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    embedding = mapped_column(Vector(1536), nullable=True)  # OpenAI text-embedding-3-small dimension
    mood_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # -1 to 1
    topics: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="moments")

    def __repr__(self) -> str:
        return f"<Moment(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"
