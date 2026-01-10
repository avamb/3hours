"""Add social_profiles table

Revision ID: 0004
Revises: 0003
Create Date: 2026-01-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "social_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("instagram_url", sa.String(length=500), nullable=True),
        sa.Column("facebook_url", sa.String(length=500), nullable=True),
        sa.Column("twitter_url", sa.String(length=500), nullable=True),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.Column("vk_url", sa.String(length=500), nullable=True),
        sa.Column("telegram_channel_url", sa.String(length=500), nullable=True),
        sa.Column("youtube_url", sa.String(length=500), nullable=True),
        sa.Column("tiktok_url", sa.String(length=500), nullable=True),
        sa.Column("bio_text", sa.Text(), nullable=True),
        sa.Column("parsed_bio", sa.Text(), nullable=True),
        sa.Column("interests", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("communication_style", sa.String(length=50), nullable=True),
        sa.Column("interests_embedding", Vector(1536), nullable=True),
        sa.Column("last_parsed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("idx_social_profiles_user_id", "social_profiles", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_social_profiles_user_id", table_name="social_profiles")
    op.drop_table("social_profiles")

