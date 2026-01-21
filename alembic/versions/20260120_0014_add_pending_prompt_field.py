"""Add last_pending_prompt_message_id field to users table

Revision ID: 0014
Revises: 0013
Create Date: 2026-01-20

This field tracks the Telegram message_id of the last unanswered scheduled prompt
to prevent message accumulation in the chat. When a new scheduled prompt is sent,
any previous unanswered prompt can be deleted using this stored message_id.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add last_pending_prompt_message_id column to users table
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS last_pending_prompt_message_id BIGINT DEFAULT NULL
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS last_pending_prompt_message_id
    """)
