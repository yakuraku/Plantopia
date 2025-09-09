from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Plant:
    """Plant model representing a plant in the system"""
    plant_name: str
    scientific_name: Optional[str] = None
    plant_category: str = ""  # flower, herb, vegetable
    
    # Growing conditions
    sun_need: Optional[str] = None
    water_need: Optional[str] = None
    maintainability: Optional[str] = None
    time_to_maturity_days: Optional[int] = None
    
    # Suitability
    container_ok: bool = False
    indoor_ok: bool = False
    habit: Optional[str] = None
    
    # Sowing information
    sowing_months_by_climate: Dict[str, List[str]] = None
    sowing_method: Optional[str] = None
    sowing_depth_mm: Optional[int] = None
    spacing_cm: Optional[int] = None
    
    # Characteristics
    is_fragrant: bool = False
    colors: List[str] = None
    is_edible: bool = False
    edible_parts: List[str] = None
    
    # Media
    image_path: Optional[str] = None
    
    # Raw data (for flexibility)
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.sowing_months_by_climate is None:
            self.sowing_months_by_climate = {}
        if self.colors is None:
            self.colors = []
        if self.edible_parts is None:
            self.edible_parts = []
        if self.raw_data is None:
            self.raw_data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plant to dictionary"""
        return {
            "plant_name": self.plant_name,
            "scientific_name": self.scientific_name,
            "plant_category": self.plant_category,
            "sun_need": self.sun_need,
            "water_need": self.water_need,
            "maintainability": self.maintainability,
            "time_to_maturity_days": self.time_to_maturity_days,
            "container_ok": self.container_ok,
            "indoor_ok": self.indoor_ok,
            "habit": self.habit,
            "sowing_months_by_climate": self.sowing_months_by_climate,
            "sowing_method": self.sowing_method,
            "sowing_depth_mm": self.sowing_depth_mm,
            "spacing_cm": self.spacing_cm,
            "is_fragrant": self.is_fragrant,
            "colors": self.colors,
            "is_edible": self.is_edible,
            "edible_parts": self.edible_parts,
            "image_path": self.image_path,
            **self.raw_data  # Include any additional raw data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Plant':
        """Create plant from dictionary"""
        # Extract known fields
        known_fields = {
            "plant_name", "scientific_name", "plant_category",
            "sun_need", "water_need", "maintainability", "time_to_maturity_days",
            "container_ok", "indoor_ok", "habit",
            "sowing_months_by_climate", "sowing_method", "sowing_depth_mm", "spacing_cm",
            "is_fragrant", "colors", "is_edible", "edible_parts", "image_path"
        }
        
        # Separate known and unknown fields
        plant_data = {k: v for k, v in data.items() if k in known_fields}
        raw_data = {k: v for k, v in data.items() if k not in known_fields}
        
        return cls(**plant_data, raw_data=raw_data)