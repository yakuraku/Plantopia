"""Email authentication migration and guide favorites

This migration implements the email-based authentication system and adds guide favorites feature.

Changes:
1. Make users.google_id nullable (auth now handled by frontend)
2. Create user_guide_favorites table for favorite plant guides

Revision ID: c2d8e9f1a4b3
Revises: b9d2f7e8a3c1
Create Date: 2025-10-11 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2d8e9f1a4b3'
down_revision: Union[str, None] = 'b9d2f7e8a3c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade database schema:
    1. Make google_id nullable in users table
    2. Create user_guide_favorites table
    """

    # 1. Make google_id nullable (supports frontend auth)
    # Note: PostgreSQL syntax - adjust if using different database
    op.alter_column('users', 'google_id',
                    existing_type=sa.String(length=255),
                    nullable=True,
                    existing_nullable=False)

    # 2. Create user_guide_favorites table
    op.create_table(
        'user_guide_favorites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('guide_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'guide_name', name='unique_user_guide_favorite')
    )

    # Create indexes for performance
    op.create_index('idx_user_guide_favorites_user_created', 'user_guide_favorites', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    """
    Downgrade database schema:
    1. Drop user_guide_favorites table
    2. Make google_id NOT NULL in users table
    """

    # Drop user_guide_favorites table and its indexes
    op.drop_index('idx_user_guide_favorites_user_created', table_name='user_guide_favorites')
    op.drop_table('user_guide_favorites')

    # Revert google_id to NOT NULL
    # WARNING: This will fail if there are users with NULL google_id
    # In production, you should clean up data before running downgrade
    op.alter_column('users', 'google_id',
                    existing_type=sa.String(length=255),
                    nullable=False,
                    existing_nullable=True)
