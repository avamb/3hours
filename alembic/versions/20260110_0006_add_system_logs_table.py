"""Add system_logs table

Revision ID: 0006
Revises: 0005
Create Date: 2026-01-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "system_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_system_logs_level", "system_logs", ["level"])
    op.create_index("idx_system_logs_source", "system_logs", ["source"])
    op.create_index("idx_system_logs_created_at", "system_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_system_logs_created_at", table_name="system_logs")
    op.drop_index("idx_system_logs_source", table_name="system_logs")
    op.drop_index("idx_system_logs_level", table_name="system_logs")
    op.drop_table("system_logs")

