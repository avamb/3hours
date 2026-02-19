"""Add attribution tracking for user acquisition

Revision ID: 0018
Revises: 0017
Create Date: 2026-01-30

This migration adds:
1. Attribution fields to users table (first-touch and last-touch)
2. start_events table to log each /start command

Used for tracking user acquisition from Telegram deep links (e.g., Reddit campaigns).
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0018'
down_revision = '0017'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add attribution tracking columns and start_events table"""

    # Add first-touch attribution fields to users table
    op.add_column('users', sa.Column('first_source', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('first_campaign', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('first_start_payload', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('first_started_at', sa.DateTime(timezone=True), nullable=True))

    # Add last-touch attribution fields to users table
    op.add_column('users', sa.Column('last_source', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('last_campaign', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('last_start_payload', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('last_started_at', sa.DateTime(timezone=True), nullable=True))

    # Create start_events table
    op.create_table(
        'start_events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('raw_payload', sa.String(500), nullable=True),
        sa.Column('source', sa.String(100), nullable=False, server_default='unknown'),
        sa.Column('campaign', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Add indexes for analytics queries
    op.create_index('ix_start_events_telegram_id', 'start_events', ['telegram_id'])
    op.create_index('ix_start_events_source', 'start_events', ['source'])
    op.create_index('ix_start_events_campaign', 'start_events', ['campaign'])
    op.create_index('ix_start_events_created_at', 'start_events', ['created_at'])
    op.create_index('ix_start_events_user_id', 'start_events', ['user_id'])
    # Composite indexes for analytics time-series queries
    op.create_index('idx_start_events_source_created', 'start_events', ['source', 'created_at'])
    op.create_index('idx_start_events_campaign_created', 'start_events', ['campaign', 'created_at'])


def downgrade() -> None:
    """Remove attribution tracking"""

    # Drop composite indexes first
    op.drop_index('idx_start_events_campaign_created', 'start_events')
    op.drop_index('idx_start_events_source_created', 'start_events')
    # Drop single-column indexes
    op.drop_index('ix_start_events_user_id', 'start_events')
    op.drop_index('ix_start_events_created_at', 'start_events')
    op.drop_index('ix_start_events_campaign', 'start_events')
    op.drop_index('ix_start_events_source', 'start_events')
    op.drop_index('ix_start_events_telegram_id', 'start_events')
    op.drop_table('start_events')

    # Remove attribution columns from users table
    op.drop_column('users', 'last_started_at')
    op.drop_column('users', 'last_start_payload')
    op.drop_column('users', 'last_campaign')
    op.drop_column('users', 'last_source')
    op.drop_column('users', 'first_started_at')
    op.drop_column('users', 'first_start_payload')
    op.drop_column('users', 'first_campaign')
    op.drop_column('users', 'first_source')
