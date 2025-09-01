from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import tempfile
import os
import base64

from recommender.engine import load_all_plants, select_environment, get_user_preferences, hard_filter, relax_if_needed, score_and_rank, assemble_output, category_diversity
from recommender.scoring import weights

def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string."""
    try:
        if not image_path or not os.path.exists(image_path):
            return ""
        
        with open(image_path, "rb") as image_file:
            # Read image and encode to base64
            image_data = image_file.read()
            base64_string = base64.b64encode(image_data).decode('utf-8')
            
            # Determine MIME type based on file extension
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif file_ext == '.png':
                mime_type = 'image/png'
            elif file_ext == '.gif':
                mime_type = 'image/gif'
            else:
                mime_type = 'image/jpeg'  # default
            
            return f"data:{mime_type};base64,{base64_string}"
    except Exception as e:
        print(f"Error converting image {image_path} to base64: {e}")
        return ""

app = FastAPI(
    title="Plantopia Recommendation Engine API",
    description="API for the Plantopia plant recommendation engine",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class SitePreferences(BaseModel):
    location_type: str = "balcony"
    area_m2: float = 2.0
    sun_exposure: str = "part_sun"
    wind_exposure: str = "moderate"
    containers: bool = True
    container_sizes: List[str] = ["small", "medium"]

class UserPreferences(BaseModel):
    goal: str = "mixed"
    edible_types: List[str] = ["herbs", "leafy"]
    ornamental_types: List[str] = ["flowers"]
    colors: List[str] = ["purple", "white"]
    fragrant: bool = True
    maintainability: str = "low"
    watering: str = "medium"
    time_to_results: str = "quick"
    season_intent: str = "start_now"
    pollen_sensitive: bool = False

class PracticalPreferences(BaseModel):
    budget: str = "medium"
    has_basic_tools: bool = True
    organic_only: bool = False

class EnvironmentPreferences(BaseModel):
    climate_zone: str = "temperate"
    month_now: str = ""
    uv_index: float = 0.0
    temperature_c: float = 8.0
    humidity_pct: int = 75
    wind_speed_kph: int = 15

class UserRequest(BaseModel):
    user_id: str = "anon_mvp"
    site: SitePreferences = SitePreferences()
    preferences: UserPreferences = UserPreferences()
    practical: PracticalPreferences = PracticalPreferences()
    environment: EnvironmentPreferences = EnvironmentPreferences()

class RecommendationRequest(BaseModel):
    suburb: str = "Richmond"
    n: int = 5
    climate_zone: Optional[str] = None
    user_preferences: UserRequest

@app.get("/")
async def root():
    return {"message": "Plantopia Recommendation Engine API"}

@app.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    try:
        # Create temporary files for user preferences and climate data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as user_prefs_file:
            json.dump(request.user_preferences.dict(), user_prefs_file)
            user_prefs_path = user_prefs_file.name
        
        # Load plant data
        csv_paths = {
            "flower": "flower_plants_data.csv",
            "herb": "herbs_plants_data.csv",
            "vegetable": "vegetable_plants_data.csv"
        }
        
        all_plants = load_all_plants(csv_paths)
        
        # Load climate data
        with open("climate_data.json", 'r', encoding='utf-8') as f:
            climate_data = json.load(f)
        
        # Select environment
        env = select_environment(request.suburb, climate_data, cli_override_climate_zone=request.climate_zone)
        
        # Load user preferences
        user_prefs = get_user_preferences(user_prefs_path)
        
        # Filter plants
        eligible_plants = hard_filter(all_plants, user_prefs, env)
        
        # Relax filters if needed
        final_candidates = relax_if_needed(eligible_plants, all_plants, user_prefs, env, request.n)
        
        # Score and rank
        scored_plants = score_and_rank(final_candidates, user_prefs, env, weights)
        
        # Apply diversity cap but ensure we reach target count
        diverse_plants = category_diversity(scored_plants, max_per_cat=2, target_count=request.n)
        
        # Take top N
        top_plants = diverse_plants[:request.n]
        
        # Assemble output
        output = assemble_output(top_plants, user_prefs, env, [])
        
        # Convert image paths to base64
        for recommendation in output.get("recommendations", []):
            if "media" in recommendation and "image_path" in recommendation["media"]:
                image_path = recommendation["media"]["image_path"]
                base64_image = image_to_base64(image_path)
                
                # Update media object with both path and base64
                recommendation["media"] = {
                    "image_path": image_path,  # Keep original path for reference
                    "image_base64": base64_image,  # Add base64 data
                    "has_image": bool(base64_image)
                }
        
        # Add suburb and climate info
        output["suburb"] = request.suburb
        output["climate_zone"] = env["climate_zone"]
        output["month_now"] = env["month_now"]
        
        # Clean up temporary file
        os.unlink(user_prefs_path)
        
        return output
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'user_prefs_path' in locals():
            try:
                os.unlink(user_prefs_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)