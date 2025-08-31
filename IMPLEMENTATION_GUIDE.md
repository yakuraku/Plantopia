# Plantopia Recommendation Engine - Implementation Guide

This guide provides frontend developers with the information needed to integrate with the Plantopia backend recommendation engine.

## Overview

The Plantopia Recommendation Engine provides personalized plant recommendations based on user preferences and environmental data. The backend processes user inputs, analyzes plant data, and returns tailored recommendations.

## API Endpoints

The backend can be accessed via two methods:

1. **Command Line Interface** - for direct execution
2. **REST API** - for integration with frontend applications

### REST API

The FastAPI backend runs on port 8000 by default. To start the API server:

```bash
uvicorn api:app --reload
```

Or alternatively:

```bash
python api.py
```

#### POST `/recommendations`

Generate plant recommendations based on user preferences and location.

**Request Body:**

```json
{
  "suburb": "Richmond",
  "n": 5,
  "climate_zone": null,
  "user_preferences": {
    "user_id": "anon_mvp",
    "site": {
      "location_type": "balcony",
      "area_m2": 2.0,
      "sun_exposure": "part_sun",
      "wind_exposure": "moderate",
      "containers": true,
      "container_sizes": ["small", "medium"]
    },
    "preferences": {
      "goal": "mixed",
      "edible_types": ["herbs", "leafy"],
      "ornamental_types": ["flowers"],
      "colors": ["purple", "white"],
      "fragrant": true,
      "maintainability": "low",
      "watering": "medium",
      "time_to_results": "quick",
      "season_intent": "start_now",
      "pollen_sensitive": false
    },
    "practical": {
      "budget": "medium",
      "has_basic_tools": true,
      "organic_only": false
    },
    "environment": {
      "climate_zone": "temperate",
      "month_now": "",
      "uv_index": 0.0,
      "temperature_c": 8.0,
      "humidity_pct": 75,
      "wind_speed_kph": 15
    }
  }
}
```

**Response:**

The API returns the same JSON structure as the command-line version:

```json
{
  "recommendations": [
    {
      "plant_name": "Basil",
      "scientific_name": "Ocimum basilicum",
      "plant_category": "herb",
      "score": 95.2,
      "why": [
        "Sowable now in cool climate (August, September, October).",
        "Part sun tolerant; matches your site conditions.",
        "Hardy plant; aligns with your maintenance preference.",
        "Fragrant traits match your preferences."
      ],
      "fit": {
        "sun_need": "part_sun",
        "time_to_maturity_days": 60,
        "maintainability": "hardy",
        "container_ok": true,
        "indoor_ok": true,
        "habit": "compact"
      },
      "sowing": {
        "climate_zone": "cool",
        "months": ["August", "September", "October"],
        "method": "sow_direct",
        "depth_mm": 5,
        "spacing_cm": 20,
        "season_label": "Start now"
      },
      "media": {
        "image_path": "herb_plant_images/basil.jpg"
      }
    }
  ],
  "notes": [],
  "suburb": "Richmond",
  "climate_zone": "cool",
  "month_now": "August"
}
```

### Command Line Interface

The backend is also a Python script that can be executed via command line. The main entry point is `main.py`.

### Command Line Interface

```bash
python main.py --suburb "Richmond" --n 5 --climate climate_data.json --prefs user_preferences.json --out recommendations.json --pretty
```

### Parameters

| Parameter | Description | Required | Default |
|----------|-------------|----------|---------|
| `--suburb` | Suburb for climate data lookup | Yes | "Richmond" |
| `--n` | Number of recommendations to return | No | 5 |
| `--climate` | Path to climate data JSON file | No | "climate_data.json" |
| `--prefs` | Path to user preferences JSON file | No | "user_preferences.json" |
| `--out` | Output file for recommendations | No | "recommendations.json" |
| `--pretty` | Pretty print JSON output | No | (none) |
| `--climate-zone` | Override climate zone | No | (none) |

## Input: User Preferences JSON

The frontend should send user preferences in the following JSON format:

```json
{
  "user_id": "anon_mvp",
  "site": {
    "location_type": "balcony",
    "area_m2": 2.0,
    "sun_exposure": "part_sun",
    "wind_exposure": "moderate",
    "containers": true,
    "container_sizes": ["small", "medium"]
  },
  "preferences": {
    "goal": "mixed",
    "edible_types": ["herbs", "leafy"],
    "ornamental_types": ["flowers"],
    "colors": ["purple", "white"],
    "fragrant": true,
    "maintainability": "low",
    "watering": "medium",
    "time_to_results": "quick",
    "season_intent": "start_now",
    "pollen_sensitive": false
  },
  "practical": {
    "budget": "medium",
    "has_basic_tools": true,
    "organic_only": false
  },
  "environment": {
    "climate_zone": "temperate",
    "month_now": "August",
    "uv_index": 0.0,
    "temperature_c": 8.0,
    "humidity_pct": 75,
    "wind_speed_kph": 15
  }
}
```

### Key Fields Explanation

1. **site.location_type**: "balcony", "garden", "indoors", etc.
2. **site.sun_exposure**: "bright_shade", "part_sun", "full_sun"
3. **site.wind_exposure**: "sheltered", "moderate", "windy"
4. **preferences.goal**: "edible", "ornamental", "mixed"
5. **preferences.maintainability**: "low", "medium", "high"
6. **preferences.time_to_results**: "quick", "standard", "patient"
7. **environment.climate_zone**: "cool", "temperate", "subtropical", "tropical", "arid"

## Input: Climate Data

Climate data is automatically selected based on the suburb name. The system contains data for 151+ Melbourne suburbs with real-time weather information.

## Output: Recommendations JSON

The engine returns recommendations in the following format:

```json
{
  "recommendations": [
    {
      "plant_name": "Basil",
      "scientific_name": "Ocimum basilicum",
      "plant_category": "herb",
      "score": 95.2,
      "why": [
        "Sowable now in cool climate (August, September, October).",
        "Part sun tolerant; matches your site conditions.",
        "Hardy plant; aligns with your maintenance preference.",
        "Fragrant traits match your preferences."
      ],
      "fit": {
        "sun_need": "part_sun",
        "time_to_maturity_days": 60,
        "maintainability": "hardy",
        "container_ok": true,
        "indoor_ok": true,
        "habit": "compact"
      },
      "sowing": {
        "climate_zone": "cool",
        "months": ["August", "September", "October"],
        "method": "sow_direct",
        "depth_mm": 5,
        "spacing_cm": 20,
        "season_label": "Start now"
      },
      "media": {
        "image_path": "herb_plant_images/basil.jpg"
      }
    }
  ],
  "notes": []
}
```

## Integration Steps

1. **Collect User Data**: Gather user preferences through the frontend interface
2. **Format JSON**: Structure the data according to the user preferences schema
3. **Execute Backend**: Run the recommendation engine with the appropriate parameters
4. **Parse Results**: Process the JSON output to display recommendations in the UI
5. **Display Recommendations**: Show plants with their attributes, sowing instructions, and reasoning

## Error Handling

The backend will return error messages to stderr if:
- Plant data files are missing or corrupted
- Climate data files are missing or corrupted
- User preferences file is invalid JSON
- Output file cannot be written

## Performance Considerations

- The engine processes all plant data on each run (flowers, herbs, vegetables)
- Processing time is typically 1-3 seconds
- Results are deterministic for the same inputs
- Caching of climate data is handled internally

## Example Usage

```bash
# Basic usage with default files
python main.py --suburb "Richmond" --n 5

# With custom preferences
python main.py --suburb "St Kilda" --n 3 --prefs custom_preferences.json --out my_recommendations.json --pretty

# With climate zone override
python main.py --suburb "Unknown Suburb" --climate-zone "subtropical" --out recommendations.json
```

## Support

For integration questions, contact the backend team with:
1. Sample user preference JSON
2. Expected vs actual results
3. Error messages received