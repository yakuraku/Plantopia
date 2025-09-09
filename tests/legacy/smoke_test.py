import os
import sys
import json
import sys
sys.path.append('../..')
from app.recommender.engine import load_all_plants, select_environment, get_user_preferences, hard_filter, relax_if_needed, score_and_rank, assemble_output, category_diversity
from app.recommender.scoring import weights

def test_smoke():
    """Run a smoke test of the recommendation engine."""
    # Load plant data
    csv_paths = {
        "flower": "../../data/csv/flower_plants_data.csv",
        "herb": "../../data/csv/herbs_plants_data.csv",
        "vegetable": "../../data/csv/vegetable_plants_data.csv"
    }
    
    try:
        all_plants = load_all_plants(csv_paths)
        print(f"Loaded {len(all_plants)} plants")
    except Exception as e:
        print(f"Error loading plant data: {e}")
        return False
    
    # Load environment and user preferences
    try:
        if os.path.exists("../../data/json/climate_data.json"):
            with open("../../data/json/climate_data.json", 'r', encoding='utf-8') as f:
                climate_data = json.load(f)
        else:
            climate_data = {}
            print("climate_data.json not found, using defaults")
    except Exception as e:
        print(f"Error loading climate data: {e}")
        climate_data = {}
    
    env = select_environment("Richmond", climate_data)
    print(f"Environment: {env}")
    
    try:
        user_prefs = get_user_preferences("user_preferences.json")
    except Exception as e:
        print(f"Error loading user preferences: {e}")
        # Use default preferences
        user_prefs = {
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
            }
        }
    
    # Filter plants
    eligible_plants = hard_filter(all_plants, user_prefs, env)
    print(f"Found {len(eligible_plants)} eligible plants")
    
    # Relax filters if needed
    final_candidates = relax_if_needed(eligible_plants, all_plants, user_prefs, env, 5)
    print(f"After relaxation: {len(final_candidates)} candidates")
    
    # Score and rank
    scored_plants = score_and_rank(final_candidates, user_prefs, env, weights)
    
    # Apply diversity cap
    diverse_plants = category_diversity(scored_plants, max_per_cat=2)
    
    # Take top 5
    top_plants = diverse_plants[:5]
    
    # Assemble output
    output = assemble_output(top_plants, user_prefs, env, [])
    
    # Validate output structure
    required_keys = ["recommendations", "notes"]
    for key in required_keys:
        if key not in output:
            print(f"Missing required key: {key}")
            return False
    
    if not output["recommendations"]:
        print("No recommendations generated")
        return False
    
    # Check first recommendation
    first_rec = output["recommendations"][0]
    rec_keys = ["plant_name", "scientific_name", "plant_category", "score", "why", "fit", "sowing", "media"]
    for key in rec_keys:
        if key not in first_rec:
            print(f"Missing required recommendation key: {key}")
            return False
    
    print("Smoke test passed!")
    print(f"Generated {len(output['recommendations'])} recommendations")
    
    # Print first recommendation as example
    if output["recommendations"]:
        rec = output["recommendations"][0]
        print(f"\nSample recommendation:")
        print(f"  Name: {rec['plant_name']}")
        print(f"  Category: {rec['plant_category']}")
        print(f"  Score: {rec['score']}")
        print(f"  Why: {rec['why']}")
    
    return True

if __name__ == "__main__":
    success = test_smoke()
    sys.exit(0 if success else 1)