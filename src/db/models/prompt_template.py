"""
MINDSETHAPPYBOT - PromptTemplate model
Stores editable prompt templates with versioning for admin management.

Features:
- Key-based identification for different prompt layers
- Version history for rollback capability
- Active version flag for production use
- Notes for change documentation
"""
from datetime import datetime

from sqlalchemy import Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class PromptTemplate(Base):
    """
    PromptTemplate model - stores versioned prompt templates.

    Each prompt is identified by a key (e.g., 'dialog_system_ru', 'language_instruction')
    and can have multiple versions. Only one version per key can be active at a time.
    """
    __tablename__ = "prompt_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Unique identifier for the prompt layer
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Full prompt content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Version number (auto-incremented per key)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Whether this version is currently active
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Change notes/description
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<PromptTemplate(id={self.id}, key='{self.key}', "
            f"version={self.version}, active={self.is_active})>"
        )
