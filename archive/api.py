from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import tempfile
import os
import base64

from recommender.engine import load_all_plants, select_environment, get_user_preferences, hard_filter, relax_if_needed, score_and_rank, assemble_output, category_diversity
from recommender.scoring import weights, calculate_scores

# Google Drive configuration
DRIVE_BASE_URL = "https://drive.google.com/uc?export=view&id="
DRIVE_FOLDERS = {
    "flower": "1ZcE9R3FMvZa5TRp8HfAHo-K7dAD5IfmL",
    "herb": "1aVMw8n51wCndrlUb8xG5cRjsMvBnON7n", 
    "vegetable": "1rmv-7k70qL_fR1efsKa_t28I22pLKzf_"
}

# Category mapping for backwards compatibility
CATEGORY_MAPPING = {
    "flowers": "flower",
    "flower": "flower",
    "flower_plant_images": "flower",
    "herbs": "herb",
    "herb": "herb", 
    "herb_plant_images": "herb",
    "vegetables": "vegetable",
    "vegetable": "vegetable",
    "vegetable_plant_images": "vegetable"
}

def get_drive_image_url(category: str, image_name: Optional[str] = None) -> str:
    """
    Generate Google Drive image URL for a plant category
    
    Args:
        category: Plant category (flower, herb, vegetable)
        image_name: Specific image filename (optional)
    
    Returns:
        Google Drive URL for the image/folder
    """
    if not category:
        return ""
        
    # Normalize category
    normalized_category = CATEGORY_MAPPING.get(category.lower(), category.lower())
    folder_id = DRIVE_FOLDERS.get(normalized_category)
    
    if not folder_id:
        print(f"No Google Drive folder found for category: {category}")
        return ""
        
    # For now, return folder URL
    # TODO: Implement specific file mapping when needed
    if image_name:
        print(f"Requested specific image: {image_name} from category: {category}")
    
    return f"{DRIVE_BASE_URL}{folder_id}"

def get_drive_thumbnail_url(category: str, size: str = "s220") -> str:
    """
    Generate Google Drive thumbnail URL for a plant category
    
    Args:
        category: Plant category (flower, herb, vegetable)
        size: Thumbnail size (s150, s220, s320, etc.)
    
    Returns:
        Google Drive thumbnail URL
    """
    if not category:
        return ""
        
    normalized_category = CATEGORY_MAPPING.get(category.lower(), category.lower())
    folder_id = DRIVE_FOLDERS.get(normalized_category)
    
    if not folder_id:
        return ""
    
    return f"https://drive.google.com/thumbnail?id={folder_id}&sz={size}"

def get_plant_categories() -> List[str]:
    """Get all available plant categories"""
    return list(DRIVE_FOLDERS.keys())

def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string (DEPRECATED - now using Google Drive)."""
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
    version="1.0.0",
    root_path="/api"
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

class PlantScoreRequest(BaseModel):
    plant_name: str
    suburb: str = "Richmond"
    climate_zone: Optional[str] = None
    user_preferences: UserRequest

@app.get("/")
async def root():
    return {"message": "Plantopia Recommendation Engine API", "status": "working", "version": "1.0.0", "debug": "API root endpoint hit successfully"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "plantopia-api", "debug": "Health check endpoint hit successfully"}

@app.get("/test")
async def test():
    return {"message": "Test endpoint working", "debug": "Test route is accessible"}

@app.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    try:
        # Create temporary files for user preferences and climate data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as user_prefs_file:
            json.dump(request.user_preferences.dict(), user_prefs_file)
            user_prefs_path = user_prefs_file.name
        
        # Load plant data (use absolute paths for serverless environment)
        base_path = os.path.dirname(os.path.abspath(__file__))
        csv_paths = {
            "flower": os.path.join(base_path, "flower_plants_data.csv"),
            "herb": os.path.join(base_path, "herbs_plants_data.csv"),
            "vegetable": os.path.join(base_path, "vegetable_plants_data.csv")
        }
        
        all_plants = load_all_plants(csv_paths)
        
        # Load climate data (use absolute path for serverless environment)
        base_path = os.path.dirname(os.path.abspath(__file__))
        climate_file_path = os.path.join(base_path, "climate_data.json")
        with open(climate_file_path, 'r', encoding='utf-8') as f:
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
        
        # Convert image paths to Google Drive URLs
        for recommendation in output.get("recommendations", []):
            plant_category = recommendation.get("plant_category", "")
            
            # Generate Google Drive URLs
            drive_url = get_drive_image_url(plant_category)
            drive_thumbnail = get_drive_thumbnail_url(plant_category)
            
            # Update media object with Google Drive URLs
            recommendation["media"] = {
                "image_path": drive_url,  # Google Drive URL
                "image_base64": "",  # No longer using base64
                "drive_url": drive_url,  # Full resolution Google Drive URL
                "drive_thumbnail": drive_thumbnail,  # Thumbnail URL
                "has_image": bool(drive_url)
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

@app.get("/plants")
async def get_all_plants():
    """
    Get all plants from the database (vegetables, herbs, and flowers).
    Returns all plant data with images converted to base64.
    """
    try:
        # Load plant data from all CSV files (use absolute paths for serverless environment)
        base_path = os.path.dirname(os.path.abspath(__file__))
        csv_paths = {
            "flower": os.path.join(base_path, "flower_plants_data.csv"),
            "herb": os.path.join(base_path, "herbs_plants_data.csv"),
            "vegetable": os.path.join(base_path, "vegetable_plants_data.csv")
        }
        
        all_plants = load_all_plants(csv_paths)
        
        # Convert image paths to Google Drive URLs for each plant
        for plant in all_plants:
            plant_category = plant.get("plant_category", "")
            
            # Generate Google Drive URLs
            drive_url = get_drive_image_url(plant_category)
            drive_thumbnail = get_drive_thumbnail_url(plant_category)
            
            # Update plant object with Google Drive URLs
            plant["media"] = {
                "image_path": drive_url,  # Google Drive URL
                "image_base64": "",  # No longer using base64
                "drive_url": drive_url,  # Full resolution Google Drive URL
                "drive_thumbnail": drive_thumbnail,  # Thumbnail URL
                "has_image": bool(drive_url)
            }
        
        return {
            "plants": all_plants,
            "total_count": len(all_plants)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading plants: {str(e)}")

@app.post("/plant-score")
async def get_plant_score(request: PlantScoreRequest):
    try:
        # Create temporary files for user preferences
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as user_prefs_file:
            json.dump(request.user_preferences.dict(), user_prefs_file)
            user_prefs_path = user_prefs_file.name
        
        # Load plant data (use absolute paths for serverless environment)
        base_path = os.path.dirname(os.path.abspath(__file__))
        csv_paths = {
            "flower": os.path.join(base_path, "flower_plants_data.csv"),
            "herb": os.path.join(base_path, "herbs_plants_data.csv"),
            "vegetable": os.path.join(base_path, "vegetable_plants_data.csv")
        }
        
        all_plants = load_all_plants(csv_paths)
        
        # Find the specific plant
        target_plant = None
        plant_name_lower = request.plant_name.lower().strip()
        
        for plant in all_plants:
            plant_name = plant.get("plant_name", "").lower().strip()
            scientific_name = plant.get("scientific_name", "").lower().strip()
            
            if (plant_name == plant_name_lower or 
                scientific_name == plant_name_lower or
                plant_name_lower in plant_name or
                plant_name_lower in scientific_name):
                target_plant = plant
                break
        
        if not target_plant:
            raise HTTPException(status_code=404, detail=f"Plant '{request.plant_name}' not found")
        
        # Load climate data (use absolute path for serverless environment)
        base_path = os.path.dirname(os.path.abspath(__file__))
        climate_file_path = os.path.join(base_path, "climate_data.json")
        with open(climate_file_path, 'r', encoding='utf-8') as f:
            climate_data = json.load(f)
        
        # Select environment
        env = select_environment(request.suburb, climate_data, cli_override_climate_zone=request.climate_zone)
        
        # Load user preferences
        user_prefs = get_user_preferences(user_prefs_path)
        
        # Calculate score for the specific plant
        score, breakdown = calculate_scores(target_plant, user_prefs, env)
        
        # Get sowing information
        sowing_months = target_plant.get("sowing_months_by_climate", {}).get(env["climate_zone"], [])
        season_label = "Start now" if env["month_now"] in sowing_months else "Plan ahead"
        
        # Generate Google Drive URLs for the plant
        plant_category = target_plant.get("plant_category", "")
        drive_url = get_drive_image_url(plant_category)
        drive_thumbnail = get_drive_thumbnail_url(plant_category)
        
        # Assemble response
        result = {
            "plant_name": target_plant.get("plant_name"),
            "scientific_name": target_plant.get("scientific_name"),
            "plant_category": target_plant.get("plant_category"),
            "score": round(score, 1),
            "score_breakdown": {k: round(v, 3) for k, v in breakdown.items()},
            "fit": {
                "sun_need": target_plant.get("sun_need"),
                "time_to_maturity_days": target_plant.get("time_to_maturity_days"),
                "maintainability": target_plant.get("maintainability"),
                "container_ok": target_plant.get("container_ok"),
                "indoor_ok": target_plant.get("indoor_ok"),
                "habit": target_plant.get("habit")
            },
            "sowing": {
                "climate_zone": env["climate_zone"],
                "months": sowing_months,
                "method": target_plant.get("sowing_method"),
                "depth_mm": target_plant.get("sowing_depth_mm"),
                "spacing_cm": target_plant.get("spacing_cm"),
                "season_label": season_label
            },
            "media": {
                "image_path": drive_url,  # Google Drive URL
                "image_base64": "",  # No longer using base64
                "drive_url": drive_url,  # Full resolution Google Drive URL
                "drive_thumbnail": drive_thumbnail,  # Thumbnail URL
                "has_image": bool(drive_url)
            },
            "suburb": request.suburb,
            "climate_zone": env["climate_zone"],
            "month_now": env["month_now"]
        }
        
        # Clean up temporary file
        os.unlink(user_prefs_path)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        # Clean up temporary file if it exists
        if 'user_prefs_path' in locals():
            try:
                os.unlink(user_prefs_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# For Vercel serverless deployment
# Export the FastAPI app as the handler
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)