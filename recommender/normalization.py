import re
import os
from typing import List, Dict, Any, Optional

def clean_text(s: str) -> str:
    """Clean text by preserving markdown markers and removing only extra whitespace."""
    if not isinstance(s, str):
        return ""
    # Keep markdown markers intact, only strip whitespace
    s = s.strip()
    return s

def parse_days_to_maturity(v: str) -> Optional[int]:
    """Parse days to maturity, returning midpoint if range."""
    if not isinstance(v, str) or not v:
        return None
    v = v.strip().lower().replace("days", "").replace("day", "").strip()
    if "-" in v:
        try:
            parts = v.split("-")
            return int((int(parts[0]) + int(parts[1])) / 2)
        except ValueError:
            return None
    else:
        try:
            return int(v)
        except ValueError:
            return None

def parse_sowing_months(s: str) -> List[str]:
    """Parse sowing months string into list of months."""
    if not isinstance(s, str) or not s:
        return []
    
    # English month names
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    result = []
    s = s.lower()
    for month in months:
        if month.lower() in s:
            result.append(month)
    
    return result

def build_sowing_by_climate(row: Dict[str, Any]) -> Dict[str, List[str]]:
    """Build sowing months by climate zone."""
    climate_zones = {
        "cool": "cool_climate_sowing_period",
        "temperate": "temperate_climate_sowing_period",
        "subtropical": "subtropical_climate_sowing_period",
        "tropical": "tropical_climate_sowing_period",
        "arid": "arid_climate_sowing_period"
    }
    
    result = {}
    for zone, col in climate_zones.items():
        result[zone] = parse_sowing_months(row.get(col, ""))
    
    return result

def derive_sun_need(position: str) -> str:
    """Derive sun need from position text."""
    if not isinstance(position, str):
        return "part_sun"
    
    pos_lower = position.lower()
    if "full sun" in pos_lower:
        return "full_sun"
    elif "part" in pos_lower:
        return "part_sun"
    elif "shade" in pos_lower:
        return "bright_shade"
    else:
        return "part_sun"

def derive_container_ok(row: Dict[str, Any]) -> bool:
    """Determine if plant is suitable for containers."""
    keywords = ["container", "pot", "compact", "dwarf"]
    
    for field in ["characteristics", "description", "plant_type"]:
        if isinstance(row.get(field), str):
            text = row[field].lower()
            if any(keyword in text for keyword in keywords):
                return True
    
    return False

def derive_indoor_ok(row: Dict[str, Any]) -> bool:
    """Determine if plant is suitable for indoor growing."""
    if not derive_container_ok(row):
        return False
    
    sun_need = derive_sun_need(row.get("position", ""))
    if sun_need == "full_sun":
        return False
    
    keywords = ["indoor", "windowsill", "bright shade", "part sun", "dwarf", "compact"]
    
    for field in ["characteristics", "description", "plant_type"]:
        if isinstance(row.get(field), str):
            text = row[field].lower()
            if any(keyword in text for keyword in keywords):
                return True
    
    return False

def derive_habit(row: Dict[str, Any]) -> str:
    """Derive plant habit from text."""
    habits = {
        "climber": ["climber", "climbing"],
        "vine": ["vine", "vining"],
        "dwarf": ["dwarf"],
        "compact": ["compact"],
        "bush": ["bush", "shrub"],
        "groundcover": ["groundcover", "ground cover"],
        "upright": ["upright", "erect"]
    }
    
    for field in ["plant_type", "description", "characteristics"]:
        if isinstance(row.get(field), str):
            text = row[field].lower()
            for habit, keywords in habits.items():
                if any(keyword in text for keyword in keywords):
                    return habit
    
    return "unknown"

def derive_maintainability_score(row: Dict[str, Any]) -> float:
    """Derive maintainability score from hardiness and other factors."""
    score = 0.6  # default
    
    hardiness = row.get("hardiness_life_cycle", "")
    if isinstance(hardiness, str):
        if "Hardy" in hardiness:
            score = 0.9
        elif "Half Hardy" in hardiness:
            score = 0.6
        elif "Frost tender" in hardiness:
            score = 0.4
    
    # Bonus for easy care keywords
    bonus_keywords = ["easy", "drought", "disease resistant"]
    found_bonus = False
    for field in ["characteristics", "description"]:
        if isinstance(row.get(field), str):
            text = row[field].lower()
            if any(keyword in text for keyword in bonus_keywords):
                found_bonus = True
                break
    
    if found_bonus:
        score = min(1.0, score + 0.05)
    
    return score

def derive_edible(row: Dict[str, Any]) -> bool:
    """Determine if plant is edible."""
    category = row.get("plant_category", "")
    if category in ["vegetable", "herb"]:
        return True
    
    culinary_keywords = ["culinary"]
    for field in ["characteristics", "description"]:
        if isinstance(row.get(field), str):
            text = row[field].lower()
            if any(keyword in text for keyword in culinary_keywords):
                return True
    
    return False

def derive_fragrant(row: Dict[str, Any]) -> bool:
    """Determine if plant is fragrant."""
    keywords = ["fragrant", "aromatic", "scented"]
    
    for field in ["characteristics", "description"]:
        if isinstance(row.get(field), str):
            text = row[field].lower()
            if any(keyword in text for keyword in keywords):
                return True
    
    return False

def derive_flower_colors(row: Dict[str, Any]) -> List[str]:
    """Extract flower colors from text."""
    colors = ["white", "yellow", "orange", "pink", "red", "purple", "violet", "blue", "magenta"]
    found_colors = []
    
    for field in ["characteristics", "description"]:
        if isinstance(row.get(field), str):
            text = row[field].lower()
            for color in colors:
                if color in text:
                    # Normalize violet to purple
                    normalized = "purple" if color == "violet" else color
                    if normalized not in found_colors:
                        found_colors.append(normalized)
    
    return found_colors

def choose_primary_image_path(row: Dict[str, Any], base_dirs: Dict[str, str]) -> str:
    """Choose primary image path."""
    image_filename = row.get("image_filename", "")
    if not isinstance(image_filename, str) or not image_filename:
        return ""
    
    # Get first image from semicolon-separated list
    first_image = image_filename.split(";")[0].strip()
    
    # Sanitize path separators
    first_image = first_image.replace("\\\\", "/")
    
    # Determine base directory
    category = row.get("plant_category", "")
    if category in base_dirs:
        return os.path.join(base_dirs[category], first_image).replace("\\\\", "/")
    
    return first_image

def parse_sowing_depth_or_spacing(value: str, unit: str) -> Optional[int]:
    """Parse sowing depth or spacing value."""
    if not isinstance(value, str) or not value:
        return None
    
    # Extract number with unit
    pattern = rf"(\\d+)\\s*{unit}"
    match = re.search(pattern, value, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # If no unit, try to parse as plain number
    try:
        return int(re.search(r"\\d+", value).group())
    except (AttributeError, ValueError):
        return None

def normalize_dataframe(df, category_hint: Optional[str] = None) -> List[Dict[str, Any]]:
    """Normalize dataframe to list of dictionaries with consistent fields."""
    base_dirs = {
        "flower": "flower_plant_images/",
        "herb": "herb_plant_images/",
        "vegetable": "vegetable_plant_images/"
    }
    
    result = []
    
    for idx, row in df.iterrows():
        # Convert row to dict
        row_dict = row.to_dict()
        
        # Add category hint if missing
        if not row_dict.get("plant_category") and category_hint:
            row_dict["plant_category"] = category_hint
        
        # Normalize fields
        normalized = {
            "plant_name": clean_text(row_dict.get("plant_name", "")),
            "scientific_name": clean_text(row_dict.get("scientific_name", "")),
            "plant_category": row_dict.get("plant_category", category_hint or "unknown"),
            "plant_type": clean_text(row_dict.get("plant_type", "")),
            "time_to_maturity_days": parse_days_to_maturity(row_dict.get("days_to_maturity", "")),
            "sun_need": derive_sun_need(row_dict.get("position", "")),
            "container_ok": derive_container_ok(row_dict),
            "indoor_ok": derive_indoor_ok(row_dict),
            "habit": derive_habit(row_dict),
            "maintainability_score": derive_maintainability_score(row_dict),
            "edible": derive_edible(row_dict),
            "fragrant": derive_fragrant(row_dict),
            "flower_colors": derive_flower_colors(row_dict),
            "sowing_months_by_climate": build_sowing_by_climate(row_dict),
            "sowing_method": clean_text(row_dict.get("sowing_method", "")),
            "sowing_depth_mm": parse_sowing_depth_or_spacing(row_dict.get("sowing_depth", ""), "mm"),
            "spacing_cm": parse_sowing_depth_or_spacing(row_dict.get("plant_spacing", ""), "cm"),
            "description": clean_text(row_dict.get("description", "")),
            "characteristics": clean_text(row_dict.get("characteristics", "")),
            "image_path": choose_primary_image_path(row_dict, base_dirs),
            "raw_row_index": idx
        }
        
        result.append(normalized)
    
    return result