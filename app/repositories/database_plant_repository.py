"""
Database-based plant repository using SQLAlchemy
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from app.models.database import Plant
from app.core.config import settings


class DatabasePlantRepository:
    """Repository for managing plant data from database"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_plants(self) -> List[Dict[str, Any]]:
        """Get all plants from database.
        
        Returns:
            List of plant dictionaries
        """
        result = await self.db.execute(select(Plant))
        plants = result.scalars().all()
        
        return [self._plant_to_dict(plant) for plant in plants]
    
    async def find_plant_by_name(self, plant_name: str) -> Optional[Dict[str, Any]]:
        """Find a specific plant by name.

        Args:
            plant_name: Name of the plant to find

        Returns:
            Plant dictionary or None if not found
        """
        plant_name_lower = plant_name.lower().strip()

        query = select(Plant).where(
            or_(
                func.lower(Plant.plant_name) == plant_name_lower,
                func.lower(Plant.scientific_name) == plant_name_lower,
                func.lower(Plant.plant_name).contains(plant_name_lower),
                func.lower(Plant.scientific_name).contains(plant_name_lower)
            )
        )

        result = await self.db.execute(query)
        plant = result.scalar_one_or_none()

        return self._plant_to_dict(plant) if plant else None

    async def get_plant_object_by_name(self, plant_name: str) -> Optional[Plant]:
        """Get Plant object (not dictionary) by name for services that need the SQLAlchemy model.

        This method is specifically for services like quantification_service that expect
        a Plant object with attributes, not a dictionary with keys.

        Args:
            plant_name: Name of the plant to find

        Returns:
            Plant SQLAlchemy object or None if not found
        """
        plant_name_lower = plant_name.lower().strip()

        query = select(Plant).where(
            or_(
                func.lower(Plant.plant_name) == plant_name_lower,
                func.lower(Plant.scientific_name) == plant_name_lower,
                func.lower(Plant.plant_name).contains(plant_name_lower),
                func.lower(Plant.scientific_name).contains(plant_name_lower)
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()  # Return Plant object directly, not dictionary
    
    async def get_plants_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all plants of a specific category.
        
        Args:
            category: Plant category (flower, herb, vegetable)
            
        Returns:
            List of plant dictionaries
        """
        query = select(Plant).where(Plant.plant_category == category)
        result = await self.db.execute(query)
        plants = result.scalars().all()
        
        return [self._plant_to_dict(plant) for plant in plants]
    
    async def search_plants(
        self,
        search_term: Optional[str] = None,
        category: Optional[str] = None,
        water_requirements: Optional[str] = None,
        sunlight_requirements: Optional[str] = None,
        maintenance_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search plants with multiple filters.
        
        Args:
            search_term: Text to search in plant name or description
            category: Filter by category
            water_requirements: Filter by water needs
            sunlight_requirements: Filter by sunlight needs
            maintenance_level: Filter by maintenance level
            
        Returns:
            List of matching plant dictionaries
        """
        query = select(Plant)
        
        filters = []
        
        if search_term:
            search_lower = f"%{search_term.lower()}%"
            filters.append(
                or_(
                    func.lower(Plant.plant_name).like(search_lower),
                    func.lower(Plant.scientific_name).like(search_lower),
                    func.lower(Plant.description).like(search_lower)
                )
            )
        
        if category:
            filters.append(Plant.plant_category == category)
        
        if water_requirements:
            filters.append(Plant.water_requirements == water_requirements)
        
        if sunlight_requirements:
            filters.append(Plant.sunlight_requirements == sunlight_requirements)
        
        if maintenance_level:
            filters.append(Plant.maintenance_level == maintenance_level)
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await self.db.execute(query)
        plants = result.scalars().all()
        
        return [self._plant_to_dict(plant) for plant in plants]
    
    async def get_plant_by_id(self, plant_id: int) -> Optional[Dict[str, Any]]:
        """Get a plant by its database ID.
        
        Args:
            plant_id: Database ID of the plant
            
        Returns:
            Plant dictionary or None if not found
        """
        result = await self.db.execute(select(Plant).where(Plant.id == plant_id))
        plant = result.scalar_one_or_none()
        
        return self._plant_to_dict(plant) if plant else None
    
    async def count_plants_by_category(self) -> Dict[str, int]:
        """Get count of plants per category.

        Returns:
            Dictionary with category names as keys and counts as values
        """
        query = select(
            Plant.plant_category,
            func.count(Plant.id).label('count')
        ).group_by(Plant.plant_category)

        result = await self.db.execute(query)
        counts = result.all()

        return {row.plant_category: row.count for row in counts if row.plant_category}

    async def get_plants_paginated(
        self,
        page: int = 1,
        limit: int = 12,
        category: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get paginated plants with optional filters.

        Args:
            page: Page number (1-based)
            limit: Number of items per page
            category: Optional category filter
            search_term: Optional search term for name/scientific name/description

        Returns:
            Tuple of (plants list, total count)
        """
        # Build base query
        query = select(Plant)
        count_query = select(func.count(Plant.id))

        filters = []

        # Add search filter
        if search_term:
            search_lower = f"%{search_term.lower()}%"
            search_filter = or_(
                func.lower(Plant.plant_name).like(search_lower),
                func.lower(Plant.scientific_name).like(search_lower),
                func.lower(Plant.description).like(search_lower)
            )
            filters.append(search_filter)

        # Add category filter
        if category:
            filters.append(Plant.plant_category == category)

        # Apply filters to both queries
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get total count
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Execute paginated query
        result = await self.db.execute(query)
        plants = result.scalars().all()

        return [self._plant_to_dict(plant) for plant in plants], total_count

    async def count_plants(
        self,
        category: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> int:
        """Count plants with optional filters.

        Args:
            category: Optional category filter
            search_term: Optional search term

        Returns:
            Total count of matching plants
        """
        query = select(func.count(Plant.id))

        filters = []

        if search_term:
            search_lower = f"%{search_term.lower()}%"
            filters.append(
                or_(
                    func.lower(Plant.plant_name).like(search_lower),
                    func.lower(Plant.scientific_name).like(search_lower),
                    func.lower(Plant.description).like(search_lower)
                )
            )

        if category:
            filters.append(Plant.plant_category == category)

        if filters:
            query = query.where(and_(*filters))

        result = await self.db.execute(query)
        return result.scalar() or 0
    
    def _plant_to_dict(self, plant: Plant) -> Dict[str, Any]:
        """Convert Plant model to dictionary.
        
        Args:
            plant: Plant model instance
            
        Returns:
            Dictionary representation of plant
        """
        if not plant:
            return {}
        
        return {
            'id': plant.id,
            'plant_name': plant.plant_name,
            'scientific_name': plant.scientific_name,
            'plant_category': plant.plant_category,
            'water_requirements': plant.water_requirements,
            'sunlight_requirements': plant.sunlight_requirements,
            'soil_type': plant.soil_type,
            'growth_time': plant.growth_time,
            'maintenance_level': plant.maintenance_level,
            'climate_zone': plant.climate_zone,
            'mature_height': plant.mature_height,
            'mature_width': plant.mature_width,
            'flower_color': plant.flower_color,
            'flowering_season': plant.flowering_season,
            'description': plant.description,
            # New fields for recommendation engine
            'sun_need': plant.sun_need,
            'indoor_ok': plant.indoor_ok,
            'container_ok': plant.container_ok,
            'edible': plant.edible,
            'sowing_months_by_climate': plant.sowing_months_by_climate,
            'maintainability_score': plant.maintainability_score,
            'time_to_maturity_days': plant.time_to_maturity_days,
            'habit': plant.habit,
            'fragrant': plant.fragrant,
            'flower_colors': plant.flower_colors,
            'sowing_depth_mm': plant.sowing_depth_mm,
            'spacing_cm': plant.spacing_cm,
            'sowing_method': plant.sowing_method,
            'planting_tips': plant.planting_tips,
            'care_instructions': plant.care_instructions,
            'companion_plants': plant.companion_plants,
            'image_url': plant.image_url,
            'created_at': plant.created_at.isoformat() if plant.created_at else None,
            'updated_at': plant.updated_at.isoformat() if plant.updated_at else None
        }