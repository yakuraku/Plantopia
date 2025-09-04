from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import traceback

# Add parent directory to Python path to find recommender modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        debug_info = {
            "status": "debug endpoint working",
            "working_directory": os.getcwd(),
            "parent_directory": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "sys_path": sys.path[:5],  # First 5 entries
            "environment_check": {},
            "file_checks": {},
            "import_checks": {},
            "recommender_test": {}
        }
        
        # Check environment variables
        env_vars = ['GOOGLE_DRIVE_API_KEY', 'GOOGLE_DRIVE_FOLDER_FLOWER', 'GOOGLE_DRIVE_FOLDER_HERB', 'GOOGLE_DRIVE_FOLDER_VEGETABLE']
        for var in env_vars:
            debug_info["environment_check"][var] = bool(os.getenv(var))
        
        # Check file existence
        files_to_check = [
            "climate_data.json",
            "flower_plants_data.csv", 
            "herbs_plants_data.csv",
            "vegetable_plants_data.csv",
            "recommender/__init__.py",
            "recommender/engine.py",
            "recommender/scoring.py"
        ]
        
        for file_path in files_to_check:
            debug_info["file_checks"][file_path] = os.path.exists(file_path)
        
        # Test imports
        try:
            from recommender.engine import load_all_plants
            debug_info["import_checks"]["recommender.engine.load_all_plants"] = "SUCCESS"
        except Exception as e:
            debug_info["import_checks"]["recommender.engine.load_all_plants"] = f"ERROR: {str(e)}"
            
        try:
            from recommender.scoring import weights
            debug_info["import_checks"]["recommender.scoring.weights"] = "SUCCESS"
        except Exception as e:
            debug_info["import_checks"]["recommender.scoring.weights"] = f"ERROR: {str(e)}"
        
        # Test loading plant data
        if debug_info["import_checks"].get("recommender.engine.load_all_plants") == "SUCCESS":
            try:
                from recommender.engine import load_all_plants
                csv_paths = {
                    "flower": "flower_plants_data.csv",
                    "herb": "herbs_plants_data.csv", 
                    "vegetable": "vegetable_plants_data.csv"
                }
                
                plants = load_all_plants(csv_paths)
                debug_info["recommender_test"]["load_plants"] = f"SUCCESS: Loaded {len(plants)} plants"
                
                if plants:
                    sample = plants[0]
                    debug_info["recommender_test"]["sample_plant"] = {
                        "name": sample.get("plant_name", "Unknown"),
                        "category": sample.get("plant_category", "Unknown"),
                        "keys": list(sample.keys())[:10]  # First 10 keys
                    }
                    
            except Exception as e:
                debug_info["recommender_test"]["load_plants"] = f"ERROR: {str(e)}"
                debug_info["recommender_test"]["traceback"] = traceback.format_exc()
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Pretty print JSON for readability
        response_json = json.dumps(debug_info, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
        return