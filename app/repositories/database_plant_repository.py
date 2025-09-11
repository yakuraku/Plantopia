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