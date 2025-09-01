from typing import Dict, Any, List, Tuple
from datetime import datetime
import calendar

# Default weights
weights = {
    "season": 0.25,
    "sun": 0.20,
    "maintainability": 0.15,
    "time_to_results": 0.10,
    "site_fit": 0.10,
    "preferences": 0.12,
    "wind_penalty": 0.03,
    "eco_bonus": 0.05
}

def season_score(climate_zone: str, month_now: str, plant: Dict[str, Any]) -> float:
    """Calculate season compatibility score."""
    sowing_months = plant.get("sowing_months_by_climate", {}).get(climate_zone, [])
    
    if month_now in sowing_months:
        return 1.0
    
    # Check ±1 month
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    try:
        current_idx = months.index(month_now)
        prev_idx = (current_idx - 1) % 12
        next_idx = (current_idx + 1) % 12
        
        if months[prev_idx] in sowing_months or months[next_idx] in sowing_months:
            return 0.7
    except ValueError:
        pass
    
    return 0.0

def sun_score(user_sun: str, plant_sun: str) -> float:
    """Calculate sun compatibility score."""
    order = ["bright_shade", "part_sun", "full_sun"]
    
    try:
        user_idx = order.index(user_sun)
        plant_idx = order.index(plant_sun)
        distance = abs(user_idx - plant_idx)
        
        if distance == 0:
            return 1.0
        elif distance == 1:
            return 0.7
        elif distance == 2:
            return 0.3
    except ValueError:
        pass
    
    return 0.5  # Default if not found

def maintainability_score(user_pref: str, plant_maint_score: float) -> float:
    """Calculate maintainability score."""
    if user_pref == "low":
        # Prefer high plant score for low maintenance
        return plant_maint_score
    elif user_pref == "medium":
        # Clamp to [0.6..1.0]
        return 0.5 + 0.5 * plant_maint_score
    elif user_pref == "high":
        # Baseline + plant score
        return 0.7 + 0.3 * plant_maint_score
    
    return plant_maint_score

def time_to_results_score(user_time_pref: str, t_days: int) -> float:
    """Calculate time to results score based on user preference and plant maturity time."""
    if t_days is None:
        return 0.6  # Default if unknown
    
    # Define preference ranges
    if user_time_pref == "quick":
        # User wants quick results (prefer plants that mature quickly)
        if t_days <= 45:          # Very quick (radishes, microgreens)
            return 1.0
        elif t_days <= 75:        # Quick (herbs, leafy greens)  
            return 0.8
        elif t_days <= 105:       # Medium (some flowers)
            return 0.5
        else:                     # Slow (long season crops)
            return 0.2
            
    elif user_time_pref == "standard":
        # User is okay with standard timing
        if t_days <= 60:          # Quick
            return 0.9
        elif t_days <= 120:       # Standard range
            return 1.0
        elif t_days <= 180:       # Longer but acceptable
            return 0.7
        else:                     # Very long
            return 0.4
            
    elif user_time_pref == "patient":
        # User is willing to wait for results (prefer longer-term crops)
        if t_days <= 60:          # Too quick
            return 0.6
        elif t_days <= 120:       # Good medium term
            return 0.8
        elif t_days <= 180:       # Perfect for patient gardeners
            return 1.0
        else:                     # Very long term
            return 0.9
    
    # Default fallback for unknown preferences
    if t_days <= 60:
        return 1.0
    elif t_days <= 120:
        return 0.8
    else:
        return 0.6

def site_fit_score(user_site: Dict[str, Any], plant: Dict[str, Any]) -> float:
    """Calculate site fit score."""
    score = 0.0
    
    # Indoor check
    if user_site.get("location_type") == "indoors" and plant.get("indoor_ok"):
        score += 0.2
    
    # Container check
    if user_site.get("containers") and plant.get("container_ok"):
        score += 0.2
    
    # Space check
    area_m2 = user_site.get("area_m2", 0)
    container_sizes = user_site.get("container_sizes", [])
    small_space = area_m2 < 3 or all(size in ["small", "medium"] for size in container_sizes)
    compact_habit = plant.get("habit") in ["dwarf", "compact", "groundcover"]
    
    if small_space and compact_habit:
        score += 0.15
    
    return min(1.0, score)

def preferences_score(pref: Dict[str, Any], plant: Dict[str, Any]) -> float:
    """Calculate preferences score."""
    score = 0.0
    
    # Edible preference
    edible_types = pref.get("edible_types", [])
    if edible_types and plant.get("edible"):
        score += 0.2
    
    # Ornamental preference
    ornamental_types = pref.get("ornamental_types", [])
    category = plant.get("plant_category", "")
    if ornamental_types and category == "flower":
        score += 0.2
    
    # Color preference
    user_colors = pref.get("colors", [])
    plant_colors = plant.get("flower_colors", [])
    if user_colors and plant_colors and set(user_colors).intersection(set(plant_colors)):
        score += 0.15
    
    # Fragrance preference
    if pref.get("fragrant") and plant.get("fragrant"):
        score += 0.15
    
    return min(1.0, score)

def wind_penalty_score(user_wind: str, plant: Dict[str, Any]) -> float:
    """Calculate wind penalty score."""
    if user_wind == "windy" and plant.get("habit") in ["climber", "upright", "vine"]:
        return 0.7
    return 1.0

def eco_bonus_score(plant: Dict[str, Any]) -> float:
    """Calculate eco bonus score."""
    bonus = 0.0
    
    keywords = ["beneficial insects", "pollinator"]
    characteristics = plant.get("characteristics", "").lower()
    description = plant.get("description", "").lower()
    
    text = characteristics + " " + description
    if any(keyword in text for keyword in keywords):
        bonus = 0.15
    
    return min(1.0, bonus)

def calculate_scores(plant: Dict[str, Any], user: Dict[str, Any], env: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """Calculate all scores for a plant."""
    # Extract user preferences
    user_site = user.get("site", {})
    user_preferences = user.get("preferences", {})
    climate_zone = env.get("climate_zone", "temperate")
    month_now = env.get("month_now", datetime.now().strftime("%B"))
    
    # Calculate sub-scores
    s_season = season_score(climate_zone, month_now, plant)
    s_sun = sun_score(user_site.get("sun_exposure", "part_sun"), plant.get("sun_need", "part_sun"))
    s_maintainability = maintainability_score(
        user_preferences.get("maintainability", "medium"), 
        plant.get("maintainability_score", 0.6)
    )
    s_time = time_to_results_score(
        user_preferences.get("time_to_results", "standard"), 
        plant.get("time_to_maturity_days")
    )
    s_site = site_fit_score(user_site, plant)
    s_preferences = preferences_score(user_preferences, plant)
    s_wind = wind_penalty_score(user_site.get("wind_exposure", "moderate"), plant)
    s_eco = eco_bonus_score(plant)
    
    # Store breakdown
    breakdown = {
        "season": s_season,
        "sun": s_sun,
        "maintainability": s_maintainability,
        "time_to_results": s_time,
        "site_fit": s_site,
        "preferences": s_preferences,
        "wind_penalty": s_wind,
        "eco_bonus": s_eco
    }
    
    # Calculate base score
    base = 100.0 * (
        weights["season"] * s_season +
        weights["sun"] * s_sun +
        weights["maintainability"] * s_maintainability +
        weights["time_to_results"] * s_time +
        weights["site_fit"] * s_site +
        weights["preferences"] * s_preferences +
        weights["eco_bonus"] * s_eco
    )
    
    # Apply wind penalty (multiplicative)
    final = base * (0.85 + 0.15 * s_wind)
    
    return final, breakdown

def goal_match(goal: str, is_edible: bool) -> bool:
    """Check if plant matches user goal."""
    if goal == "edible":
        return is_edible
    elif goal == "ornamental":
        return not is_edible
    elif goal == "mixed":
        return True
    return True

def type_match(plant_category: str, edible_types: List[str], ornamental_types: List[str]) -> bool:
    """Soft preference matching for types."""
    # This is handled in preferences_score
    return True

def category_diversity(result_list: List[Tuple[float, Dict[str, Any], Dict[str, float]]], 
                      max_per_cat: int = 2) -> List[Tuple[float, Dict[str, Any], Dict[str, float]]]:
    """Limit number of plants per category."""
    category_count = {}
    filtered = []
    
    for item in result_list:
        _, plant, _ = item
        category = plant.get("plant_category", "unknown")
        
        if category not in category_count:
            category_count[category] = 0
        
        if category_count[category] < max_per_cat:
            category_count[category] += 1
            filtered.append(item)
    
    return filtered