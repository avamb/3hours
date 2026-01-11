"""Add user gender field for gender detection

Revision ID: 0009
Revises: 0008
Create Date: 2026-01-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add gender column to users table
    op.add_column(
        "users",
        sa.Column("gender", sa.String(length=10), nullable=True, server_default="unknown")
    )


def downgrade() -> None:
    op.drop_column("users", "gender")
