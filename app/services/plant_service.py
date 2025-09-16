from typing import List, Dict, Any, Optional
import re

from app.repositories.database_plant_repository import DatabasePlantRepository
from app.utils.image_utils import image_to_base64
from app.schemas.response import PlantMedia, AllPlantsResponse
from app.core.config import settings


class PlantService:
    """Service for plant-related operations"""

    def __init__(self, plant_repository: DatabasePlantRepository):
        self.plant_repository = plant_repository
    
    async def get_all_plants_with_images(self) -> AllPlantsResponse:
        """Get all plants with base64 encoded images.

        Returns:
            AllPlantsResponse with all plants and images
        """
        plants = await self.plant_repository.get_all_plants()

        # Add base64 images and GCS URL to each plant
        for plant in plants:
            image_path = plant.get("image_path", "")
            base64_image = image_to_base64(image_path)

            # Generate GCS image URL with cleaned special characters
            plant_name = plant.get("plant_name", "")
            plant_category = plant.get("plant_category", "flower")
            scientific_name = plant.get("scientific_name", "")

            # Use the same method that generates clean URLs
            image_url = self.get_primary_image_url(plant_name, plant_category, scientific_name)

            plant["media"] = {
                "image_url": image_url,  # Add the cleaned URL
                "image_path": image_path,
                "image_base64": base64_image,
                "has_image": bool(base64_image) or bool(image_url)
            }

        return AllPlantsResponse(
            plants=plants,
            total_count=len(plants)
        )
    
    async def find_plant_with_details(self, plant_name: str) -> Optional[Dict[str, Any]]:
        """Find a plant by name and include all details.
        
        Args:
            plant_name: Name of the plant
            
        Returns:
            Plant dictionary with full details or None
        """
        plant = await self.plant_repository.find_plant_by_name(plant_name)
        
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
    
    async def get_plants_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all plants of a specific category.

        Args:
            category: Plant category (flower, herb, vegetable)

        Returns:
            List of plants in the category
        """
        return await self.plant_repository.get_plants_by_category(category)

    def generate_gcs_image_urls(self, plant_name: str, plant_category: str, scientific_name: str = None) -> List[str]:
        """Generate GCS image URLs for a plant.

        Args:
            plant_name: Name of the plant
            plant_category: Category of the plant (flower, herb, vegetable)
            scientific_name: Scientific name of the plant (optional)

        Returns:
            List of GCS URLs for the plant images
        """
        # Map category to folder name
        category_folder = f"{plant_category.lower()}_plant_images"

        # Clean plant name to match GCS folder naming
        # GCS folders remove these special characters: ' ( ) , . / : &
        special_chars_to_remove = ["'", "(", ")", ",", ".", "/", ":", "&"]
        cleaned_plant_name = plant_name
        for char in special_chars_to_remove:
            cleaned_plant_name = cleaned_plant_name.replace(char, "")
        cleaned_plant_name = cleaned_plant_name.strip()

        cleaned_scientific_name = scientific_name
        if scientific_name:
            for char in special_chars_to_remove:
                cleaned_scientific_name = cleaned_scientific_name.replace(char, "")
            cleaned_scientific_name = cleaned_scientific_name.strip()

        # The folder name format is: "Plant Name_Scientific Name"
        # If scientific name is not provided or is 'unknown', use just the plant name
        if cleaned_scientific_name and cleaned_scientific_name.lower() != 'unknown':
            folder_name = f"{cleaned_plant_name}_{cleaned_scientific_name}"
        else:
            # For cases where scientific name is unknown, try just the plant name
            folder_name = f"{cleaned_plant_name}_unknown"

        # Generate URLs for potential multiple images (1-4)
        base_url = f"{settings.GCS_BUCKET_URL}/{category_folder}/{folder_name}"

        # Most plants have 2-4 images, generate URLs for all possibilities
        # Frontend can handle 404s for non-existent images
        image_urls = []
        for i in range(1, 5):  # Generate URLs for _1.jpg to _4.jpg
            image_url = f"{base_url}/{folder_name}_{i}.jpg"
            image_urls.append(image_url)

        return image_urls

    def get_primary_image_url(self, plant_name: str, plant_category: str, scientific_name: str = None) -> str:
        """Get the primary (first) image URL for a plant.

        Args:
            plant_name: Name of the plant
            plant_category: Category of the plant
            scientific_name: Scientific name of the plant (optional)

        Returns:
            URL of the first image
        """
        urls = self.generate_gcs_image_urls(plant_name, plant_category, scientific_name)
        return urls[0] if urls else None

    async def get_plant_image_url(self, plant_id: int) -> Optional[str]:
        """Get the primary GCS image URL for a specific plant by ID.

        Args:
            plant_id: ID of the plant

        Returns:
            Primary GCS image URL or None if plant not found
        """
        plant = await self.plant_repository.get_plant_by_id(plant_id)

        if not plant:
            return None

        # If plant already has image_url in database, return it
        if plant.get("image_url"):
            return plant["image_url"]

        # Otherwise generate it from plant name and category
        return self.get_primary_image_url(
            plant["plant_name"],
            plant.get("plant_category", "flower"),
            plant.get("scientific_name")
        )

    async def get_all_plant_image_urls(self, plant_id: int) -> Optional[List[str]]:
        """Get all GCS image URLs for a specific plant by ID.

        Args:
            plant_id: ID of the plant

        Returns:
            List of all GCS image URLs or None if plant not found
        """
        plant = await self.plant_repository.get_plant_by_id(plant_id)

        if not plant:
            return None

        # Generate all possible image URLs
        return self.generate_gcs_image_urls(
            plant["plant_name"],
            plant.get("plant_category", "flower"),
            plant.get("scientific_name")
        )