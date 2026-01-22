"""Add notifications_paused_until field to users table

Revision ID: 0015
Revises: 0014
Create Date: 2026-01-22

This field stores the datetime until which user notifications are paused.
When set, the scheduler will skip sending notifications to this user until the specified datetime.
If user sends a message while paused, the pause is automatically cleared.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add notifications_paused_until column to users table
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS notifications_paused_until TIMESTAMP DEFAULT NULL
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS notifications_paused_until
    """)
