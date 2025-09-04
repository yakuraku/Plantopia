from http.server import BaseHTTPRequestHandler
import json
import tempfile
import os
from typing import Optional, Dict, Any, List
from urllib.parse import parse_qs, urlparse

# Import the existing modules - but wrapped in try/except to handle import issues
try:
    from recommender.engine import load_all_plants, select_environment, get_user_preferences, hard_filter, relax_if_needed, score_and_rank, assemble_output, category_diversity
    from recommender.scoring import weights, calculate_scores
    IMPORTS_OK = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_OK = False

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
                "imports_status": "OK" if IMPORTS_OK else "FAILED"
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
                    
                    # Add image information for all plants with placeholder system
                    for i, plant in enumerate(all_plants):
                        original_image_path = plant.get("image_path", "")
                        plant_category = plant.get("plant_category", "")
                        
                        # Try to generate Google Drive URL (currently returns empty string)
                        drive_url = get_drive_image_url(original_image_path, plant_category)
                        
                        plant["media"] = {
                            "image_path": original_image_path,
                            "image_base64": "",  # Could contain base64 data in the future
                            "drive_url": drive_url,  # Empty for now - will be populated when Google Drive API is integrated
                            "drive_thumbnail": drive_url,
                            "has_image": False,  # Set to False to trigger placeholder usage in frontend
                            "placeholder": "/placeholder-plant.svg",
                            "note": "Using placeholder images - Google Drive API integration required for actual plant photos"
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
                            "media": {"drive_url": get_drive_image_url("herb")},
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