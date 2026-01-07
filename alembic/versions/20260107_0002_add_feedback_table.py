"""Add feedback table for user suggestions and bug reports

Revision ID: 0002
Revises: 0001
Create Date: 2026-01-07 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='new', nullable=False),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_feedback_user_id', 'feedback', ['user_id'])
    op.create_index('idx_feedback_status', 'feedback', ['status'])
    op.create_index('idx_feedback_created_at', 'feedback', ['created_at'])


def downgrade() -> None:
    op.drop_index('idx_feedback_created_at', table_name='feedback')
    op.drop_index('idx_feedback_status', table_name='feedback')
    op.drop_index('idx_feedback_user_id', table_name='feedback')
    op.drop_table('feedback')
