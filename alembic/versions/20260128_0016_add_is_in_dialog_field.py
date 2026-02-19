"""Add is_in_dialog field to users table

Revision ID: 0016
Revises: 0015
Create Date: 2026-01-28

This field stores the dialog state in database instead of in-memory.
Prevents losing dialog state on bot restart and enables multi-instance deployment.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0016'
down_revision = '0015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_in_dialog column to users table
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS is_in_dialog BOOLEAN DEFAULT FALSE
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS is_in_dialog
    """)