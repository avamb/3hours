"""Initial database schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('language_code', sa.String(length=10), server_default='ru', nullable=False),
        sa.Column('formal_address', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('active_hours_start', sa.Time(), server_default='09:00', nullable=False),
        sa.Column('active_hours_end', sa.Time(), server_default='21:00', nullable=False),
        sa.Column('notification_interval_hours', sa.Integer(), server_default='3', nullable=False),
        sa.Column('notifications_enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('timezone', sa.String(length=50), server_default='UTC', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_active_at', sa.DateTime(), nullable=True),
        sa.Column('onboarding_completed', sa.Boolean(), server_default='false', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index('idx_users_telegram_id', 'users', ['telegram_id'], unique=True)

    # Create moments table
    op.create_table(
        'moments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source_type', sa.String(length=20), server_default='text', nullable=False),
        sa.Column('original_voice_file_id', sa.String(length=255), nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('mood_score', sa.Float(), nullable=True),
        sa.Column('topics', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_moments_user_id', 'moments', ['user_id'])
    op.create_index('idx_moments_created_at', 'moments', ['created_at'])

    # Create vector index for similarity search
    op.execute(
        'CREATE INDEX idx_moments_embedding ON moments '
        'USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)'
    )

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])

    # Create user_stats table
    op.create_table(
        'user_stats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('current_streak', sa.Integer(), server_default='0', nullable=False),
        sa.Column('longest_streak', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_moments', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_questions_sent', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_questions_answered', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_response_date', sa.Date(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create scheduled_notifications table
    op.create_table(
        'scheduled_notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(), nullable=False),
        sa.Column('sent', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('question_template_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scheduled_notifications_time', 'scheduled_notifications', ['scheduled_time', 'sent'])

    # Create question_templates table
    op.create_table(
        'question_templates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('language_code', sa.String(length=10), nullable=False),
        sa.Column('formal', sa.Boolean(), nullable=False),
        sa.Column('template_text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), server_default='main', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_question_templates_language', 'question_templates', ['language_code'])


def downgrade() -> None:
    op.drop_table('question_templates')
    op.drop_table('scheduled_notifications')
    op.drop_table('user_stats')
    op.drop_table('conversations')
    op.drop_table('moments')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS vector')
