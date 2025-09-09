# Plantopia Recommendation Engine - Implementation Guide

This guide provides frontend developers with the information needed to integrate with the Plantopia backend recommendation engine.

## Overview

The Plantopia Recommendation Engine provides personalized plant recommendations based on user preferences and environmental data. The backend processes user inputs, analyzes plant data, and returns tailored recommendations.

## API Endpoints

The backend can be accessed via two methods:

1. **Command Line Interface** - for direct execution
2. **REST API** - for integration with frontend applications

The REST API provides three main endpoints:
- `/recommendations` - Get multiple plant recommendations based on user preferences
- `/plant-score` - Get detailed scoring information for a specific plant
- `/plants` - Get all plants from the database (vegetables, herbs, and flowers)

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

#### GET `/plants`

Get all plants from the database (vegetables, herbs, and flowers) with their associated images.

**Parameters:** None

**Response:**

```json
{
  "plants": [
    {
      "plant_name": "Basil",
      "scientific_name": "Ocimum basilicum",
      "plant_category": "herb",
      "plant_type": "Annual herb to 50cm; Culinary use; Aromatic leaves",
      "days_to_maturity": 60,
      "plant_spacing": 20,
      "sowing_depth": 5,
      "position": "Full sun to part sun, moist well drained soil",
      "season": "Spring and summer",
      "germination": "7-14 days @ 18-25°C",
      "sowing_method": "Sow direct or raise seedlings",
      "hardiness_life_cycle": "Frost tender Annual",
      "characteristics": "Aromatic, culinary herb",
      "description": "Sweet basil is one of the most popular culinary herbs...",
      "additional_information": "Culinary use; Container growing",
      "seed_type": "Open pollinated, untreated, non-GMO variety of seed",
      "image_filename": "herb_plant_images/basil.jpg",
      "cool_climate_sowing_period": "September, October, November",
      "temperate_climate_sowing_period": "August, September, October, November, December",
      "subtropical_climate_sowing_period": "March, April, May, June, July, August, September",
      "tropical_climate_sowing_period": "April, May, June, July, August",
      "arid_climate_sowing_period": "March, April, May, August, September, October",
      "media": {
        "image_path": "herb_plant_images/basil.jpg",
        "image_base64": "data:image/jpeg;base64,...",
        "has_image": true
      }
    }
  ],
  "total_count": 450
}
```

#### POST `/plant-score`

Get the score for a specific plant based on user preferences and location.

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
      "pollen_sensitive": false,
      "pets_or_toddlers": false
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

## Fields to Collect (controls & options)

### A. Site & Space

- `location_type` (radio): `indoors | balcony | courtyard | backyard | community_garden`
- `area_m2` (number input with helper): default `2.0`
- `sun_exposure` (radio): `full_sun (6–8h) | part_sun (3–5h) | bright_shade (1–3h) | low_light (<1h)`
- `wind_exposure` (radio): `sheltered | moderate | windy`
- `containers` (toggle): `true/false`
- `container_sizes` (chips, multi): `small(≤15cm) | medium(16–25) | large(26–40) | very_large(>40)`

### B. Goals & Types

- `goal` (radio): `edible | ornamental | mixed`
- If `goal` includes edible → `edible_types` (chips, multi): `leafy | fruiting | root | herbs | legumes`
- If `goal` includes ornamental → `ornamental_types` (chips, multi): `flowers | foliage | climbers | groundcovers`

### C. Care Preferences

- `maintainability` (radio): `low | medium | high` (how much effort they'll spend)
- `watering` (radio): `low | medium | high`
- `time_to_results` (radio): `quick(≤60d) | standard(60–120d) | patient(>120d)`
- `season_intent` (radio): `start_now | happy_to_wait`

### D. Aesthetics (optional)

- `colors` (chips, multi): `white, yellow, orange, pink, red, purple, blue`
- `fragrant` (toggle): `true/false`

### E. Safety & Practical (optional)

- `pollen_sensitive` (toggle): `true/false`
- `pets_or_toddlers` (toggle): `true/false` (future toxicity filter)
- `budget` (radio): `low | medium | high`
- `has_basic_tools` (toggle): `true/false`
- `organic_only` (toggle): `true/false`

## JSON Payload (send to backend)

Send with the **selected suburb** (and lat/lon if available). Backend will map suburb → environment and default to **cool** for Melbourne/VIC.

```json
{
  "suburb": "Richmond",
  "site": {
    "location_type": "balcony",
    "area_m2": 2.0,
    "sun_exposure": "part_sun",
    "wind_exposure": "moderate",
    "containers": true,
    "container_sizes": ["small","medium"]
  },
  "preferences": {
    "goal": "mixed",
    "edible_types": ["herbs","leafy"],
    "ornamental_types": ["flowers"],
    "colors": ["purple","white"],
    "fragrant": true,
    "maintainability": "low",
    "watering": "medium",
    "time_to_results": "quick",
    "season_intent": "start_now",
    "pollen_sensitive": false,
    "pets_or_toddlers": false
  },
  "practical": {
    "budget": "medium",
    "has_basic_tools": true,
    "organic_only": false
  }
}
```

### Defaults if user skips everything

```json
{
  "site": {
    "location_type": "balcony",
    "area_m2": 2.0,
    "sun_exposure": "part_sun",
    "wind_exposure": "moderate",
    "containers": true,
    "container_sizes": ["small","medium"]
  },
  "preferences": {
    "goal": "mixed",
    "edible_types": ["herbs","leafy"],
    "ornamental_types": ["flowers"],
    "colors": [],
    "fragrant": false,
    "maintainability": "low",
    "watering": "medium",
    "time_to_results": "standard",
    "season_intent": "start_now",
    "pollen_sensitive": false,
    "pets_or_toddlers": false
  },
  "practical": {
    "budget": "medium",
    "has_basic_tools": true,
    "organic_only": false
  }
}
```

## Conditional UI Logic (keep it simple)

- If `location_type = indoors` → keep `containers = true` by default; emphasize `bright_shade / low_light`.
- If `location_type ∈ {balcony, indoors}` → show `container_sizes`.
- If `area_m2 < 3` OR only `small/medium` pots → show helper text "We'll favor compact/dwarf/container-friendly plants."
- If `goal = edible` → show only edible chips; if `ornamental` → show only ornamental chips; if `mixed` → show both.
- Show an **Advanced** accordion with read-only "Detected climate: **cool** (Melbourne)" (no need to let users change it in MVP).

## Light Validation

- `area_m2`: min `0.2`, max `50`.
- Arrays (chips): allow empty (treated as "no strong preference").
- Strings: lowercase, dash/underscore free on your side is fine—the backend normalizes anyway.

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
    "pollen_sensitive": false,
    "pets_or_toddlers": false
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

**Plant Score Request Body:**

```json
{
  "plant_name": "Basil",
  "suburb": "Richmond",
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
      "pollen_sensitive": false,
      "pets_or_toddlers": false
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

**Plant Score Response:**

```json
{
  "plant_name": "Basil",
  "scientific_name": "Ocimum basilicum",
  "plant_category": "herb",
  "score": 95.2,
  "score_breakdown": {
    "season": 1.0,
    "sun": 0.7,
    "maintainability": 0.8,
    "time_to_results": 0.9,
    "site_fit": 0.4,
    "preferences": 0.6,
    "wind_penalty": 1.0,
    "eco_bonus": 0.0
  },
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
    "image_path": "herb_plant_images/basil.jpg",
    "image_base64": "data:image/jpeg;base64,...",
    "has_image": true
  },
  "suburb": "Richmond",
  "climate_zone": "cool",
  "month_now": "August"
}
```

## New Feature: Plant Score Endpoint

The `/plant-score` endpoint allows you to get detailed scoring information for a specific plant. This is useful when users want to:

1. **Check a specific plant**: See how well a particular plant matches their preferences and location
2. **Compare plants**: Get detailed score breakdowns to understand why one plant scores higher than another
3. **Understand scoring**: See the detailed breakdown of how the recommendation engine calculates scores

### Key Features

- **Plant Search**: Supports searching by plant name or scientific name (partial matches work)
- **Detailed Scoring**: Returns a complete breakdown of all scoring factors
- **Same Context**: Uses the same user preferences and environmental data as recommendations
- **Rich Response**: Includes all plant details, sowing information, and media

### Plant Name Matching

The endpoint supports flexible plant name matching:
- Exact plant name match: "Basil"
- Exact scientific name match: "Ocimum basilicum"  
- Partial matches: "bas" would match "Basil"
- Case insensitive: "basil", "BASIL", "Basil" all work

### Error Handling

- Returns HTTP 404 if the plant is not found
- Returns HTTP 500 for other errors (malformed request, missing files, etc.)

## New Feature: All Plants Endpoint

The `/plants` endpoint provides access to the complete plant database, including vegetables, herbs, and flowers. This is useful when you need to:

1. **Browse All Plants**: Display a comprehensive catalog of all available plants
2. **Search and Filter**: Implement client-side search and filtering functionality
3. **Plant Details**: Show detailed information about plants without needing user preferences
4. **Catalog Views**: Create category-based views (vegetables, herbs, flowers)

### Key Features

- **Complete Database**: Returns all plants from vegetable_plants_data.csv, herbs_plants_data.csv, and flower_plants_data.csv
- **Rich Data**: Includes all plant attributes like scientific names, growing requirements, sowing periods, etc.
- **Image Support**: All plant images are converted to base64 for easy frontend integration
- **Performance**: Single endpoint call returns all data - no pagination needed for MVP
- **Categories**: Each plant includes its category (vegetable, herb, flower) for easy filtering

### Data Structure

Each plant object includes:
- **Basic Info**: plant_name, scientific_name, plant_category, plant_type
- **Growing Details**: days_to_maturity, plant_spacing, sowing_depth, position requirements
- **Timing**: season, germination period, climate-specific sowing periods
- **Care Instructions**: sowing_method, hardiness_life_cycle, characteristics
- **Descriptions**: detailed description and additional_information
- **Media**: image_path, base64 encoded image data, and availability flag

### Frontend Integration Examples

```javascript
// Fetch all plants
const response = await fetch('/plants');
const data = await response.json();
console.log(`Total plants: ${data.total_count}`);

// Filter by category
const herbs = data.plants.filter(plant => plant.plant_category === 'herb');
const vegetables = data.plants.filter(plant => plant.plant_category === 'vegetable');
const flowers = data.plants.filter(plant => plant.plant_category === 'flower');

// Search by name
const searchTerm = 'basil';
const results = data.plants.filter(plant => 
  plant.plant_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
  plant.scientific_name.toLowerCase().includes(searchTerm.toLowerCase())
);

// Display plant with image
plants.forEach(plant => {
  if (plant.media.has_image) {
    // Use plant.media.image_base64 as src for img tag
    console.log(`${plant.plant_name} has an image`);
  }
});
```

## Integration Steps

1. **Collect User Data**: Gather user preferences through the frontend interface
2. **Format JSON**: Structure the data according to the user preferences schema
3. **Execute Backend**: 
   - Use `/recommendations` for getting multiple plant suggestions
   - Use `/plant-score` for getting detailed information about a specific plant
   - Use `/plants` for getting all plants in the database for browsing/searching
4. **Parse Results**: Process the JSON output to display recommendations or plant scores in the UI
5. **Display Information**: Show plants with their attributes, sowing instructions, and reasoning

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