"""
Plant Growth Service for managing plant growth data with AI generation
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.plant_growth_repository import PlantGrowthRepository
from app.repositories.climate_repository import ClimateRepository
from app.services.external_api_service import get_gemini_service
from app.models.database import Plant, Suburb
from sqlalchemy import select


logger = logging.getLogger(__name__)


class PlantGrowthService:
    """Service for managing plant growth data with AI-powered generation"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PlantGrowthRepository(db)
        self.climate_repository = ClimateRepository(db)
        self.gemini_service = get_gemini_service()

    async def _get_location_context(self, suburb_id: Optional[int]) -> Optional[Dict[str, Any]]:
        """
        Fetch location and climate data for context building.

        Args:
            suburb_id: Optional suburb ID

        Returns:
            Dictionary with location and climate context, or None if not available
        """
        if not suburb_id:
            return None

        try:
            # Get suburb details
            query = select(Suburb).where(Suburb.id == suburb_id)
            result = await self.db.execute(query)
            suburb = result.scalar_one_or_none()

            if not suburb:
                logger.warning(f"Suburb with ID {suburb_id} not found")
                return None

            # Get latest climate data
            climate_data = await self.climate_repository.get_latest_climate_by_suburb(suburb.name)

            location_context = {
                "location": f"{suburb.name}, {suburb.state}",
                "climate_zone": suburb.state or "VIC"
            }

            # Add heat category if available
            if suburb.suburb_heat_category:
                location_context["heat_category"] = suburb.suburb_heat_category

            # Add current climate data if available
            if climate_data:
                weather = climate_data.get("weather", {})
                uv = climate_data.get("uv", {})
                aqi = climate_data.get("air_quality", {})

                if weather.get("temperature_current"):
                    location_context["temperature"] = weather["temperature_current"]
                if weather.get("humidity"):
                    location_context["humidity"] = weather["humidity"]
                if uv.get("index"):
                    location_context["uv_index"] = uv["index"]
                if uv.get("category"):
                    location_context["uv_category"] = uv["category"]
                if aqi.get("aqi"):
                    location_context["aqi"] = aqi["aqi"]
                if aqi.get("category"):
                    location_context["aqi_category"] = aqi["category"]

            return location_context

        except Exception as e:
            logger.error(f"Error fetching location context: {e}")
            return None

    async def get_plant_by_id(self, plant_id: int) -> Optional[Plant]:
        """Get plant by ID"""
        query = select(Plant).where(Plant.id == plant_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_or_generate_growth_data(
        self,
        plant_id: int,
        user_data: Dict[str, Any],
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Get existing plant growth data or generate new data using Gemini API

        Args:
            plant_id: Plant ID
            user_data: User context data for personalized generation
            force_regenerate: If True, regenerate even if data exists

        Returns:
            Dictionary with growth data

        Raises:
            ValueError: If plant not found
        """
        # Check if data exists and is current
        if not force_regenerate:
            existing_data = await self.repository.get_by_plant_id(plant_id)
            if existing_data and await self.repository.is_data_current(plant_id):
                logger.info(f"Using cached growth data for plant_id {plant_id}")
                return {
                    "requirements_checklist": existing_data.requirements_checklist,
                    "setup_instructions": existing_data.setup_instructions,
                    "growth_stages": existing_data.growth_stages,
                    "care_tips": existing_data.care_tips,
                    "data_source_info": existing_data.data_source_info,
                    "cached": True
                }

        # Get plant details
        plant = await self.get_plant_by_id(plant_id)
        if not plant:
            raise ValueError(f"Plant with ID {plant_id} not found")

        # Convert plant model to dictionary for API
        plant_data = {
            "plant_name": plant.plant_name,
            "scientific_name": plant.scientific_name,
            "plant_category": plant.plant_category,
            "description": plant.description,
            "water_requirements": plant.water_requirements,
            "sunlight_requirements": plant.sunlight_requirements,
            "soil_type": plant.soil_type,
            "time_to_maturity_days": plant.time_to_maturity_days,
            "maintenance_level": plant.maintenance_level,
            "climate_zone": plant.climate_zone,
            "plant_spacing": plant.plant_spacing,
            "sowing_depth": plant.sowing_depth,
            "germination": plant.germination,
            "hardiness_life_cycle": plant.hardiness_life_cycle,
            "characteristics": plant.characteristics,
            "care_instructions": plant.care_instructions
        }

        # Fetch location and climate context if suburb_id provided
        suburb_id = user_data.get("suburb_id")
        location_context = await self._get_location_context(suburb_id)

        if location_context:
            logger.info(f"Using location context for plant_id {plant_id}: {location_context.get('location')}")
        else:
            logger.info(f"No location context available for plant_id {plant_id}")

        # Generate new data using Gemini API
        logger.info(f"Generating new growth data for plant_id {plant_id}")
        generated_data = await self.gemini_service.generate_complete_plant_data(
            plant_data,
            user_data,
            location_context
        )

        # Store in database
        await self.repository.get_or_create(plant_id, generated_data)

        generated_data["cached"] = False
        return generated_data

    async def get_requirements(self, plant_id: int) -> Dict[str, Any]:
        """
        Get requirements checklist for a plant

        Args:
            plant_id: Plant ID

        Returns:
            Dictionary with requirements checklist

        Raises:
            ValueError: If growth data not found
        """
        growth_data = await self.repository.get_by_plant_id(plant_id)
        if not growth_data:
            raise ValueError(f"No growth data found for plant_id {plant_id}. Generate data first.")

        return {
            "plant_id": plant_id,
            "requirements": growth_data.requirements_checklist
        }

    async def get_instructions(self, plant_id: int) -> Dict[str, Any]:
        """
        Get setup instructions for a plant

        Args:
            plant_id: Plant ID

        Returns:
            Dictionary with setup instructions

        Raises:
            ValueError: If growth data not found
        """
        growth_data = await self.repository.get_by_plant_id(plant_id)
        if not growth_data:
            raise ValueError(f"No growth data found for plant_id {plant_id}. Generate data first.")

        return {
            "plant_id": plant_id,
            "instructions": growth_data.setup_instructions
        }

    async def get_timeline(self, plant_id: int) -> Dict[str, Any]:
        """
        Get growth timeline for a plant

        Args:
            plant_id: Plant ID

        Returns:
            Dictionary with growth stages

        Raises:
            ValueError: If growth data not found
        """
        growth_data = await self.repository.get_by_plant_id(plant_id)
        if not growth_data:
            raise ValueError(f"No growth data found for plant_id {plant_id}. Generate data first.")

        # Calculate total days from stages
        total_days = 0
        if growth_data.growth_stages:
            total_days = max(
                stage.get("end_day", 0)
                for stage in growth_data.growth_stages
            )

        return {
            "plant_id": plant_id,
            "total_days": total_days,
            "stages": growth_data.growth_stages
        }

    async def get_care_tips_for_stage(self, plant_id: int, stage_name: str) -> Dict[str, Any]:
        """
        Get care tips for a specific growth stage

        Args:
            plant_id: Plant ID
            stage_name: Growth stage name

        Returns:
            Dictionary with stage-specific tips

        Raises:
            ValueError: If growth data not found
        """
        growth_data = await self.repository.get_by_plant_id(plant_id)
        if not growth_data:
            raise ValueError(f"No growth data found for plant_id {plant_id}. Generate data first.")

        # Find tips for the specific stage
        stage_tips = None
        if growth_data.care_tips:
            for tip_group in growth_data.care_tips:
                if tip_group.get("stage_name") == stage_name:
                    stage_tips = tip_group.get("tips", [])
                    break

        if stage_tips is None:
            stage_tips = []

        # Get stage info
        stage_info = None
        if growth_data.growth_stages:
            for stage in growth_data.growth_stages:
                if stage.get("stage_name") == stage_name:
                    stage_info = stage
                    break

        return {
            "plant_id": plant_id,
            "stage_name": stage_name,
            "tips": stage_tips,
            "stage_info": stage_info
        }

    async def invalidate_cache(self, plant_id: int) -> bool:
        """
        Invalidate (delete) cached growth data for a plant

        Args:
            plant_id: Plant ID

        Returns:
            True if data was deleted, False if not found
        """
        logger.info(f"Invalidating cache for plant_id {plant_id}")
        return await self.repository.delete(plant_id)

    async def refresh_growth_data(
        self,
        plant_id: int,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Force refresh of growth data (regenerate with AI)

        Args:
            plant_id: Plant ID
            user_data: User context data

        Returns:
            Newly generated growth data
        """
        return await self.get_or_generate_growth_data(
            plant_id,
            user_data,
            force_regenerate=True
        )
