"""
Script to update the image_url field in the database with GCS URLs
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from app.models.database import Plant
from app.core.config import settings
from app.services.plant_service import PlantService


async def update_plant_image_urls():
    """Update all plant records with GCS image URLs"""

    # Create database connection with async PostgreSQL driver
    # Replace postgresql:// with postgresql+asyncpg:// for async support
    async_db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(async_db_url)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create plant service instance (we just need the URL generation methods)
    plant_service = PlantService(None)

    async with async_session() as session:
        try:
            # Get all plants
            result = await session.execute(select(Plant))
            plants = result.scalars().all()

            print(f"Found {len(plants)} plants to update")

            updated_count = 0
            for plant in plants:
                # Generate the primary image URL
                image_url = plant_service.get_primary_image_url(
                    plant.plant_name,
                    plant.plant_category or "flower",
                    plant.scientific_name
                )

                if image_url:
                    # Update the plant record
                    plant.image_url = image_url
                    updated_count += 1
                    print(f"Updated {plant.plant_name}: {image_url}")
                else:
                    print(f"Could not generate URL for {plant.plant_name}")

            # Commit all changes
            await session.commit()
            print(f"\nSuccessfully updated {updated_count} plant records with image URLs")

        except Exception as e:
            print(f"Error updating image URLs: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


async def verify_image_urls():
    """Verify that image URLs were updated correctly"""

    # Use async PostgreSQL driver
    async_db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(async_db_url)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Count plants with and without image URLs
            result = await session.execute(
                select(Plant).where(Plant.image_url != None)
            )
            plants_with_urls = len(result.scalars().all())

            result = await session.execute(
                select(Plant).where(Plant.image_url == None)
            )
            plants_without_urls = len(result.scalars().all())

            print(f"\nVerification Results:")
            print(f"Plants with image URLs: {plants_with_urls}")
            print(f"Plants without image URLs: {plants_without_urls}")

            # Show a few sample URLs
            result = await session.execute(
                select(Plant).where(Plant.image_url != None).limit(5)
            )
            sample_plants = result.scalars().all()

            print(f"\nSample image URLs:")
            for plant in sample_plants:
                print(f"  {plant.plant_name}: {plant.image_url}")

        except Exception as e:
            print(f"Error verifying image URLs: {e}")
        finally:
            await engine.dispose()


def main():
    """Main function to run the migration"""
    print("Starting image URL migration...")
    print(f"GCS Bucket URL: {settings.GCS_BUCKET_URL}")
    print("-" * 50)

    # Run the update
    asyncio.run(update_plant_image_urls())

    # Verify the results
    asyncio.run(verify_image_urls())

    print("\nMigration complete!")


if __name__ == "__main__":
    main()