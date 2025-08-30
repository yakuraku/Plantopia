import pandas as pd
import json
import os
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime
from dateutil import tz
from dateutil import parser as dtparser
from recommender.normalization import normalize_dataframe
from recommender.scoring import calculate_scores, goal_match


def _norm(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"\*\*", "", s)            # strip markdown bold
    s = re.sub(r"[^a-z0-9]+", "", s)      # keep alnum only
    return s

def canonical_id(plant: dict) -> str:
    # Prefer scientific_name if present; else plant_name
    sci = _norm(plant.get("scientific_name", ""))
    if sci:
        return f"sci:{sci}"
    return f"name:{_norm(plant.get('plant_name',''))}"

def dedupe_scored(scored_list: list[tuple]) -> list[tuple]:
    """
    Input: list of (score, plant_dict, breakdown) already sorted DESC by score.
    Output: same shape, but with duplicates removed by canonical_id.
    We keep the first occurrence (the highest-ranked due to sort order).
    """
    seen = set()
    out = []
    for item in scored_list:
        _, plant, _ = item
        cid = canonical_id(plant)
        if cid in seen:
            continue
        seen.add(cid)
        out.append(item)
    return out

def load_all_plants(csv_paths: Dict[str, str]) -> List[Dict[str, Any]]:
    """Load and normalize all plant data."""
    all_plants = []
    
    for category, path in csv_paths.items():
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, encoding='utf-8')
                normalized = normalize_dataframe(df, category)
                all_plants.extend(normalized)
            except Exception as e:
                print(f"Warning: Could not load {path}: {e}")
        else:
            print(f"Warning: CSV file {path} not found")
    
    return all_plants

def select_environment(suburb: str, climate_json: dict, cli_override_climate_zone: str | None = None) -> dict:
    entry = climate_json.get(suburb)
    if entry is None:
        entry = climate_json.get("Melbourne CBD")

    # Default Melbourne/VIC assumptions → COOL climate by default
    env = {
        "climate_zone": "cool",
        "month_now": datetime.now().strftime("%B"),
        "uv_index": 0.0,
        "temperature_c": 15.0,
        "humidity_pct": 60,
        "wind_speed_kph": 10
    }

    if entry:
        # If JSON has an 'environment' block with overlapping keys, adopt them
        if isinstance(entry.get("environment"), dict):
            for k in ["climate_zone","month_now","uv_index","temperature_c","humidity_pct","wind_speed_kph"]:
                if k in entry["environment"]:
                    env[k] = entry["environment"][k]
        # Otherwise, derive month from timestamp if provided and month_now not explicitly set
        if "timestamp" in entry and not entry.get("environment", {}).get("month_now"):
            try:
                ts = dtparser.parse(entry["timestamp"])
                env["month_now"] = ts.strftime("%B")
            except Exception:
                pass

    # CLI override has highest priority
    if cli_override_climate_zone:
        env["climate_zone"] = cli_override_climate_zone

    return env

def get_user_preferences(path: str) -> Dict[str, Any]:
    """Load user preferences with defaults."""
    # Default preferences
    defaults = {
        "user_id": "anon_mvp",
        "site": {
            "location_type": "balcony",
            "area_m2": 2.0,
            "sun_exposure": "part_sun",
            "wind_exposure": "moderate",
            "containers": True,
            "container_sizes": ["small", "medium"]
        },
        "preferences": {
            "goal": "mixed",
            "edible_types": ["herbs", "leafy"],
            "ornamental_types": ["flowers"],
            "colors": ["purple", "white"],
            "fragrant": True,
            "maintainability": "low",
            "watering": "medium",
            "time_to_results": "quick",
            "season_intent": "start_now",
            "pollen_sensitive": False
        },
        "practical": {
            "budget": "medium",
            "has_basic_tools": True,
            "organic_only": False
        },
        "environment": {
            "climate_zone": "temperate",
            "month_now": datetime.now().strftime("%B"),
            "uv_index": 0.0,
            "temperature_c": 8.0,
            "humidity_pct": 75,
            "wind_speed_kph": 15
        }
    }
    
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            # Merge with defaults
            for section in defaults:
                if section not in user_data:
                    user_data[section] = defaults[section]
                elif isinstance(defaults[section], dict):
                    for key, value in defaults[section].items():
                        if key not in user_data[section]:
                            user_data[section][key] = value
            
            return user_data
        except Exception as e:
            print(f"Warning: Could not load user preferences from {path}: {e}")
    
    return defaults

def hard_filter(plants: List[Dict[str, Any]], user: Dict[str, Any], env: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply hard filters to plant list."""
    filtered = []
    user_site = user.get("site", {})
    user_preferences = user.get("preferences", {})
    climate_zone = env.get("climate_zone", "temperate")
    month_now = env.get("month_now", datetime.now().strftime("%B"))
    
    for plant in plants:
        # Season filter
        sowing_months = plant.get("sowing_months_by_climate", {}).get(climate_zone, [])
        if month_now not in sowing_months:
            continue
        
        # Goal filter
        if not goal_match(user_preferences.get("goal", "mixed"), plant.get("edible", False)):
            continue
        
        # Site filters
        # Indoors requirement
        if user_site.get("location_type") == "indoors" and not plant.get("indoor_ok"):
            continue
        
        # Container requirement
        if user_site.get("containers") and not plant.get("container_ok"):
            continue
        
        # Sun requirement - strict match for hard filter
        user_sun = user_site.get("sun_exposure", "part_sun")
        plant_sun = plant.get("sun_need", "part_sun")
        
        # For hard filter, only allow exact match or one-step difference
        sun_order = ["bright_shade", "part_sun", "full_sun"]
        try:
            user_idx = sun_order.index(user_sun)
            plant_idx = sun_order.index(plant_sun)
            if abs(user_idx - plant_idx) > 1:
                continue
        except ValueError:
            pass
        
        filtered.append(plant)
    
    return filtered

def relax_if_needed(eligible: List[Dict[str, Any]], all_plants: List[Dict[str, Any]], 
                   user: Dict[str, Any], env: Dict[str, Any], target: int = 5) -> List[Dict[str, Any]]:
    """Relax filters if needed to reach target."""
    if len(eligible) >= target:
        return eligible
    
    # Collect notes about relaxations
    notes = []
    
    # 1. Include "near" season ±1 month
    climate_zone = env.get("climate_zone", "temperate")
    month_now = env.get("month_now", datetime.now().strftime("%B"))
    
    # Get all months
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    try:
        current_idx = months.index(month_now)
        prev_idx = (current_idx - 1) % 12
        next_idx = (current_idx + 1) % 12
        near_months = [months[prev_idx], month_now, months[next_idx]]
    except ValueError:
        near_months = [month_now]
    
    # Add plants that are sowable in near months
    expanded = eligible.copy()
    added_count = 0
    for plant in all_plants:
        if plant in eligible:
            continue
            
        sowing_months = plant.get("sowing_months_by_climate", {}).get(climate_zone, [])
        if any(month in sowing_months for month in near_months):
            expanded.append(plant)
            added_count += 1
    
    if added_count > 0:
        notes.append(f"Relaxed season by ±1 month for {added_count} items.")
    
    if len(expanded) >= target:
        return expanded
    
    # 2. Allow sun difference up to 2 steps
    user_site = user.get("site", {})
    user_sun = user_site.get("sun_exposure", "part_sun")
    sun_order = ["bright_shade", "part_sun", "full_sun"]
    
    try:
        user_idx = sun_order.index(user_sun)
    except ValueError:
        user_idx = 1  # Default to part_sun
    
    further_expanded = expanded.copy()
    added_count = 0
    for plant in all_plants:
        if plant in expanded:
            continue
            
        plant_sun = plant.get("sun_need", "part_sun")
        try:
            plant_idx = sun_order.index(plant_sun)
            if abs(user_idx - plant_idx) <= 2:  # Allow up to 2 steps
                further_expanded.append(plant)
                added_count += 1
        except ValueError:
            # If we can't determine, include it
            further_expanded.append(plant)
            added_count += 1
    
    if added_count > 0:
        notes.append(f"Relaxed sun tolerance by up to 2 levels for {added_count} items.")
    
    if len(further_expanded) >= target:
        return further_expanded
    
    # 3. If still not enough, return what we have
    return further_expanded

def score_and_rank(candidates: List[Dict[str, Any]], user: Dict[str, Any], 
                  env: Dict[str, Any], weights: Dict[str, float]) -> List[Tuple[float, Dict[str, Any], Dict[str, float]]]:
    """Score and rank candidate plants."""
    scored = []
    
    for plant in candidates:
        score, breakdown = calculate_scores(plant, user, env)
        scored.append((score, plant, breakdown))
    
    # scored is a list of tuples like (score, plant_dict, breakdown) OR similar.
    # We normalize by rounding score to 3 decimals for stable ordering.
    scored.sort(
        key=lambda x: (
            -round(x[0], 3),
            (x[1].get("time_to_maturity_days") or 10**9),
            x[1].get("plant_name","").lower()
        )
    )
    
    # NEW: dedupe same plant appearing in multiple categories or CSVs
    scored = dedupe_scored(scored)
    
    return scored

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

def assemble_output(top: List[Tuple[float, Dict[str, Any], Dict[str, float]]], 
                   user: Dict[str, Any], env: Dict[str, Any], notes: List[str]) -> Dict[str, Any]:
    """Assemble final output."""
    recommendations = []
    climate_zone = env.get("climate_zone", "temperate")
    month_now = env.get("month_now", datetime.now().strftime("%B"))
    
    for score, plant, breakdown in top:
        # Determine season label
        sowing_months = plant.get("sowing_months_by_climate", {}).get(climate_zone, [])
        season_label = "Start now" if month_now in sowing_months else "Plan ahead"
        
        # Normalize sowing method
        sowing_method = plant.get("sowing_method", "").lower()
        if "raise seedlings" in sowing_method:
            method_normalized = "raise_seedlings"
        elif "sow direct" in sowing_method:
            method_normalized = "sow_direct"
        else:
            method_normalized = sowing_method
        
        # Generate why bullets (4 reasons based on highest scores)
        why_bullets = []
        
        # Sort breakdown by score values
        sorted_breakdown = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        
        # Generate explanations based on top factors
        for factor, value in sorted_breakdown[:4]:
            if value > 0.1:  # Only include significant factors
                if factor == "season" and value >= 0.7:
                    if season_label == "Start now":
                        why_bullets.append(f"Sowable now in {climate_zone} climate ({', '.join(sowing_months[:3])}).")
                    else:
                        why_bullets.append(f"Ideal sowing time in {climate_zone} climate ({', '.join(sowing_months[:3])}).")
                elif factor == "sun" and value >= 0.7:
                    why_bullets.append(f"{plant['sun_need'].replace('_', ' ').title()} tolerant; matches your site conditions.")
                elif factor == "maintainability" and value >= 0.7:
                    maint_desc = "Hardy" if plant['maintainability_score'] >= 0.8 else "Moderate-care" if plant['maintainability_score'] >= 0.6 else "Special-care"
                    why_bullets.append(f"{maint_desc} plant; aligns with your maintenance preference.")
                elif factor == "site_fit" and value > 0:
                    site_fits = []
                    if user.get("site", {}).get("containers") and plant.get("container_ok"):
                        site_fits.append("container-friendly")
                    if plant.get("habit") in ["dwarf", "compact", "groundcover"]:
                        site_fits.append(f"{plant['habit']} habit")
                    if site_fits:
                        why_bullets.append(f"{' and '.join(site_fits)} suit your space constraints.")
                elif factor == "preferences" and value > 0:
                    pref_fits = []
                    if plant.get("edible") and "edible" in user.get("preferences", {}).get("goal", ""):
                        pref_fits.append("edible")
                    if plant.get("fragrant") and user.get("preferences", {}).get("fragrant"):
                        pref_fits.append("fragrant")
                    if plant.get("flower_colors") and set(plant["flower_colors"]).intersection(
                            set(user.get("preferences", {}).get("colors", []))):
                        colors = set(plant["flower_colors"]).intersection(
                            set(user.get("preferences", {}).get("colors", [])))
                        pref_fits.append(f"{', '.join(colors)} colored")
                    if pref_fits:
                        why_bullets.append(f"{' and '.join(pref_fits)} traits match your preferences.")
                elif factor == "eco_bonus" and value > 0:
                    why_bullets.append("Pollinator-friendly; supports biodiversity.")
                
                # Limit to 4 bullets
                if len(why_bullets) >= 4:
                    break
        
        # Fill up to 4 bullets if needed
        while len(why_bullets) < 4:
            why_bullets.append("Well-suited to your growing conditions.")
        
        # Trim to exactly 4
        why_bullets = why_bullets[:4]
        
        recommendation = {
            "plant_name": plant.get("plant_name", ""),
            "scientific_name": plant.get("scientific_name", ""),
            "plant_category": plant.get("plant_category", ""),
            "score": round(score, 1),
            "why": why_bullets,
            "fit": {
                "sun_need": plant.get("sun_need", ""),
                "time_to_maturity_days": plant.get("time_to_maturity_days"),
                "maintainability": "hardy" if plant.get("maintainability_score", 0) >= 0.8 else 
                                  "moderate" if plant.get("maintainability_score", 0) >= 0.6 else "specialty",
                "container_ok": plant.get("container_ok", False),
                "indoor_ok": plant.get("indoor_ok", False),
                "habit": plant.get("habit", "")
            },
            "sowing": {
                "climate_zone": climate_zone,
                "months": sowing_months,
                "method": method_normalized,
                "depth_mm": plant.get("sowing_depth_mm"),
                "spacing_cm": plant.get("spacing_cm"),
                "season_label": season_label
            },
            "media": {
                "image_path": plant.get("image_path", "")
            }
        }
        
        recommendations.append(recommendation)
    
    return {
        "recommendations": recommendations,
        "notes": notes
    }