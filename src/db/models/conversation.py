"""
MINDSETHAPPYBOT - Conversation model
Stores all conversation messages for context
"""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Conversation(Base):
    """Conversation model - stores all messages for context"""
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: 'bot_question', 'user_response', 'free_dialog', 'bot_reply'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="conversations")

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id}, type={self.message_type})>"
