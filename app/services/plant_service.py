from typing import List, Dict, Any, Optional

from app.repositories.plant_repository import PlantRepository
from app.utils.image_utils import image_to_base64
from app.schemas.response import PlantMedia, AllPlantsResponse


class PlantService:
    """Service for plant-related operations"""
    
    def __init__(self, plant_repository: PlantRepository):
        self.plant_repository = plant_repository
    
    def get_all_plants_with_images(self) -> AllPlantsResponse:
        """Get all plants with base64 encoded images.
        
        Returns:
            AllPlantsResponse with all plants and images
        """
        plants = self.plant_repository.load_all_plants()
        
        # Add base64 images to each plant
        for plant in plants:
            image_path = plant.get("image_path", "")
            base64_image = image_to_base64(image_path)
            
            plant["media"] = {
                "image_path": image_path,
                "image_base64": base64_image,
                "has_image": bool(base64_image)
            }
        
        return AllPlantsResponse(
            plants=plants,
            total_count=len(plants)
        )
    
    def find_plant_with_details(self, plant_name: str) -> Optional[Dict[str, Any]]:
        """Find a plant by name and include all details.
        
        Args:
            plant_name: Name of the plant
            
        Returns:
            Plant dictionary with full details or None
        """
        plant = self.plant_repository.find_plant_by_name(plant_name)
        
        if plant:
            # Add image data
            image_path = plant.get("image_path", "")
            base64_image = image_to_base64(image_path)
            
            plant["media"] = {
                "image_path": image_path,
                "image_base64": base64_image,
                "has_image": bool(base64_image)
            }
        
        return plant
    
    def get_plants_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all plants of a specific category.
        
        Args:
            category: Plant category (flower, herb, vegetable)
            
        Returns:
            List of plants in the category
        """
        return self.plant_repository.get_plants_by_category(category)