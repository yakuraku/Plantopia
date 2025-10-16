import json
import tempfile
import os
from typing import Dict, Any, List, Optional, Tuple

from app.repositories.database_plant_repository import DatabasePlantRepository
from app.repositories.climate_repository import ClimateRepository
from app.utils.image_utils import image_to_base64
from app.utils.cache import cached
from app.schemas.request import RecommendationRequest, PlantScoreRequest
from app.core.config import settings
from app.schemas.response import (
    RecommendationResponse, PlantScoreResponse,
    PlantMedia, PlantFit, PlantSowing, PlantRecommendation, QuantifiedImpactResponse
)
from app.services.quantification_service import QuantificationService
from app.recommender.engine import (
    load_all_plants, select_environment, get_user_preferences,
    hard_filter, relax_if_needed, score_and_rank, assemble_output, category_diversity
)
from app.recommender.scoring import weights, calculate_scores


class RecommendationService:
    """Service for generating plant recommendations"""

    def __init__(self, plant_repository: DatabasePlantRepository, climate_repository: ClimateRepository):
        self.plant_repository = plant_repository
        self.climate_repository = climate_repository
        self.quantification_service = QuantificationService()
    
    @cached(ttl=600, prefix="recommendations")  # Cache for 10 minutes
    async def generate_recommendations(self, request: RecommendationRequest) -> Dict[str, Any]:
        """Generate plant recommendations based on user preferences.

        Args:
            request: Recommendation request with user preferences

        Returns:
            Dictionary with recommendations and metadata
        """
        # Create temporary file for user preferences
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as user_prefs_file:
            json.dump(request.user_preferences.dict(), user_prefs_file)
            user_prefs_path = user_prefs_file.name
        
        try:
            # Load all plants
            all_plants = await self.plant_repository.get_all_plants()
            
            # Get latest climate for suburb or use default
            climate_entry = await self.climate_repository.get_latest_climate_by_suburb(request.suburb)
            
            # Convert to legacy format for compatibility
            climate_data = {}
            if climate_entry:
                climate_data[request.suburb] = {
                    "temperature": climate_entry.get("weather", {}).get("temperature_current"),
                    "humidity": climate_entry.get("weather", {}).get("humidity"),
                    "rainfall": climate_entry.get("weather", {}).get("rainfall"),
                    "uv_index": climate_entry.get("uv", {}).get("index"),
                    "air_quality": climate_entry.get("air_quality", {}).get("aqi")
                }
            
            # Select environment
            env = select_environment(
                request.suburb, 
                climate_data, 
                cli_override_climate_zone=request.climate_zone
            )
            
            # Load user preferences
            user_prefs = get_user_preferences(user_prefs_path)
            
            # Filter plants
            eligible_plants = hard_filter(all_plants, user_prefs, env)
            
            # Relax filters if needed
            final_candidates = relax_if_needed(
                eligible_plants, all_plants, user_prefs, env, request.n
            )
            
            # Score and rank
            scored_plants = score_and_rank(final_candidates, user_prefs, env, weights)
            
            # Apply diversity cap
            diverse_plants = category_diversity(
                scored_plants, max_per_cat=2, target_count=request.n
            )
            
            # Take top N
            top_plants = diverse_plants[:request.n]
            
            # Assemble output
            output = assemble_output(top_plants, user_prefs, env, [])
            
            # Enhance with images and plant IDs
            output = await self._enhance_recommendations_with_images(output)
            
            # Add metadata
            output["suburb"] = request.suburb
            output["climate_zone"] = env["climate_zone"]
            output["month_now"] = env["month_now"]
            
            return output
            
        finally:
            # Clean up temporary file
            if os.path.exists(user_prefs_path):
                os.unlink(user_prefs_path)
    
    async def score_plant(self, request: PlantScoreRequest) -> PlantScoreResponse:
        """Score a specific plant based on user preferences.
        
        Args:
            request: Plant score request
            
        Returns:
            PlantScoreResponse with scoring details
        """
        # Find the plant
        plant = await self.plant_repository.find_plant_by_name(request.plant_name)
        if not plant:
            raise ValueError(f"Plant '{request.plant_name}' not found")
        
        # Create temporary file for user preferences
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as user_prefs_file:
            json.dump(request.user_preferences.dict(), user_prefs_file)
            user_prefs_path = user_prefs_file.name
        
        try:
            # Get latest climate for suburb or use default
            climate_entry = await self.climate_repository.get_latest_climate_by_suburb(request.suburb)
            
            # Convert to legacy format for compatibility
            climate_data = {}
            if climate_entry:
                climate_data[request.suburb] = {
                    "temperature": climate_entry.get("weather", {}).get("temperature_current"),
                    "humidity": climate_entry.get("weather", {}).get("humidity"),
                    "rainfall": climate_entry.get("weather", {}).get("rainfall"),
                    "uv_index": climate_entry.get("uv", {}).get("index"),
                    "air_quality": climate_entry.get("air_quality", {}).get("aqi")
                }
            
            # Select environment
            env = select_environment(
                request.suburb,
                climate_data,
                cli_override_climate_zone=request.climate_zone
            )
            
            # Load user preferences
            user_prefs = get_user_preferences(user_prefs_path)
            
            # Calculate score
            score, breakdown = calculate_scores(plant, user_prefs, env)
            
            # Get sowing information
            sowing_data = plant.get("sowing_months_by_climate")
            if sowing_data is None:
                sowing_data = {}
            sowing_months = sowing_data.get(env["climate_zone"], [])
            season_label = "Start now" if env["month_now"] in sowing_months else "Plan ahead"
            
            # Prepare media
            image_path = plant.get("image_path", "")
            image_base64 = image_to_base64(image_path)
            
            # Create response
            return PlantScoreResponse(
                plant_name=plant.get("plant_name"),
                scientific_name=plant.get("scientific_name"),
                plant_category=plant.get("plant_category"),
                score=round(score, 1),
                score_breakdown={k: round(v, 3) for k, v in breakdown.items()},
                fit=PlantFit(
                    sun_need=plant.get("sun_need"),
                    time_to_maturity_days=plant.get("time_to_maturity_days"),
                    maintainability=plant.get("maintainability"),
                    container_ok=plant.get("container_ok"),
                    indoor_ok=plant.get("indoor_ok"),
                    habit=plant.get("habit")
                ),
                sowing=PlantSowing(
                    climate_zone=env["climate_zone"],
                    months=sowing_months,
                    method=plant.get("sowing_method"),
                    depth_mm=plant.get("sowing_depth_mm"),
                    spacing_cm=plant.get("spacing_cm"),
                    season_label=season_label
                ),
                media=PlantMedia(
                    image_path=image_path,
                    image_base64=image_base64,
                    has_image=bool(image_base64)
                ),
                suburb=request.suburb,
                climate_zone=env["climate_zone"],
                month_now=env["month_now"]
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(user_prefs_path):
                os.unlink(user_prefs_path)
    
    async def _enhance_recommendations_with_images(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Add GCS image URLs, plant database IDs, and companion planting data to recommendations.

        Args:
            output: Recommendation output dictionary

        Returns:
            Enhanced output with GCS image URLs, plant IDs, and companion planting data
        """
        for recommendation in output.get("recommendations", []):
            plant_name = recommendation.get("plant_name", "")
            plant_category = recommendation.get("plant_category", "flower")
            scientific_name = recommendation.get("scientific_name", "")

            # Look up plant by name to get database ID and companion planting data
            plant = await self.plant_repository.find_plant_by_name(plant_name)
            if plant:
                recommendation["id"] = plant.get("id")  # Add database ID

                # Add companion planting data
                recommendation["beneficial_companions"] = plant.get("beneficial_companions") or ""
                recommendation["harmful_companions"] = plant.get("harmful_companions") or ""
                recommendation["neutral_companions"] = plant.get("neutral_companions") or ""

            # Generate GCS image URL
            image_url = self._generate_gcs_image_url(plant_name, plant_category, scientific_name)

            # Add media with GCS URL
            recommendation["media"] = {
                "image_url": image_url,
                "has_image": bool(image_url)
            }

        return output

    def _generate_gcs_image_url(self, plant_name: str, plant_category: str, scientific_name: str = None) -> str:
        """Generate primary GCS image URL for a plant.

        Args:
            plant_name: Name of the plant
            plant_category: Category of the plant
            scientific_name: Scientific name of the plant (optional)

        Returns:
            Primary GCS image URL
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
        if cleaned_scientific_name and cleaned_scientific_name.lower() != 'unknown':
            folder_name = f"{cleaned_plant_name}_{cleaned_scientific_name}"
        else:
            folder_name = f"{cleaned_plant_name}_unknown"

        # Return the first image URL
        return f"{settings.GCS_BUCKET_URL}/{category_folder}/{folder_name}/{folder_name}_1.jpg"