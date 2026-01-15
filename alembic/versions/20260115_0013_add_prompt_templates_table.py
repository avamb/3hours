"""Add prompt_templates table for editable prompt layers

Revision ID: 0013
Revises: 0012
Create Date: 2026-01-15

Stores versioned prompt templates with support for:
- Key-based identification for different prompt layers
- Version history for rollback capability
- Active version flag for production use
- Notes for change documentation
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0013'
down_revision = '0012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create prompt_templates table
    op.execute("""
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id SERIAL PRIMARY KEY,
            key VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            is_active BOOLEAN NOT NULL DEFAULT FALSE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(key, version)
        )
    """)

    # Create indexes for efficient retrieval
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_prompt_templates_key
        ON prompt_templates(key)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_prompt_templates_active
        ON prompt_templates(is_active)
        WHERE is_active = TRUE
    """)

    # Create function to auto-update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_prompt_templates_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)

    # Create trigger for auto-updating updated_at
    op.execute("""
        CREATE TRIGGER trigger_prompt_templates_updated_at
        BEFORE UPDATE ON prompt_templates
        FOR EACH ROW
        EXECUTE FUNCTION update_prompt_templates_updated_at()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trigger_prompt_templates_updated_at ON prompt_templates")
    op.execute("DROP FUNCTION IF EXISTS update_prompt_templates_updated_at()")
    op.execute("DROP INDEX IF EXISTS idx_prompt_templates_active")
    op.execute("DROP INDEX IF EXISTS idx_prompt_templates_key")
    op.execute("DROP TABLE IF EXISTS prompt_templates")
