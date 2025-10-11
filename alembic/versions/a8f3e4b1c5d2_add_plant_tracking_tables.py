"""Add plant tracking tables for Iteration 3

Revision ID: a8f3e4b1c5d2
Revises: 65cb6b235291
Create Date: 2025-10-10 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a8f3e4b1c5d2'
down_revision: Union[str, None] = 'd75625ff8c6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create plant_growth_data table
    op.create_table(
        'plant_growth_data',
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('requirements_checklist', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('setup_instructions', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('growth_stages', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('care_tips', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('data_source_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id'], ),
        sa.PrimaryKeyConstraint('plant_id')
    )
    op.create_index('idx_plant_growth_data_updated', 'plant_growth_data', ['last_updated'], unique=False)

    # Create user_plant_instances table
    op.create_table(
        'user_plant_instances',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('plant_nickname', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('expected_maturity_date', sa.Date(), nullable=False),
        sa.Column('current_stage', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('user_notes', sa.Text(), nullable=True),
        sa.Column('location_details', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_plant_instances_plant', 'user_plant_instances', ['plant_id'], unique=False)
    op.create_index('idx_user_plant_instances_stage', 'user_plant_instances', ['current_stage'], unique=False)
    op.create_index('idx_user_plant_instances_user_active', 'user_plant_instances', ['user_id', 'is_active'], unique=False)

    # Create user_progress_tracking table
    op.create_table(
        'user_progress_tracking',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_plant_instance_id', sa.Integer(), nullable=False),
        sa.Column('checklist_item_key', sa.String(length=200), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('user_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_plant_instance_id'], ['user_plant_instances.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_plant_instance_id', 'checklist_item_key', name='unique_instance_checklist_item')
    )
    op.create_index('idx_user_progress_tracking_completed', 'user_progress_tracking', ['user_plant_instance_id', 'is_completed'], unique=False)
    op.create_index('idx_user_progress_tracking_instance', 'user_progress_tracking', ['user_plant_instance_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_index('idx_user_progress_tracking_instance', table_name='user_progress_tracking')
    op.drop_index('idx_user_progress_tracking_completed', table_name='user_progress_tracking')
    op.drop_table('user_progress_tracking')

    op.drop_index('idx_user_plant_instances_user_active', table_name='user_plant_instances')
    op.drop_index('idx_user_plant_instances_stage', table_name='user_plant_instances')
    op.drop_index('idx_user_plant_instances_plant', table_name='user_plant_instances')
    op.drop_table('user_plant_instances')

    op.drop_index('idx_plant_growth_data_updated', table_name='plant_growth_data')
    op.drop_table('plant_growth_data')
