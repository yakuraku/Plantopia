import json
import tempfile
import os
from typing import Dict, Any, List, Optional, Tuple

from app.repositories.plant_repository import PlantRepository
from app.utils.image_utils import image_to_base64
from app.schemas.request import RecommendationRequest, PlantScoreRequest
from app.schemas.response import (
    RecommendationResponse, PlantScoreResponse, 
    PlantMedia, PlantFit, PlantSowing, PlantRecommendation
)
from app.recommender.engine import (
    load_all_plants, select_environment, get_user_preferences,
    hard_filter, relax_if_needed, score_and_rank, assemble_output, category_diversity
)
from app.recommender.scoring import weights, calculate_scores


class RecommendationService:
    """Service for generating plant recommendations"""
    
    def __init__(self, plant_repository: PlantRepository):
        self.plant_repository = plant_repository
    
    def generate_recommendations(self, request: RecommendationRequest) -> Dict[str, Any]:
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
            all_plants = self.plant_repository.load_all_plants()
            
            # Load climate data
            climate_data = self.plant_repository.load_climate_data()
            
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
            
            # Enhance with images
            output = self._enhance_recommendations_with_images(output)
            
            # Add metadata
            output["suburb"] = request.suburb
            output["climate_zone"] = env["climate_zone"]
            output["month_now"] = env["month_now"]
            
            return output
            
        finally:
            # Clean up temporary file
            if os.path.exists(user_prefs_path):
                os.unlink(user_prefs_path)
    
    def score_plant(self, request: PlantScoreRequest) -> PlantScoreResponse:
        """Score a specific plant based on user preferences.
        
        Args:
            request: Plant score request
            
        Returns:
            PlantScoreResponse with scoring details
        """
        # Find the plant
        plant = self.plant_repository.find_plant_by_name(request.plant_name)
        if not plant:
            raise ValueError(f"Plant '{request.plant_name}' not found")
        
        # Create temporary file for user preferences
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as user_prefs_file:
            json.dump(request.user_preferences.dict(), user_prefs_file)
            user_prefs_path = user_prefs_file.name
        
        try:
            # Load climate data
            climate_data = self.plant_repository.load_climate_data()
            
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
            sowing_months = plant.get("sowing_months_by_climate", {}).get(env["climate_zone"], [])
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
    
    def _enhance_recommendations_with_images(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Add base64 encoded images to recommendations.
        
        Args:
            output: Recommendation output dictionary
            
        Returns:
            Enhanced output with images
        """
        for recommendation in output.get("recommendations", []):
            if "media" in recommendation and "image_path" in recommendation["media"]:
                image_path = recommendation["media"]["image_path"]
                base64_image = image_to_base64(image_path)
                
                recommendation["media"] = {
                    "image_path": image_path,
                    "image_base64": base64_image,
                    "has_image": bool(base64_image)
                }
        
        return output