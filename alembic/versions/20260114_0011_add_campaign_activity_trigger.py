"""Add activity trigger fields to admin_campaign_targets

Revision ID: 0011
Revises: 0010
Create Date: 2026-01-14 18:00:00

Adds fields for the "send on activity" feature:
- last_activity_triggered_at: Timestamp when last activity-based send was triggered
- activity_send_count: Number of activity-triggered sends for this target
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0011'
down_revision: Union[str, None] = '0010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns for activity-triggered delivery
    op.add_column('admin_campaign_targets',
        sa.Column('last_activity_triggered_at', sa.DateTime(), nullable=True))
    op.add_column('admin_campaign_targets',
        sa.Column('activity_send_count', sa.Integer(), server_default='0', nullable=False))

    # Add index for efficient activity trigger queries
    op.create_index('idx_campaign_targets_activity_trigger', 'admin_campaign_targets',
                    ['campaign_id', 'status', 'last_activity_triggered_at'])


def downgrade() -> None:
    op.drop_index('idx_campaign_targets_activity_trigger', table_name='admin_campaign_targets')
    op.drop_column('admin_campaign_targets', 'activity_send_count')
    op.drop_column('admin_campaign_targets', 'last_activity_triggered_at')
