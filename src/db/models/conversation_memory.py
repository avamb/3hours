"""
MINDSETHAPPYBOT - Conversation Memory model
Stores extracted memory-worthy facts from user conversations.
Used for per-user isolated vector memory retrieval.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import Integer, String, Text, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from src.db.database import Base


class ConversationMemory(Base):
    """
    Conversation Memory model - stores extracted facts from user dialogs.

    This table stores "memory-worthy" content extracted from user conversations:
    - Facts about the user's life
    - People the user mentions
    - Preferences and plans
    - Achievements and projects

    Key features:
    - Strict user isolation via user_id FK
    - Deduplication via fingerprint unique constraint
    - Vector search via pgvector embedding
    - Traceability via source_conversation_ids
    """
    __tablename__ = "conversation_memories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Source tracking for traceability
    source_conversation_ids: Mapped[List[int]] = mapped_column(
        ARRAY(Integer),
        nullable=False,
        default=[]
    )

    # The extracted memory content (canonical form)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Vector embedding for similarity search
    embedding = mapped_column(Vector(1536), nullable=True)

    # Memory classification
    # Types: fact, preference, person, project, plan, constraint, achievement, event
    kind: Mapped[str] = mapped_column(String(50), default="fact", nullable=False)

    # Importance score for boosting (1.0 = normal, higher = more important)
    importance: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Fingerprint for deduplication (hash of normalized content)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Additional metadata
    # Can include: lang, confidence, expires_at, original_text_snippet
    memory_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        default={}
    )

    # Relationships
    user = relationship("User", back_populates="conversation_memories")

    def __repr__(self) -> str:
        return f"<ConversationMemory(id={self.id}, user_id={self.user_id}, kind={self.kind})>"
