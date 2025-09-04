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
            # Simple recommendations response for testing
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    request_data = json.loads(post_data.decode('utf-8'))
                else:
                    request_data = {}
                
                # Return a simple test response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    "recommendations": [
                        {
                            "plant_name": "Test Plant",
                            "scientific_name": "Testus Plantus",
                            "plant_category": "test",
                            "score": 95.0,
                            "why": ["This is a test recommendation from BaseHTTPRequestHandler"],
                            "fit": {"sun_need": "full_sun", "container_ok": True},
                            "media": {"drive_url": get_drive_image_url("herb_plant_images/test.jpg", "herb")},
                        }
                    ],
                    "suburb": request_data.get("suburb", "Richmond"),
                    "debug": "POST recommendations working with BaseHTTPRequestHandler"
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