"""Add user summary fields and template activity fields

Revision ID: 0003
Revises: 0002
Create Date: 2026-01-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users: summary toggles + moderation/aux fields
    op.add_column("users", sa.Column("last_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("detected_language", sa.String(length=10), nullable=True))
    op.add_column(
        "users",
        sa.Column("daily_summary_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("weekly_summary_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("monthly_summary_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.add_column("users", sa.Column("is_blocked", sa.Boolean(), server_default=sa.text("false"), nullable=False))

    # question_templates: allow soft-disable and track updates (non-breaking for existing code)
    op.add_column(
        "question_templates",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.add_column(
        "question_templates",
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("question_templates", "updated_at")
    op.drop_column("question_templates", "is_active")
    op.drop_column("users", "is_blocked")
    op.drop_column("users", "monthly_summary_enabled")
    op.drop_column("users", "weekly_summary_enabled")
    op.drop_column("users", "daily_summary_enabled")
    op.drop_column("users", "detected_language")
    op.drop_column("users", "last_name")

