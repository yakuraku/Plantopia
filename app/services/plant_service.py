from typing import List, Dict, Any, Optional
import re
import math

from app.repositories.database_plant_repository import DatabasePlantRepository
from app.utils.image_utils import image_to_base64
from app.utils.cache import cached
from app.schemas.response import PlantMedia, AllPlantsResponse, PaginatedPlantsResponse
from app.core.config import settings


class PlantService:
    """Service for plant-related operations"""

    def __init__(self, plant_repository: DatabasePlantRepository):
        self.plant_repository = plant_repository
    
    @cached(ttl=1800, prefix="plants")  # Cache for 30 minutes
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

    async def get_plants_paginated(
        self,
        page: int = 1,
        limit: int = 12,
        category: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> PaginatedPlantsResponse:
        """Get paginated plants with optional filters.

        Args:
            page: Page number (1-based)
            limit: Number of items per page
            category: Optional category filter (flower, herb, vegetable)
            search_term: Optional search term for name/scientific name/description

        Returns:
            PaginatedPlantsResponse with paginated plants and metadata
        """
        # Get paginated data from repository
        plants, total_count = await self.plant_repository.get_plants_paginated(
            page=page,
            limit=limit,
            category=category,
            search_term=search_term
        )

        # Add image URLs to each plant
        for plant in plants:
            plant_name = plant.get("plant_name", "")
            plant_category = plant.get("plant_category", "flower")
            scientific_name = plant.get("scientific_name", "")

            # Generate primary image URL
            image_url = self.get_primary_image_url(plant_name, plant_category, scientific_name)

            # Add media information
            plant["media"] = {
                "image_url": image_url,
                "image_path": plant.get("image_path", ""),
                "has_image": bool(image_url)
            }

        # Calculate pagination metadata
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1

        return PaginatedPlantsResponse(
            plants=plants,
            page=page,
            limit=limit,
            total=total_count,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )

    @cached(ttl=86400, prefix="companions")  # Cache for 24 hours (static data)
    async def get_plant_companions(self, plant_id: int) -> Optional[Dict[str, Any]]:
        """Get companion planting information for a specific plant.

        Args:
            plant_id: ID of the plant

        Returns:
            Dictionary containing companion planting data or None if plant not found
        """
        plant = await self.plant_repository.get_plant_by_id(plant_id)

        if not plant:
            return None

        # Parse companion data (they are comma-separated strings)
        def parse_companions(companion_str: Optional[str]) -> List[str]:
            """Parse companion string into list of plant names"""
            if not companion_str or companion_str.strip() == '':
                return []
            # Split by comma and strip whitespace
            return [c.strip() for c in companion_str.split(',') if c.strip()]

        return {
            "plant_id": plant_id,
            "plant_name": plant.get("plant_name"),
            "scientific_name": plant.get("scientific_name"),
            "plant_category": plant.get("plant_category"),
            "companion_planting": {
                "beneficial_companions": parse_companions(plant.get("beneficial_companions")),
                "harmful_companions": parse_companions(plant.get("harmful_companions")),
                "neutral_companions": parse_companions(plant.get("neutral_companions"))
            }
        }