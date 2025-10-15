"""Add setup_completed fields to user_plant_instances

Revision ID: f9e4d3b2a1c0
Revises: c2d8e9f1a4b3
Create Date: 2025-10-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9e4d3b2a1c0'
down_revision: Union[str, None] = 'c2d8e9f1a4b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add setup_completed and setup_completed_at columns to user_plant_instances
    op.add_column('user_plant_instances', sa.Column('setup_completed', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('user_plant_instances', sa.Column('setup_completed_at', sa.DateTime(), nullable=True))

    # Set default value for existing rows
    op.execute("UPDATE user_plant_instances SET setup_completed = false WHERE setup_completed IS NULL")

    # Make setup_completed non-nullable after setting defaults
    op.alter_column('user_plant_instances', 'setup_completed', nullable=False, server_default='false')


def downgrade() -> None:
    # Remove the columns if rolling back
    op.drop_column('user_plant_instances', 'setup_completed_at')
    op.drop_column('user_plant_instances', 'setup_completed')
