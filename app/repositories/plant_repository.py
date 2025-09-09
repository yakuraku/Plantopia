import json
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.core.config import settings
from app.models.plant import Plant


class PlantRepository:
    """Repository for managing plant data from CSV files"""
    
    def __init__(self):
        self.csv_paths = settings.CSV_PATHS
        self.climate_data_path = settings.CLIMATE_DATA_PATH
        self._plants_cache: Optional[List[Dict[str, Any]]] = None
        self._climate_cache: Optional[Dict[str, Any]] = None
    
    def load_all_plants(self) -> List[Dict[str, Any]]:
        """Load all plants from CSV files.
        
        Returns:
            List of plant dictionaries
        """
        if self._plants_cache is not None:
            return self._plants_cache
        
        all_plants = []
        
        for category, csv_path in self.csv_paths.items():
            try:
                df = pd.read_csv(csv_path)
                plants = df.to_dict('records')
                
                # Add category to each plant
                for plant in plants:
                    plant['plant_category'] = category
                
                all_plants.extend(plants)
            except FileNotFoundError:
                print(f"Warning: {csv_path} not found")
            except Exception as e:
                print(f"Error loading {csv_path}: {e}")
        
        self._plants_cache = all_plants
        return all_plants
    
    def find_plant_by_name(self, plant_name: str) -> Optional[Dict[str, Any]]:
        """Find a specific plant by name.
        
        Args:
            plant_name: Name of the plant to find
            
        Returns:
            Plant dictionary or None if not found
        """
        plants = self.load_all_plants()
        plant_name_lower = plant_name.lower().strip()
        
        for plant in plants:
            current_name = plant.get("plant_name", "").lower().strip()
            scientific_name = plant.get("scientific_name", "").lower().strip()
            
            if (current_name == plant_name_lower or 
                scientific_name == plant_name_lower or
                plant_name_lower in current_name or
                plant_name_lower in scientific_name):
                return plant
        
        return None
    
    def get_plants_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all plants of a specific category.
        
        Args:
            category: Plant category (flower, herb, vegetable)
            
        Returns:
            List of plant dictionaries
        """
        plants = self.load_all_plants()
        return [p for p in plants if p.get('plant_category') == category]
    
    def load_climate_data(self) -> Dict[str, Any]:
        """Load climate data from JSON file.
        
        Returns:
            Climate data dictionary
        """
        if self._climate_cache is not None:
            return self._climate_cache
        
        try:
            with open(self.climate_data_path, 'r', encoding='utf-8') as f:
                self._climate_cache = json.load(f)
                return self._climate_cache
        except FileNotFoundError:
            print(f"Climate data file {self.climate_data_path} not found")
            return {}
        except Exception as e:
            print(f"Error loading climate data: {e}")
            return {}
    
    def get_suburb_climate(self, suburb: str) -> Optional[Dict[str, Any]]:
        """Get climate data for a specific suburb.
        
        Args:
            suburb: Name of the suburb
            
        Returns:
            Climate data for the suburb or None if not found
        """
        climate_data = self.load_climate_data()
        return climate_data.get(suburb)
    
    def clear_cache(self):
        """Clear cached data."""
        self._plants_cache = None
        self._climate_cache = None