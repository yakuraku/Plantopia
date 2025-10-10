"""
Plant Growth Data Repository for managing plant growth data operations
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import PlantGrowthData


class PlantGrowthRepository:
    """Repository for managing plant growth data database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_plant_id(self, plant_id: int) -> Optional[PlantGrowthData]:
        """
        Get plant growth data by plant ID

        Args:
            plant_id: Plant ID

        Returns:
            PlantGrowthData instance or None if not found
        """
        query = select(PlantGrowthData).where(PlantGrowthData.plant_id == plant_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, plant_id: int, growth_data: Dict[str, Any]) -> PlantGrowthData:
        """
        Create new plant growth data

        Args:
            plant_id: Plant ID
            growth_data: Dictionary containing growth data

        Returns:
            Created PlantGrowthData instance
        """
        plant_growth = PlantGrowthData(
            plant_id=plant_id,
            requirements_checklist=growth_data['requirements_checklist'],
            setup_instructions=growth_data['setup_instructions'],
            growth_stages=growth_data['growth_stages'],
            care_tips=growth_data['care_tips'],
            data_source_info=growth_data.get('data_source_info'),
            last_updated=datetime.utcnow(),
            version=growth_data.get('version', '1.0')
        )

        self.db.add(plant_growth)
        await self.db.commit()
        await self.db.refresh(plant_growth)

        return plant_growth

    async def update(self, plant_id: int, growth_data: Dict[str, Any]) -> PlantGrowthData:
        """
        Update existing plant growth data

        Args:
            plant_id: Plant ID
            growth_data: Dictionary containing updated growth data

        Returns:
            Updated PlantGrowthData instance

        Raises:
            ValueError: If plant growth data not found
        """
        existing_data = await self.get_by_plant_id(plant_id)
        if not existing_data:
            raise ValueError(f"Plant growth data for plant_id {plant_id} not found")

        # Update fields
        existing_data.requirements_checklist = growth_data['requirements_checklist']
        existing_data.setup_instructions = growth_data['setup_instructions']
        existing_data.growth_stages = growth_data['growth_stages']
        existing_data.care_tips = growth_data['care_tips']
        existing_data.data_source_info = growth_data.get('data_source_info')
        existing_data.last_updated = datetime.utcnow()
        existing_data.version = growth_data.get('version', existing_data.version)

        await self.db.commit()
        await self.db.refresh(existing_data)

        return existing_data

    async def get_or_create(self, plant_id: int, growth_data: Dict[str, Any]) -> PlantGrowthData:
        """
        Get existing plant growth data or create if it doesn't exist

        Args:
            plant_id: Plant ID
            growth_data: Dictionary containing growth data

        Returns:
            PlantGrowthData instance
        """
        existing_data = await self.get_by_plant_id(plant_id)

        if existing_data:
            return existing_data

        return await self.create(plant_id, growth_data)

    async def delete(self, plant_id: int) -> bool:
        """
        Delete plant growth data

        Args:
            plant_id: Plant ID

        Returns:
            True if data was deleted, False if not found
        """
        existing_data = await self.get_by_plant_id(plant_id)

        if existing_data:
            await self.db.delete(existing_data)
            await self.db.commit()
            return True

        return False

    async def is_data_current(self, plant_id: int, max_age_days: int = 30) -> bool:
        """
        Check if plant growth data is current (not too old)

        Args:
            plant_id: Plant ID
            max_age_days: Maximum age in days before data is considered stale

        Returns:
            True if data is current, False otherwise
        """
        growth_data = await self.get_by_plant_id(plant_id)

        if not growth_data or not growth_data.last_updated:
            return False

        age_days = (datetime.utcnow() - growth_data.last_updated).days
        return age_days <= max_age_days
