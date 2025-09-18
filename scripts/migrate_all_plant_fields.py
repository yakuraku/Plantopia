#!/usr/bin/env python3
"""
Migration script to add all missing columns to plants table and populate from CSV files
"""

import asyncio
import os
import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import get_async_db, async_engine
from app.core.config import settings
from app.models.database import Plant
from sqlalchemy.ext.asyncio import AsyncSession


def clean_value(value):
    """Clean and normalize values from CSV"""
    if pd.isna(value) or value is None:
        return None
    str_value = str(value).strip()
    if str_value.lower() in ['nan', 'none', 'null', '']:
        return None
    return str_value


async def add_columns_if_needed():
    """Add all missing columns to plants table if they don't exist"""
    async with async_engine.begin() as conn:
        # Check which columns already exist
        result = await conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='plants'
        """))
        existing_columns = {row[0] for row in result}

        # List of columns to add
        columns_to_add = [
            ('position', 'TEXT'),
            ('characteristics', 'TEXT'),
            ('plant_type', 'TEXT'),
            ('season', 'VARCHAR(100)'),
            ('germination', 'VARCHAR(200)'),
            ('additional_information', 'TEXT'),
            ('days_to_maturity', 'VARCHAR(100)'),
            ('plant_spacing', 'VARCHAR(100)'),
            ('sowing_depth', 'VARCHAR(100)'),
            ('hardiness_life_cycle', 'VARCHAR(200)'),
            ('seed_type', 'VARCHAR(100)'),
            ('beneficial_companions', 'TEXT'),
            ('harmful_companions', 'TEXT'),
            ('neutral_companions', 'TEXT'),
            ('cool_climate_sowing_period', 'VARCHAR(200)'),
            ('temperate_climate_sowing_period', 'VARCHAR(200)'),
            ('subtropical_climate_sowing_period', 'VARCHAR(200)'),
            ('tropical_climate_sowing_period', 'VARCHAR(200)'),
            ('arid_climate_sowing_period', 'VARCHAR(200)')
        ]

        # Add each column if it doesn't exist
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    await conn.execute(text(f"""
                        ALTER TABLE plants
                        ADD COLUMN {column_name} {column_type}
                    """))
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"⚠️ Error adding column {column_name}: {str(e)}")
            else:
                print(f"Column already exists: {column_name}")


async def update_plants_from_csv(session: AsyncSession):
    """Update existing plants with all missing fields from CSV files"""
    updated_count = 0
    total_plants = 0

    for category, csv_path in settings.CSV_PATHS.items():
        if not os.path.exists(csv_path):
            print(f"  ⚠️  {csv_path} not found, skipping {category} plants")
            continue

        print(f"\n  Processing {category} plants from {csv_path}...")

        try:
            # Read CSV file
            df = pd.read_csv(csv_path)

            # Process each row
            for _, row in df.iterrows():
                plant_name = clean_value(row.get('plant_name', row.get('name')))
                if not plant_name:
                    continue

                total_plants += 1

                # Prepare update data
                update_data = {
                    'plant_name': plant_name,
                    'category': category,

                    # Position and characteristics
                    'position': clean_value(row.get('position')),
                    'characteristics': clean_value(row.get('characteristics')),

                    # Additional CSV fields
                    'plant_type': clean_value(row.get('plant_type', row.get('type'))),
                    'season': clean_value(row.get('season')),
                    'germination': clean_value(row.get('germination')),
                    'additional_information': clean_value(row.get('additional_information')),
                    'days_to_maturity': clean_value(row.get('days_to_maturity')),
                    'plant_spacing': clean_value(row.get('plant_spacing', row.get('spacing'))),
                    'sowing_depth': clean_value(row.get('sowing_depth')),
                    'hardiness_life_cycle': clean_value(row.get('hardiness_life_cycle', row.get('hardiness'))),
                    'seed_type': clean_value(row.get('seed_type')),

                    # Companion planting fields
                    'beneficial_companions': clean_value(row.get('beneficial_companions', row.get('good_companions'))),
                    'harmful_companions': clean_value(row.get('harmful_companions', row.get('bad_companions'))),
                    'neutral_companions': clean_value(row.get('neutral_companions')),

                    # Climate-specific sowing periods
                    'cool_climate_sowing_period': clean_value(row.get('cool_climate_sowing_period', row.get('cool_climate_sowing'))),
                    'temperate_climate_sowing_period': clean_value(row.get('temperate_climate_sowing_period', row.get('temperate_climate_sowing'))),
                    'subtropical_climate_sowing_period': clean_value(row.get('subtropical_climate_sowing_period', row.get('subtropical_climate_sowing'))),
                    'tropical_climate_sowing_period': clean_value(row.get('tropical_climate_sowing_period', row.get('tropical_climate_sowing'))),
                    'arid_climate_sowing_period': clean_value(row.get('arid_climate_sowing_period', row.get('arid_climate_sowing')))
                }

                # Update plant in database
                result = await session.execute(
                    text("""
                        UPDATE plants
                        SET position = :position,
                            characteristics = :characteristics,
                            plant_type = :plant_type,
                            season = :season,
                            germination = :germination,
                            additional_information = :additional_information,
                            days_to_maturity = :days_to_maturity,
                            plant_spacing = :plant_spacing,
                            sowing_depth = :sowing_depth,
                            hardiness_life_cycle = :hardiness_life_cycle,
                            seed_type = :seed_type,
                            beneficial_companions = :beneficial_companions,
                            harmful_companions = :harmful_companions,
                            neutral_companions = :neutral_companions,
                            cool_climate_sowing_period = :cool_climate_sowing_period,
                            temperate_climate_sowing_period = :temperate_climate_sowing_period,
                            subtropical_climate_sowing_period = :subtropical_climate_sowing_period,
                            tropical_climate_sowing_period = :tropical_climate_sowing_period,
                            arid_climate_sowing_period = :arid_climate_sowing_period,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE plant_name = :plant_name
                        AND plant_category = :category
                    """),
                    update_data
                )

                if result.rowcount > 0:
                    updated_count += 1
                    if updated_count % 10 == 0:
                        print(f"    Updated {updated_count} plants...")

        except Exception as e:
            print(f"  ❌ Error processing {csv_path}: {str(e)}")
            continue

    await session.commit()

    print(f"\nSummary:")
    print(f"  ✅ Updated {updated_count} plants with all missing fields")
    print(f"  📊 Total plants in CSV files: {total_plants}")


async def verify_migration(session: AsyncSession):
    """Verify that migration was successful"""
    print("\n🔍 Verifying migration...")

    # Count plants with new fields populated
    checks = [
        ('position', "position IS NOT NULL"),
        ('characteristics', "characteristics IS NOT NULL"),
        ('plant_type', "plant_type IS NOT NULL"),
        ('beneficial_companions', "beneficial_companions IS NOT NULL"),
        ('temperate_climate_sowing_period', "temperate_climate_sowing_period IS NOT NULL")
    ]

    for field_name, condition in checks:
        result = await session.execute(text(f"""
            SELECT COUNT(*) FROM plants WHERE {condition}
        """))
        count = result.scalar()
        print(f"  Plants with {field_name}: {count}")

    # Sample some plants to see populated data
    print("\n📝 Sample plants with new data:")
    result = await session.execute(text("""
        SELECT plant_name, position, characteristics, plant_type
        FROM plants
        WHERE position IS NOT NULL
        OR characteristics IS NOT NULL
        LIMIT 5
    """))

    for row in result:
        print(f"\n  Plant: {row[0]}")
        if row[1]:
            print(f"    Position: {row[1][:60]}...")
        if row[2]:
            print(f"    Characteristics: {row[2][:60]}...")
        if row[3]:
            print(f"    Plant Type: {row[3][:60]}...")


async def main():
    """Main migration function"""
    print("=" * 60)
    print("🚀 PLANT FIELDS MIGRATION")
    print("=" * 60)

    # Step 1: Add columns if needed
    print("\nStep 1: Adding columns to plants table...")
    await add_columns_if_needed()

    # Step 2: Update plants with all missing field data
    print("\nStep 2: Updating plants with all missing field data...")
    async for session in get_async_db():
        await update_plants_from_csv(session)
        await verify_migration(session)
        break

    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())