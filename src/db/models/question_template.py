"""
MINDSETHAPPYBOT - QuestionTemplate model
Stores question templates for various languages and contexts
"""
from datetime import datetime, timezone

from sqlalchemy import Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class QuestionTemplate(Base):
    """QuestionTemplate model - stores question templates"""
    __tablename__ = "question_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    formal: Mapped[bool] = mapped_column(Boolean, nullable=False)  # True = вы, False = ты
    template_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="main")
    # Categories: 'main', 'follow_up', 'return_inactive'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<QuestionTemplate(id={self.id}, lang={self.language_code}, category={self.category})>"
