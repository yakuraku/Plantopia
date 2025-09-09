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

# Google Drive configuration
DRIVE_BASE_URL = "https://drive.google.com/uc?export=view&id="
DRIVE_FOLDERS = {
    "flower": "1ZcE9R3FMvZa5TRp8HfAHo-K7dAD5IfmL",
    "herb": "1aVMw8n51wCndrlUb8xG5cRjsMvBnON7n", 
    "vegetable": "1rmv-7k70qL_fR1efsKa_t28I22pLKzf_"
}

def get_drive_image_url(category: str, image_name: Optional[str] = None) -> str:
    """Generate Google Drive image URL for a plant category"""
    if not category:
        return ""
        
    # Normalize category
    normalized_category = category.lower()
    if normalized_category in ["flowers"]: normalized_category = "flower"
    if normalized_category in ["herbs"]: normalized_category = "herb"
    if normalized_category in ["vegetables"]: normalized_category = "vegetable"
    
    folder_id = DRIVE_FOLDERS.get(normalized_category)
    if not folder_id:
        return ""
    
    return f"{DRIVE_BASE_URL}{folder_id}"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/" or path == "":
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
            
        elif path == "/health":
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
            
        elif path == "/plants":
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
                base_path = os.path.dirname(os.path.abspath(__file__))
                csv_paths = {
                    "flower": os.path.join(base_path, "flower_plants_data.csv"),
                    "herb": os.path.join(base_path, "herbs_plants_data.csv"),
                    "vegetable": os.path.join(base_path, "vegetable_plants_data.csv")
                }
                
                all_plants = load_all_plants(csv_paths)
                
                # Add Google Drive URLs to first 5 plants as a test
                for i, plant in enumerate(all_plants[:5]):
                    plant_category = plant.get("plant_category", "")
                    drive_url = get_drive_image_url(plant_category)
                    plant["media"] = {
                        "image_path": drive_url,
                        "drive_url": drive_url,
                        "drive_thumbnail": drive_url,
                        "has_image": bool(drive_url)
                    }
                
                response = {
                    "plants": all_plants[:5],  # Return first 5 for testing
                    "total_count": len(all_plants),
                    "debug": "BaseHTTPRequestHandler implementation working"
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
        
        if path == "/recommendations":
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