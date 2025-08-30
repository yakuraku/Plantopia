import argparse
import json
import sys
from recommender.engine import load_all_plants, select_environment, get_user_preferences, hard_filter, relax_if_needed, score_and_rank, assemble_output, category_diversity
from recommender.scoring import weights

def main():
    parser = argparse.ArgumentParser(description="Plant Recommendation Engine")
    parser.add_argument("--suburb", default="Richmond", help="Suburb for climate data")
    parser.add_argument("--n", type=int, default=5, help="Number of recommendations")
    parser.add_argument("--climate", default="climate_data.json", help="Climate data JSON file")
    parser.add_argument("--prefs", default="user_preferences.json", help="User preferences JSON file")
    parser.add_argument("--out", default="recommendations.json", help="Output JSON file")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    parser.add_argument("--climate-zone", type=str, default=None,
        help="Override climate zone (e.g., cool|temperate|subtropical|tropical|arid)")
    
    args = parser.parse_args()
    
    # Load plant data
    csv_paths = {
        "flower": "flower_plants_data.csv",
        "herb": "herbs_plants_data.csv",
        "vegetable": "vegetable_plants_data.csv"
    }
    
    try:
        all_plants = load_all_plants(csv_paths)
    except Exception as e:
        print(f"Error loading plant data: {e}")
        sys.exit(1)
    
    # Load environment and user preferences
    try:
        with open(args.climate, 'r', encoding='utf-8') as f:
            climate_data = json.load(f)
    except FileNotFoundError:
        print(f"Climate data file {args.climate} not found, using defaults")
        climate_data = {}
    except Exception as e:
        print(f"Error loading climate data: {e}")
        climate_data = {}
    
    env = select_environment(args.suburb, climate_data, cli_override_climate_zone=args.climate_zone)
    
    try:
        user_prefs = get_user_preferences(args.prefs)
    except Exception as e:
        print(f"Error loading user preferences: {e}")
        sys.exit(1)
    
    # Filter plants
    eligible_plants = hard_filter(all_plants, user_prefs, env)
    
    # Relax filters if needed
    final_candidates = relax_if_needed(eligible_plants, all_plants, user_prefs, env, args.n)
    
    # Score and rank
    scored_plants = score_and_rank(final_candidates, user_prefs, env, weights)
    
    # Apply diversity cap
    diverse_plants = category_diversity(scored_plants, max_per_cat=2)
    
    # Take top N
    top_plants = diverse_plants[:args.n]
    
    # Assemble output
    output = assemble_output(top_plants, user_prefs, env, [])
    
    # Add suburb and climate info
    output["suburb"] = args.suburb
    output["climate_zone"] = env["climate_zone"]
    output["month_now"] = env["month_now"]
    
    # Write JSON output
    try:
        with open(args.out, 'w', encoding='utf-8') as f:
            if args.pretty:
                json.dump(output, f, indent=2, ensure_ascii=False)
            else:
                json.dump(output, f, ensure_ascii=False)
        print(f"Recommendations saved to {args.out}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)
    
    # Print summary table
    print(f"\nTop {len(top_plants)} Recommendations for {args.suburb}:")
    print("-" * 60)
    print(f"{'Plant Name':<25} {'Category':<12} {'Score':<8} {'Season'}")
    print("-" * 60)
    for score, plant, _ in top_plants:
        season_label = "Start now" if env["month_now"] in plant["sowing_months_by_climate"].get(env["climate_zone"], []) else "Plan ahead"
        print(f"{plant['plant_name']:<25} {plant['plant_category']:<12} {score:<8.1f} {season_label}")

if __name__ == "__main__":
    main()