"""add_performance_indexes

Revision ID: c840856cb980
Revises: f9e4d3b2a1c0
Create Date: 2025-10-16 13:57:32.399538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c840856cb980'
down_revision: Union[str, None] = 'f9e4d3b2a1c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for faster queries"""

    # 1. Plants search optimization - case-insensitive plant name search
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plants_name_lower
        ON plants (LOWER(plant_name))
    """)

    # 2. Plants search optimization - case-insensitive scientific name search
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plants_scientific_name_lower
        ON plants (LOWER(scientific_name))
    """)

    # 3. Plants filtering optimization - category and maintenance level
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plants_category_maintenance
        ON plants (plant_category, maintenance_level)
    """)

    # 4. User instances queries optimization
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_instances_compound
        ON user_plant_instances (user_id, is_active, created_at DESC)
    """)

    # 5. Progress tracking optimization
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_progress_tracking_lookup
        ON user_progress_tracking (user_plant_instance_id, is_completed)
    """)

    # 6. Climate data time-series queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_climate_suburb_date_desc
        ON climate_data (suburb_id, recorded_date DESC)
    """)

    print("✅ Performance indexes created successfully!")


def downgrade() -> None:
    """Remove performance indexes"""
    op.execute("DROP INDEX IF EXISTS idx_plants_name_lower")
    op.execute("DROP INDEX IF EXISTS idx_plants_scientific_name_lower")
    op.execute("DROP INDEX IF EXISTS idx_plants_category_maintenance")
    op.execute("DROP INDEX IF EXISTS idx_user_instances_compound")
    op.execute("DROP INDEX IF EXISTS idx_progress_tracking_lookup")
    op.execute("DROP INDEX IF EXISTS idx_climate_suburb_date_desc")
