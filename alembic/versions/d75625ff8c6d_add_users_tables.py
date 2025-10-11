"""add_users_tables

Revision ID: d75625ff8c6d
Revises: 65cb6b235291
Create Date: 2025-10-11 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd75625ff8c6d'
down_revision: Union[str, None] = '65cb6b235291'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('google_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('suburb_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['suburb_id'], ['suburbs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('google_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_user_google_id', 'users', ['google_id'], unique=False)
    op.create_index('idx_user_email', 'users', ['email'], unique=False)

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('experience_level', sa.String(length=50), nullable=True),
        sa.Column('garden_type', sa.String(length=100), nullable=True),
        sa.Column('climate_goals', sa.Text(), nullable=True),
        sa.Column('available_space_m2', sa.Float(), nullable=True),
        sa.Column('sun_exposure', sa.String(length=50), nullable=True),
        sa.Column('has_containers', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('organic_preference', sa.Boolean(), nullable=True, server_default=sa.text('true')),
        sa.Column('budget_level', sa.String(length=50), nullable=True),
        sa.Column('notification_preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create user_favorites table
    op.create_table(
        'user_favorites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('priority_level', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'plant_id', name='unique_user_plant_favorite')
    )
    op.create_index('idx_user_favorites_user_created', 'user_favorites', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_user_favorites_user_created', table_name='user_favorites')
    op.drop_table('user_favorites')
    op.drop_table('user_profiles')
    op.drop_index('idx_user_email', table_name='users')
    op.drop_index('idx_user_google_id', table_name='users')
    op.drop_table('users')
