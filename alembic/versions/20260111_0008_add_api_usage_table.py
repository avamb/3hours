"""Add api_usage table for tracking token expenses

Revision ID: 0008
Revises: 0007
Create Date: 2026-01-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_usage",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),  # Can be null for system calls
        sa.Column("api_provider", sa.String(length=50), nullable=False),  # openai, whisper, etc.
        sa.Column("model", sa.String(length=100), nullable=False),  # gpt-4o-mini, whisper-1, etc.
        sa.Column("operation_type", sa.String(length=50), nullable=False),  # chat, transcription, embedding, etc.
        sa.Column("input_tokens", sa.Integer(), nullable=True, default=0),
        sa.Column("output_tokens", sa.Integer(), nullable=True, default=0),
        sa.Column("total_tokens", sa.Integer(), nullable=True, default=0),
        sa.Column("cost_usd", sa.Numeric(precision=10, scale=6), nullable=True, default=0),  # Cost in USD
        sa.Column("duration_ms", sa.Integer(), nullable=True),  # Request duration in milliseconds
        sa.Column("success", sa.Boolean(), nullable=False, default=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("extra_data", sa.JSON(), nullable=True),  # Additional context
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_api_usage_user_id", "api_usage", ["user_id"])
    op.create_index("idx_api_usage_api_provider", "api_usage", ["api_provider"])
    op.create_index("idx_api_usage_created_at", "api_usage", ["created_at"])
    op.create_index("idx_api_usage_model", "api_usage", ["model"])


def downgrade() -> None:
    op.drop_index("idx_api_usage_model", table_name="api_usage")
    op.drop_index("idx_api_usage_created_at", table_name="api_usage")
    op.drop_index("idx_api_usage_api_provider", table_name="api_usage")
    op.drop_index("idx_api_usage_user_id", table_name="api_usage")
    op.drop_table("api_usage")
