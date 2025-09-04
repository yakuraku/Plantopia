from http.server import BaseHTTPRequestHandler
import json
import tempfile
import os
from typing import Optional, Dict, Any, List
from urllib.parse import parse_qs, urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the existing modules - but wrapped in try/except to handle import issues
try:
    from recommender.engine import load_all_plants, select_environment, get_user_preferences, hard_filter, relax_if_needed, score_and_rank, assemble_output, category_diversity
    from recommender.scoring import weights, calculate_scores
    IMPORTS_OK = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_OK = False

# Import Google Drive service
try:
    from services.google_drive_service import drive_service
    DRIVE_SERVICE_OK = True
except ImportError as e:
    print(f"Google Drive service import error: {e}")
    DRIVE_SERVICE_OK = False
    drive_service = None

# Google Drive configuration - Public folder IDs from frontend imageHelper.js
DRIVE_FOLDERS = {
    "flower": "1ZcE9R3FMvZa5TRp8HfAHo-K7dAD5IfmL",
    "herb": "1aVMw8n51wCndrlUb8xG5cRjsMvBnON7n", 
    "vegetable": "1rmv-7k70qL_fR1efsKa_t28I22pLKzf_"
}

def get_drive_image_url(image_path: str, plant_category: str) -> str:
    """Generate Google Drive image URL based on plant category and image path
    
    Args:
        image_path: Path like "flower_plant_images/Agastache- Lavender Martini_Agastache aurantiaca/Agastache- Lavender Martini_Agastache aurantiaca_1.jpg"
        plant_category: Category like "flower", "herb", "vegetable"
    
    Returns:
        Empty string for now - Google Drive folder URLs don't work for direct image display
        Individual file IDs are required for proper Google Drive integration
    """
    # TEMPORARY FIX: Return empty string to disable broken Google Drive URLs
    # The current implementation uses folder IDs which don't work for direct image display
    # 
    # Google Drive folder structure (as confirmed by user):
    # Plantopia/
    # ├── flower_plant_images/
    # │   └── Agastache- Lavender Martini_Agastache aurantiaca/
    # │       ├── Agastache- Lavender Martini_Agastache aurantiaca_1.jpg
    # │       ├── Agastache- Lavender Martini_Agastache aurantiaca_2.jpg
    # │       └── Agastache- Lavender Martini_Agastache aurantiaca_3.jpg
    # ├── herb_plant_images/
    # └── vegetable_plant_images/
    #
    # REQUIRED FOR PROPER IMPLEMENTATION:
    # 1. Google Drive API credentials
    # 2. Search for files by exact path within Plantopia folder
    # 3. Get individual file IDs for each image
    # 4. Return URLs like: https://drive.google.com/uc?export=view&id=ACTUAL_FILE_ID
    #
    # For now, returning empty string triggers frontend to use placeholder images
    
    return ""

def check_environment():
    """Verify all required environment variables are present"""
    required_vars = [
        'GOOGLE_DRIVE_API_KEY',
        'GOOGLE_DRIVE_FOLDER_FLOWER',
        'GOOGLE_DRIVE_FOLDER_HERB', 
        'GOOGLE_DRIVE_FOLDER_VEGETABLE'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please check your .env file")
        return False
    
    print("✅ All environment variables loaded successfully")
    return True

# Check environment on startup
env_ok = check_environment()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Handle both /api and /api/ as root API endpoint
        if path == "/" or path == "" or path == "/api" or path == "/api/":
            # Root endpoint
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "Plantopia Recommendation Engine API", 
                "status": "working", 
                "version": "1.0.0",
                "debug": "API root endpoint working with BaseHTTPRequestHandler",
                "imports_status": "OK" if IMPORTS_OK else "FAILED",
                "google_drive": "connected" if DRIVE_SERVICE_OK and drive_service and drive_service.api_key else "not configured",
                "environment_ok": env_ok
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        elif path == "/health" or path == "/api/health":
            # Health check endpoint
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy", 
                "service": "plantopia-api",
                "debug": "Health check working with BaseHTTPRequestHandler"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        elif path == "/test-drive" or path == "/api/test-drive":
            # Test Google Drive API connection
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if DRIVE_SERVICE_OK and drive_service:
                is_connected = drive_service.test_connection()
                response = {
                    "google_drive_connected": is_connected,
                    "api_key_present": bool(drive_service.api_key),
                    "folder_ids_configured": len([f for f in drive_service.folder_ids.values() if f])
                }
            else:
                response = {
                    "google_drive_connected": False,
                    "api_key_present": False,
                    "folder_ids_configured": 0,
                    "error": "Google Drive service not available"
                }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        elif path.startswith("/images/") or path.startswith("/api/images/"):
            # Get all images for a specific plant category
            category = path.split("/")[-1]
            
            if category not in ['flower', 'herb', 'vegetable']:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Invalid category. Must be flower, herb, or vegetable"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if DRIVE_SERVICE_OK and drive_service:
                images = drive_service.get_folder_files(category)
                response = {
                    "category": category,
                    "count": len(images),
                    "images": images
                }
            else:
                response = {
                    "category": category,
                    "count": 0,
                    "images": [],
                    "error": "Google Drive service not available"
                }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        elif path == "/plants" or path == "/api/plants":
            # Simple plants endpoint - return a basic response for now
            if not IMPORTS_OK:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Import error - dependencies not available"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Try to load plants
            try:
                # Get the root directory (one level up from /api/)
                api_dir = os.path.dirname(os.path.abspath(__file__))
                root_path = os.path.dirname(api_dir)
                csv_paths = {
                    "flower": os.path.join(root_path, "flower_plants_data.csv"),
                    "herb": os.path.join(root_path, "herbs_plants_data.csv"),
                    "vegetable": os.path.join(root_path, "vegetable_plants_data.csv")
                }
                
                # Check if CSV files exist
                missing_files = []
                for category, path in csv_paths.items():
                    if not os.path.exists(path):
                        missing_files.append(f"{category}: {path}")
                
                if missing_files:
                    response = {
                        "error": "CSV files not found",
                        "missing_files": missing_files,
                        "root_path": root_path,
                        "plants": [],
                        "total_count": 0
                    }
                else:
                    all_plants = load_all_plants(csv_paths)
                    
                    # Add image information for all plants with Google Drive API integration
                    if DRIVE_SERVICE_OK and drive_service:
                        all_images = drive_service.get_all_images()
                    else:
                        all_images = {}
                    
                    for i, plant in enumerate(all_plants):
                        original_image_path = plant.get("image_path", "")
                        plant_category = plant.get("plant_category", "")
                        plant_name = plant.get("plant_name", "")
                        
                        # Try to find matching Google Drive image
                        drive_url = ""
                        plant_images = all_images.get(plant_category, [])
                        
                        if plant_images:
                            # Try to find matching image by plant name
                            for img in plant_images:
                                if plant_name.lower().replace(" ", "_") in img["name"].lower() or \
                                   plant_name.lower() in img["name"].lower():
                                    drive_url = img["url"]
                                    break
                            
                            # If no exact match, use first available image in category
                            if not drive_url and plant_images:
                                drive_url = plant_images[0]["url"]
                        
                        plant["media"] = {
                            "image_path": original_image_path,
                            "image_base64": "",
                            "drive_url": drive_url,
                            "drive_thumbnail": drive_url,
                            "has_image": bool(drive_url),
                            "placeholder": "/placeholder-plant.svg",
                            "note": "Google Drive API integration active" if drive_url else "No matching image found in Google Drive"
                        }
                    
                    response = {
                        "plants": all_plants,  # Return all plants
                        "total_count": len(all_plants),
                        "debug": "BaseHTTPRequestHandler implementation working",
                        "csv_files_found": len(csv_paths),
                        "root_path": root_path
                    }
                
            except Exception as e:
                response = {
                    "error": f"Error loading plants: {str(e)}",
                    "plants": [],
                    "total_count": 0
                }
                
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        else:
            # 404 for unknown paths
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Endpoint not found", "path": path}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
    
    def do_POST(self):
        # Handle POST endpoints
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if not IMPORTS_OK:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Import error - dependencies not available for POST endpoints"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        if path == "/recommendations" or path == "/api/recommendations":
            # Plant recommendations endpoint with fallback images
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    request_data = json.loads(post_data.decode('utf-8'))
                else:
                    request_data = {}
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                # Try to get real recommendations, fallback to test response if imports fail
                if IMPORTS_OK:
                    try:
                        # Get the root directory (one level up from /api/)
                        api_dir = os.path.dirname(os.path.abspath(__file__))
                        root_path = os.path.dirname(api_dir)
                        
                        # Load climate data
                        climate_file = os.path.join(root_path, "climate_data.json")
                        if os.path.exists(climate_file):
                            with open(climate_file, 'r') as f:
                                climate_data = json.load(f)
                        else:
                            climate_data = {}
                        
                        # Load plant data
                        csv_paths = {
                            "flower": os.path.join(root_path, "flower_plants_data.csv"),
                            "herb": os.path.join(root_path, "herbs_plants_data.csv"),
                            "vegetable": os.path.join(root_path, "vegetable_plants_data.csv")
                        }
                        
                        all_plants = load_all_plants(csv_paths)
                        
                        # Get user preferences from request
                        suburb = request_data.get("suburb", "Richmond")
                        n_recommendations = request_data.get("n", 5)
                        user_prefs = request_data.get("user_preferences", {})
                        
                        # Select environment
                        environment = select_environment(suburb, climate_data, 
                                                       climate_zone=request_data.get("climate_zone"))
                        
                        # Get processed user preferences
                        processed_prefs = get_user_preferences(user_prefs, environment)
                        
                        # Apply filters
                        filtered_plants = hard_filter(all_plants, processed_prefs, environment)
                        
                        # Relax filters if needed
                        if len(filtered_plants) < n_recommendations:
                            filtered_plants = relax_if_needed(all_plants, processed_prefs, environment, 
                                                            filtered_plants, n_recommendations)
                        
                        # Score and rank
                        scored_plants = score_and_rank(filtered_plants, processed_prefs, environment)
                        
                        # Apply diversity cap but ensure we reach target count
                        diverse_plants = category_diversity(scored_plants, max_per_cat=2, target_count=n_recommendations)
                        
                        # Take top N recommendations
                        top_plants = diverse_plants[:n_recommendations]
                        
                        # Assemble final recommendations with safe image handling
                        recommendations = []
                        for score, plant, scores_breakdown in top_plants:
                            # Generate safe media object with fallback
                            media_obj = {
                                "image_path": plant.get("image_path", ""),
                                "image_base64": "",
                                "drive_url": "",
                                "drive_thumbnail": "",
                                "has_image": False,  # Always use placeholder for now
                                "placeholder": "/placeholder-plant.svg",
                                "note": "Using placeholder - Google Drive integration disabled"
                            }
                            
                            recommendation = assemble_output([score], [plant], [scores_breakdown], 
                                                           environment, processed_prefs)[0]
                            recommendation["media"] = media_obj
                            recommendations.append(recommendation)
                        
                        response = {
                            "recommendations": recommendations,
                            "suburb": suburb,
                            "climate_zone": environment.get("climate_zone", "temperate"),
                            "month_now": environment.get("month_now", "August"),
                            "notes": [],
                            "debug": f"Real recommendations engine - {len(top_plants)} plants processed"
                        }
                        
                    except Exception as e:
                        # Fallback to test response if real recommendations fail
                        response = {
                            "recommendations": [
                                {
                                    "plant_name": "Basil",
                                    "scientific_name": "Ocimum basilicum",
                                    "plant_category": "herb",
                                    "plant_type": "Annual herb to 50cm; Culinary use; Aromatic leaves",
                                    "score": 95.0,
                                    "why": ["Fallback recommendation - real engine failed", f"Error: {str(e)}"],
                                    "fit": {
                                        "sun_need": "full_sun", 
                                        "container_ok": True,
                                        "time_to_maturity_days": 60,
                                        "maintainability": "hardy",
                                        "indoor_ok": True,
                                        "habit": "compact"
                                    },
                                    "sowing": {
                                        "climate_zone": "cool",
                                        "months": ["August", "September", "October"],
                                        "method": "sow_direct",
                                        "depth_mm": 5,
                                        "spacing_cm": 20,
                                        "season_label": "Start now"
                                    },
                                    "media": {
                                        "image_path": "herb_plant_images/basil.jpg",
                                        "image_base64": "",
                                        "drive_url": "",
                                        "drive_thumbnail": "",
                                        "has_image": False,
                                        "placeholder": "/placeholder-plant.svg",
                                        "note": "Using placeholder - Google Drive integration disabled for testing"
                                    },
                                    "days_to_maturity": 60,
                                    "plant_spacing": 20,
                                    "sowing_depth": 5,
                                    "position": "Full sun to part sun, well drained soil",
                                    "season": "Spring and summer",
                                    "germination": "7-14 days @ 18-25°C",
                                    "sowing_method": "Sow direct or raise seedlings",
                                    "hardiness_life_cycle": "Frost tender Annual",
                                    "characteristics": "Aromatic, culinary herb",
                                    "description": "Sweet basil is a popular culinary herb with aromatic leaves",
                                    "additional_information": "Culinary use; Container growing",
                                    "seed_type": "Open pollinated, untreated, non-GMO variety of seed",
                                    "image_filename": "herb_plant_images/basil.jpg",
                                    "cool_climate_sowing_period": "September, October, November",
                                    "temperate_climate_sowing_period": "August, September, October, November, December",
                                    "subtropical_climate_sowing_period": "March, April, May, June, July, August, September",
                                    "tropical_climate_sowing_period": "April, May, June, July, August",
                                    "arid_climate_sowing_period": "March, April, May, August, September, October"
                                }
                            ],
                            "suburb": request_data.get("suburb", "Richmond"),
                            "climate_zone": "cool",
                            "month_now": "August",
                            "notes": [],
                            "debug": f"Fallback recommendation due to error: {str(e)}"
                        }
                else:
                    # Basic test response when imports are not available
                    response = {
                        "recommendations": [
                            {
                                "plant_name": "Test Plant - Imports Failed",
                                "scientific_name": "Importus Failedus",
                                "plant_category": "herb",
                                "plant_type": "Test plant when imports are not available",
                                "score": 90.0,
                                "why": ["Test recommendation - imports not available"],
                                "fit": {
                                    "sun_need": "full_sun", 
                                    "container_ok": True,
                                    "time_to_maturity_days": 60,
                                    "maintainability": "hardy",
                                    "indoor_ok": True,
                                    "habit": "compact"
                                },
                                "sowing": {
                                    "climate_zone": "cool",
                                    "months": ["August", "September", "October"],
                                    "method": "sow_direct",
                                    "depth_mm": 5,
                                    "spacing_cm": 20,
                                    "season_label": "Start now"
                                },
                                "media": {
                                    "image_path": "herb_plant_images/test.jpg",
                                    "image_base64": "",
                                    "drive_url": "",
                                    "drive_thumbnail": "",
                                    "has_image": False,
                                    "placeholder": "/placeholder-plant.svg",
                                    "note": "Using placeholder - imports not available"
                                },
                                "days_to_maturity": 60,
                                "plant_spacing": 20,
                                "sowing_depth": 5,
                                "position": "Full sun to part sun, well drained soil",
                                "season": "Spring and summer",
                                "germination": "7-14 days @ 18-25°C",
                                "sowing_method": "Sow direct or raise seedlings",
                                "hardiness_life_cycle": "Frost tender Annual",
                                "characteristics": "Test plant, hardy herb",
                                "description": "Test plant for API endpoint when imports fail",
                                "additional_information": "Test use only",
                                "seed_type": "Test seed variety",
                                "image_filename": "herb_plant_images/test.jpg",
                                "cool_climate_sowing_period": "September, October, November",
                                "temperate_climate_sowing_period": "August, September, October, November, December",
                                "subtropical_climate_sowing_period": "March, April, May, June, July, August, September",
                                "tropical_climate_sowing_period": "April, May, June, July, August",
                                "arid_climate_sowing_period": "March, April, May, August, September, October"
                            }
                        ],
                        "suburb": request_data.get("suburb", "Richmond"),
                        "climate_zone": "cool",
                        "month_now": "August",
                        "notes": [],
                        "debug": "Test recommendations - imports not available"
                    }
                
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": f"Error processing recommendations: {str(e)}"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
        else:
            # 404 for unknown POST paths
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "POST endpoint not found", "path": path}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return