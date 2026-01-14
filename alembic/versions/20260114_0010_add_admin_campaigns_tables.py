"""Add admin campaigns tables for broadcast functionality

Revision ID: 0010
Revises: 0009
Create Date: 2026-01-14 14:00:00

Creates:
- admin_campaigns: Stores campaign metadata (title, topic, draft_text, tone, filters, status)
- admin_campaign_targets: Stores individual target users with rendered text and delivery status
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '0010'
down_revision: Union[str, None] = '0009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create admin_campaigns table
    op.create_table(
        'admin_campaigns',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('topic', sa.Text(), nullable=True),
        sa.Column('draft_text', sa.Text(), nullable=False),
        sa.Column('tone', sa.String(length=50), server_default='friendly', nullable=False),
        # Tone options: 'short', 'friendly', 'formal'
        sa.Column('filters_json', JSONB, nullable=True),
        # Filter schema: {
        #   "timezone_default": true/false,  # timezone is null/UTC
        #   "formal_address": true/false/null,
        #   "language_codes": ["ru", "en", ...] or null,
        #   "onboarding_completed": true/false/null,
        #   "notifications_enabled": true/false/null,
        #   "notification_interval_hours": int or null,
        #   "inactive_days": int or null,  # last_active_at older than N days
        #   "exclude_blocked": true (default true)
        # }
        sa.Column('delivery_params_json', JSONB, nullable=True),
        # Delivery schema: {
        #   "test_mode": true/false,
        #   "within_hours": 24,  # complete delivery within N hours
        #   "not_after": "2026-01-15T23:59:59Z"  # deadline for delivery
        # }
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='draft', nullable=False),
        # Status options: 'draft', 'preview', 'scheduled', 'sending', 'done', 'cancelled'
        sa.Column('total_targets', sa.Integer(), server_default='0', nullable=False),
        sa.Column('sent_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('failed_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_admin_campaigns_status', 'admin_campaigns', ['status'])
    op.create_index('idx_admin_campaigns_created_at', 'admin_campaigns', ['created_at'])

    # Create admin_campaign_targets table
    op.create_table(
        'admin_campaign_targets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('language_code', sa.String(length=10), nullable=False),
        sa.Column('formal_address', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('planned_send_at_utc', sa.DateTime(), nullable=True),
        sa.Column('rendered_text', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        # Status options: 'pending', 'rendered', 'sent', 'failed', 'skipped'
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['admin_campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_campaign_targets_campaign_id', 'admin_campaign_targets', ['campaign_id'])
    op.create_index('idx_campaign_targets_user_id', 'admin_campaign_targets', ['user_id'])
    op.create_index('idx_campaign_targets_status', 'admin_campaign_targets', ['status'])
    op.create_index('idx_campaign_targets_planned_send', 'admin_campaign_targets', ['planned_send_at_utc', 'status'])
    # Unique constraint to prevent duplicate targets per campaign
    op.create_unique_constraint('uq_campaign_user', 'admin_campaign_targets', ['campaign_id', 'user_id'])


def downgrade() -> None:
    op.drop_table('admin_campaign_targets')
    op.drop_table('admin_campaigns')
