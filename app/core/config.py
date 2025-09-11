from typing import List
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application configuration settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Plantopia Recommendation Engine API"
    PROJECT_DESCRIPTION: str = "API for the Plantopia plant recommendation engine"
    VERSION: str = "1.0.0"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # In production, replace with specific origins
    
    # File Paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # Data Files
    CSV_PATHS = {
        "flower": str(DATA_DIR / "csv" / "flower_plants_data.csv"),
        "herb": str(DATA_DIR / "csv" / "herbs_plants_data.csv"),
        "vegetable": str(DATA_DIR / "csv" / "vegetable_plants_data.csv")
    }
    
    CLIMATE_DATA_PATH = str(DATA_DIR / "json" / "climate_data.json")
    
    # Image Directories
    IMAGE_DIRS = {
        "flower": str(DATA_DIR / "flower_plant_images"),
        "herb": str(DATA_DIR / "herb_plant_images"),
        "vegetable": str(DATA_DIR / "vegetable_plant_images")
    }
    
    # Default Values
    DEFAULT_SUBURB = "Richmond"
    DEFAULT_RECOMMENDATIONS = 5
    DEFAULT_MAX_PER_CATEGORY = 2
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Climate API Keys
    WAQI_API_TOKEN: str = os.getenv("WAQI_API_TOKEN", "")
    OPEN_METEO_API_KEY: str = os.getenv("OPEN_METEO_API_KEY", "")
    EPA_VIC_API_KEY: str = os.getenv("EPA_VIC_API_KEY", "")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()