"""
Simple API test to verify companion planting data is included in recommendations response.
This test uses httpx to make direct API calls without needing to start the server.
"""
import json

# Sample request payload
request_payload = {
    "suburb": "Richmond",
    "n": 5,
    "climate_zone": "temperate",
    "user_preferences": {
        "user_id": "test_user",
        "site": {
            "location_type": "backyard",
            "area_m2": 10.0,
            "sun_exposure": "full_sun",
            "wind_exposure": "moderate",
            "containers": False,
            "container_sizes": ["medium"]
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
            "month_now": "",
            "uv_index": 0.0,
            "temperature_c": 18.0,
            "humidity_pct": 70,
            "wind_speed_kph": 15
        }
    }
}

print("=" * 80)
print("COMPANION PLANTING API TEST")
print("=" * 80)
print("\nThis test will verify that the recommendations API includes companion planting data.")
print("\nTo run this test:")
print("1. Start the API server:")
print("   cd D:\\MAIN_PROJECT\\Plantopia")
print("   python -m uvicorn app.main:app --reload")
print("\n2. In another terminal, run this curl command:")
print("\ncurl -X POST http://localhost:8000/api/v1/recommendations \\")
print("  -H \"Content-Type: application/json\" \\")
print(f"  -d '{json.dumps(request_payload, indent=2)}'")
print("\n3. Verify that each recommendation in the response includes:")
print("   - beneficial_companions")
print("   - harmful_companions")
print("   - neutral_companions")
print("\n" + "=" * 80)
print("\nSample expected response structure:")
print(json.dumps({
    "recommendations": [
        {
            "plant_name": "Example Plant",
            "scientific_name": "Plantus exampleus",
            "score": 85.5,
            "beneficial_companions": "Tomatoes, Beans, Carrots",
            "harmful_companions": "Fennel",
            "neutral_companions": "Lettuce, Spinach",
            "media": {
                "image_url": "https://...",
                "has_image": True
            }
        }
    ]
}, indent=2))
print("\n" + "=" * 80)
