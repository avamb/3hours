"""Add knowledge_base and knowledge_chunks tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-01-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_base",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("file_type", sa.String(length=20), nullable=True),
        sa.Column("original_filename", sa.String(length=500), nullable=True),
        sa.Column("tags", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("chunks_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("indexing_status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("indexing_error", sa.Text(), nullable=True),
        sa.Column("usage_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_knowledge_base_category", "knowledge_base", ["category"])
    op.create_index("idx_knowledge_base_indexing_status", "knowledge_base", ["indexing_status"])

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("knowledge_base_id", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_base_id"], ["knowledge_base.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_knowledge_chunks_kb_id", "knowledge_chunks", ["knowledge_base_id"])


def downgrade() -> None:
    op.drop_index("idx_knowledge_chunks_kb_id", table_name="knowledge_chunks")
    op.drop_table("knowledge_chunks")
    op.drop_index("idx_knowledge_base_indexing_status", table_name="knowledge_base")
    op.drop_index("idx_knowledge_base_category", table_name="knowledge_base")
    op.drop_table("knowledge_base")

