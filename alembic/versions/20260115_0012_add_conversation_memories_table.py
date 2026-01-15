"""Add conversation_memories table for per-user dialog vector memory

Revision ID: 0012
Revises: 0011
Create Date: 2026-01-15

Stores extracted "memory-worthy" facts from user conversations.
Enables per-user isolated memory retrieval for answering questions
like "remember what I said about..." without hallucination.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

# revision identifiers, used by Alembic.
revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversation_memories table with pgvector embedding
    op.execute("""
        CREATE TABLE IF NOT EXISTS conversation_memories (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            source_conversation_ids INTEGER[] NOT NULL DEFAULT '{}',
            content TEXT NOT NULL,
            embedding vector(1536),
            kind VARCHAR(50) NOT NULL DEFAULT 'fact',
            importance FLOAT NOT NULL DEFAULT 1.0,
            fingerprint VARCHAR(64) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            metadata JSONB DEFAULT '{}',
            UNIQUE(user_id, fingerprint)
        )
    """)

    # Create indexes for efficient retrieval
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation_memories_user_id
        ON conversation_memories(user_id)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation_memories_kind
        ON conversation_memories(kind)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation_memories_created_at
        ON conversation_memories(created_at)
    """)

    # Create vector similarity index for efficient retrieval
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation_memories_embedding
        ON conversation_memories USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)

    # Add tracking column to users table for incremental indexing
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS last_memory_indexed_conversation_id INTEGER DEFAULT 0
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_conversation_memories_embedding")
    op.execute("DROP INDEX IF EXISTS idx_conversation_memories_created_at")
    op.execute("DROP INDEX IF EXISTS idx_conversation_memories_kind")
    op.execute("DROP INDEX IF EXISTS idx_conversation_memories_user_id")
    op.execute("DROP TABLE IF EXISTS conversation_memories")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS last_memory_indexed_conversation_id")
