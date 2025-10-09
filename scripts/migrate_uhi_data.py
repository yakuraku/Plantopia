#!/usr/bin/env python3
"""
Migration script to add Urban Heat Island data to suburbs table
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import get_async_db, async_engine
from app.models.database import Base, Suburb
from sqlalchemy.ext.asyncio import AsyncSession


async def add_heat_columns():
    """Add heat columns to suburbs table if they don't exist"""
    async with async_engine.begin() as conn:
        # Check if columns already exist
        result = await conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='suburbs'
            AND column_name IN ('suburb_heat_category', 'suburb_heat_intensity')
        """))
        existing_columns = {row[0] for row in result}

        # Add columns if they don't exist
        if 'suburb_heat_category' not in existing_columns:
            await conn.execute(text("""
                ALTER TABLE suburbs
                ADD COLUMN suburb_heat_category VARCHAR(50)
            """))
            print("Added suburb_heat_category column")

        if 'suburb_heat_intensity' not in existing_columns:
            await conn.execute(text("""
                ALTER TABLE suburbs
                ADD COLUMN suburb_heat_intensity FLOAT
            """))
            print("Added suburb_heat_intensity column")


async def load_uhi_data():
    """Load UHI data from JSON file"""
    uhi_file = Path(__file__).parent.parent / "app" / "static" / "uhi" / "melbourne_heat_data.json"

    if not uhi_file.exists():
        print(f"Error: UHI data file not found at {uhi_file}")
        return None

    with open(uhi_file, 'r') as f:
        data = json.load(f)

    return data


def normalize_suburb_name(name):
    """Normalize suburb name for matching"""
    # Remove common suffixes and normalize
    name = name.lower().strip()
    # Remove state suffixes
    name = name.replace(' (vic.)', '').replace(' (vic)', '')
    # Remove directional suffixes for matching
    for suffix in [' north', ' south', ' east', ' west', ' central']:
        if name.endswith(suffix):
            base_name = name[:-len(suffix)]
            return [name, base_name]  # Return both versions
    return [name]


async def update_suburbs_with_heat_data(session: AsyncSession, uhi_data):
    """Update suburbs with heat data"""
    updated_count = 0
    not_found = []

    # Create a mapping of normalized names to heat data
    heat_map = {}
    for suburb_data in uhi_data['suburbs']:
        original_name = suburb_data['name']
        normalized_names = normalize_suburb_name(original_name)
        for norm_name in normalized_names:
            heat_map[norm_name] = {
                'category': suburb_data['heat']['category'],
                'intensity': suburb_data['heat']['intensity'],
                'original_name': original_name
            }

    # Get all suburbs from database
    result = await session.execute(text("SELECT id, name FROM suburbs"))
    suburbs = result.fetchall()

    for suburb_id, suburb_name in suburbs:
        normalized_names = normalize_suburb_name(suburb_name)
        heat_data = None

        # Try to find heat data for this suburb
        for norm_name in normalized_names:
            if norm_name in heat_map:
                heat_data = heat_map[norm_name]
                break

        if heat_data:
            # Update suburb with heat data
            await session.execute(
                text("""
                    UPDATE suburbs
                    SET suburb_heat_category = :category,
                        suburb_heat_intensity = :intensity,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """),
                {
                    'category': heat_data['category'],
                    'intensity': heat_data['intensity'],
                    'id': suburb_id
                }
            )
            updated_count += 1
            print(f"Updated {suburb_name} -> {heat_data['category']} ({heat_data['intensity']}°C)")
        else:
            not_found.append(suburb_name)

    await session.commit()

    print(f"\nSummary:")
    print(f"Updated {updated_count} suburbs with heat data")
    if not_found:
        print(f"Could not find heat data for {len(not_found)} suburbs:")
        for name in not_found[:10]:  # Show first 10
            print(f"  - {name}")
        if len(not_found) > 10:
            print(f"  ... and {len(not_found) - 10} more")


async def main():
    """Main migration function"""
    print("Starting UHI data migration...")

    # Step 1: Add columns if needed
    print("\nStep 1: Adding heat columns to suburbs table...")
    await add_heat_columns()

    # Step 2: Load UHI data
    print("\nStep 2: Loading UHI data...")
    uhi_data = await load_uhi_data()
    if not uhi_data:
        return

    print(f"Loaded data for {len(uhi_data['suburbs'])} suburbs")

    # Step 3: Update suburbs with heat data
    print("\nStep 3: Updating suburbs with heat data...")
    async for session in get_async_db():
        await update_suburbs_with_heat_data(session, uhi_data)
        break

    print("\nMigration completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())