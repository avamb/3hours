"""Add admin response fields to feedback

Revision ID: 0007
Revises: 0006
Create Date: 2026-01-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Admin responses (used by admin panel)
    op.add_column("feedback", sa.Column("admin_response", sa.Text(), nullable=True))
    op.add_column("feedback", sa.Column("admin_response_at", sa.DateTime(), nullable=True))
    # false = pending delivery (if bot ever implements it), true = nothing pending
    op.add_column(
        "feedback",
        sa.Column("admin_response_sent", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )

    op.create_index("idx_feedback_admin_response_sent", "feedback", ["admin_response_sent"])


def downgrade() -> None:
    op.drop_index("idx_feedback_admin_response_sent", table_name="feedback")
    op.drop_column("feedback", "admin_response_sent")
    op.drop_column("feedback", "admin_response_at")
    op.drop_column("feedback", "admin_response")


