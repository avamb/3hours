"""Convert all timestamp columns to TIMESTAMP WITH TIME ZONE

Revision ID: 0017
Revises: 0016
Create Date: 2026-01-28

This migration converts all TIMESTAMP WITHOUT TIME ZONE columns to TIMESTAMP WITH TIME ZONE
for proper timezone handling across the application.

IMPORTANT: This assumes all existing timestamps are in UTC!
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0017'
down_revision = '0016'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Convert all timestamp columns to TIMESTAMPTZ"""

    # IMPORTANT: Set timezone to UTC for the session to ensure correct conversion
    op.execute("SET TIME ZONE 'UTC'")

    # 1. Users table
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
            USING updated_at AT TIME ZONE 'UTC',
        ALTER COLUMN last_active_at TYPE TIMESTAMP WITH TIME ZONE
            USING last_active_at AT TIME ZONE 'UTC',
        ALTER COLUMN notifications_paused_until TYPE TIMESTAMP WITH TIME ZONE
            USING notifications_paused_until AT TIME ZONE 'UTC'
    """)

    # 2. Moments table
    op.execute("""
        ALTER TABLE moments
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
    """)

    # 3. Conversations table
    op.execute("""
        ALTER TABLE conversations
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
    """)

    # 4. Conversation memories table
    op.execute("""
        ALTER TABLE conversation_memories
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
            USING updated_at AT TIME ZONE 'UTC'
    """)

    # 5. User stats table
    op.execute("""
        ALTER TABLE user_stats
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
            USING updated_at AT TIME ZONE 'UTC'
    """)

    # Note: last_good_moment_date is DATE type, not TIMESTAMP, so we don't convert it

    # 6. Feedback table
    op.execute("""
        ALTER TABLE feedback
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN reviewed_at TYPE TIMESTAMP WITH TIME ZONE
            USING reviewed_at AT TIME ZONE 'UTC'
    """)

    # 7. Social profiles table
    op.execute("""
        ALTER TABLE social_profiles
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
            USING updated_at AT TIME ZONE 'UTC',
        ALTER COLUMN last_parsed_at TYPE TIMESTAMP WITH TIME ZONE
            USING last_parsed_at AT TIME ZONE 'UTC'
    """)

    # 8. API usage table
    op.execute("""
        ALTER TABLE api_usage
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
    """)

    # 9. System logs table
    op.execute("""
        ALTER TABLE system_logs
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
    """)

    # 10. Prompt templates table
    op.execute("""
        ALTER TABLE prompt_templates
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
            USING updated_at AT TIME ZONE 'UTC'
    """)

    # 11. Question templates table
    op.execute("""
        ALTER TABLE question_templates
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
            USING updated_at AT TIME ZONE 'UTC'
    """)

    # 12. Scheduled notifications table (if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scheduled_notifications') THEN
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scheduled_notifications' AND column_name = 'scheduled_for') THEN
                    ALTER TABLE scheduled_notifications
                    ALTER COLUMN scheduled_for TYPE TIMESTAMP WITH TIME ZONE
                        USING scheduled_for AT TIME ZONE 'UTC';
                END IF;
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scheduled_notifications' AND column_name = 'created_at') THEN
                    ALTER TABLE scheduled_notifications
                    ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
                        USING created_at AT TIME ZONE 'UTC';
                END IF;
            END IF;
        END $$;
    """)

    # 13. Campaign activities table (if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'campaign_activities') THEN
                ALTER TABLE campaign_activities
                ALTER COLUMN triggered_at TYPE TIMESTAMP WITH TIME ZONE
                    USING triggered_at AT TIME ZONE 'UTC';
            END IF;
        END $$;
    """)

    # 14. Campaigns table (if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'campaigns') THEN
                ALTER TABLE campaigns
                ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
                    USING created_at AT TIME ZONE 'UTC',
                ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
                    USING updated_at AT TIME ZONE 'UTC';
            END IF;
        END $$;
    """)

    print("✓ All timestamp columns converted to TIMESTAMP WITH TIME ZONE")


def downgrade() -> None:
    """Revert timestamp columns back to TIMESTAMP WITHOUT TIME ZONE"""

    # IMPORTANT: Set timezone to UTC for the session
    op.execute("SET TIME ZONE 'UTC'")

    # 1. Users table
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING updated_at AT TIME ZONE 'UTC',
        ALTER COLUMN last_active_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING last_active_at AT TIME ZONE 'UTC',
        ALTER COLUMN notifications_paused_until TYPE TIMESTAMP WITHOUT TIME ZONE
            USING notifications_paused_until AT TIME ZONE 'UTC'
    """)

    # 2. Moments table
    op.execute("""
        ALTER TABLE moments
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
    """)

    # 3. Conversations table
    op.execute("""
        ALTER TABLE conversations
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
    """)

    # 4. Conversation memories table
    op.execute("""
        ALTER TABLE conversation_memories
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING updated_at AT TIME ZONE 'UTC'
    """)

    # 5. User stats table
    op.execute("""
        ALTER TABLE user_stats
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING updated_at AT TIME ZONE 'UTC'
    """)

    # 6. Feedback table
    op.execute("""
        ALTER TABLE feedback
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN reviewed_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING reviewed_at AT TIME ZONE 'UTC'
    """)

    # 7. Social profiles table
    op.execute("""
        ALTER TABLE social_profiles
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING updated_at AT TIME ZONE 'UTC',
        ALTER COLUMN last_parsed_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING last_parsed_at AT TIME ZONE 'UTC'
    """)

    # 8. API usage table
    op.execute("""
        ALTER TABLE api_usage
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
    """)

    # 9. System logs table
    op.execute("""
        ALTER TABLE system_logs
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
    """)

    # 10. Prompt templates table
    op.execute("""
        ALTER TABLE prompt_templates
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING updated_at AT TIME ZONE 'UTC'
    """)

    # 11. Question templates table
    op.execute("""
        ALTER TABLE question_templates
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC',
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
            USING updated_at AT TIME ZONE 'UTC'
    """)

    # 12. Scheduled notifications table (if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scheduled_notifications') THEN
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scheduled_notifications' AND column_name = 'scheduled_for') THEN
                    ALTER TABLE scheduled_notifications
                    ALTER COLUMN scheduled_for TYPE TIMESTAMP WITHOUT TIME ZONE
                        USING scheduled_for AT TIME ZONE 'UTC';
                END IF;
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scheduled_notifications' AND column_name = 'created_at') THEN
                    ALTER TABLE scheduled_notifications
                    ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
                        USING created_at AT TIME ZONE 'UTC';
                END IF;
            END IF;
        END $$;
    """)

    # 13. Campaign activities table (if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'campaign_activities') THEN
                ALTER TABLE campaign_activities
                ALTER COLUMN triggered_at TYPE TIMESTAMP WITHOUT TIME ZONE
                    USING triggered_at AT TIME ZONE 'UTC';
            END IF;
        END $$;
    """)

    # 14. Campaigns table (if exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'campaigns') THEN
                ALTER TABLE campaigns
                ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
                    USING created_at AT TIME ZONE 'UTC',
                ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
                    USING updated_at AT TIME ZONE 'UTC';
            END IF;
        END $$;
    """)

    print("✓ All timestamp columns reverted to TIMESTAMP WITHOUT TIME ZONE")