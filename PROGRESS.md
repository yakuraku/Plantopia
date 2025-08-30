# Plantopia Recommendation Engine - Project Progress

This file contains all essential information about the Plantopia Recommendation Engine project to provide complete context for future development work.

## Project Overview

Plantopia is a plant recommendation system that provides personalized plant suggestions based on user preferences and environmental conditions. The system combines plant data with real-time climate information to recommend suitable plants for specific locations and user needs.

## Repository Structure

```
Plantopia-Main/
├── main.py                           # Entry point for the recommendation engine
├── recommender/                      # Core recommendation engine modules
│   ├── __init__.py
│   ├── engine.py                     # Main processing logic
│   ├── normalization.py              # Data normalization functions
│   └── scoring.py                    # Scoring algorithms
├── CLIMATE_DATA/                     # Climate data integration system
│   ├── melbourne_climate_optimized.py
│   ├── open_meteo_client.py
│   ├── waqi_client.py
│   ├── uv_index_client.py
│   ├── epa_api_client.py
│   ├── process_all_suburbs.py
│   └── PROJECT_DOCUMENTATION.md
├── data files
│   ├── flower_plants_data.csv        # Flower plant data
│   ├── herbs_plants_data.csv         # Herb plant data
│   ├── vegetable_plants_data.csv     # Vegetable plant data
│   ├── climate_data.json             # Climate data for Melbourne suburbs
│   └── user_preferences.json         # Example user preferences
├── documentation files
│   ├── IMPLEMENTATION_GUIDE.md       # Guide for frontend integration
│   ├── YASH.md                       # Technical summary (Yash's documentation)
│   └── QWEN.md                       # Original project context
├── requirements.txt                  # Python dependencies
├── README.md
└── LICENSE
```

## Core Functionality

### Data Processing

The system processes three categories of plant data:
1. **Flowers** - Ornamental plants
2. **Herbs** - Culinary and medicinal herbs
3. **Vegetables** - Edible vegetables

Each dataset is normalized through the `recommender.normalization` module which:
- Cleans text fields by removing markdown markers
- Parses time-to-maturity values
- Extracts sowing months by climate zone
- Derives plant characteristics like sun needs, container suitability, etc.

### Recommendation Engine

The recommendation process follows these steps:
1. Load and normalize all plant data
2. Select environment based on suburb
3. Apply hard filters (season, goal, site requirements)
4. Relax filters if needed to reach target number of recommendations
5. Score and rank candidates
6. Apply category diversity cap (max 2 per category initially)
7. Generate explanations for top recommendations

### Scoring System

Each plant is scored based on multiple factors with the following weights:
- **Season compatibility** (25% weight): How well the plant's sowing period matches the current month
- **Sun compatibility** (20% weight): Match between plant's sun needs and site conditions
- **Maintainability** (15% weight): How well the plant matches user's maintenance preferences
- **Time to results** (10% weight): How quickly the plant produces results
- **Site fit** (10% weight): Compatibility with containers, space, and location
- **User preferences** (12% weight): Edible/ornamental types, colors, fragrance
- **Wind penalty** (3% weight): Reduction for tall plants in windy conditions
- **Eco bonus** (5% weight): Bonus for pollinator-friendly plants

## Climate Data Integration

The system includes a comprehensive climate data integration module that collects real-time data from multiple sources:
- **Open-Meteo**: Weather data (temperature, humidity, wind, pressure)
- **WAQI**: Air quality data (AQI, pollutants)
- **ARPANSA**: UV index data

The system covers 151+ Melbourne suburbs with GPS coordinates and provides optimized data collection using the best source for each parameter.

## API Usage

### Command Line Interface

The main entry point is `main.py` with the following parameters:
```bash
python main.py --suburb "Richmond" --n 5 --climate climate_data.json --prefs user_preferences.json --out recommendations.json --pretty
```

Parameters:
- `--suburb`: Suburb for climate data lookup (default: "Richmond")
- `--n`: Number of recommendations to return (default: 5)
- `--climate`: Path to climate data JSON file (default: "climate_data.json")
- `--prefs`: Path to user preferences JSON file (default: "user_preferences.json")
- `--out`: Output file for recommendations (default: "recommendations.json")
- `--pretty`: Pretty print JSON output
- `--climate-zone`: Override climate zone (e.g., cool|temperate|subtropical|tropical|arid)

### Input Format

User preferences are provided in JSON format:
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

### Output Format

Recommendations are returned in JSON format:
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

## Technical Implementation Details

### Key Components

1. **Data Normalization** (`recommender.normalization`):
   - Text cleaning and standardization
   - Parsing of time-to-maturity values
   - Extraction of sowing months by climate zone
   - Derivation of plant characteristics

2. **Engine Logic** (`recommender.engine`):
   - Plant data loading and normalization
   - Environment selection based on suburb
   - Hard filtering of plants
   - Filter relaxation when needed
   - Scoring and ranking
   - Diversity capping
   - Output assembly

3. **Scoring Algorithms** (`recommender.scoring`):
   - Season compatibility scoring
   - Sun compatibility scoring
   - Maintainability scoring
   - Time to results scoring
   - Site fit scoring
   - User preferences scoring
   - Wind penalty calculation
   - Eco bonus calculation

### Dependencies

The project requires:
- pandas
- python-dateutil

Install with:
```bash
pip install -r requirements.txt
```

## Documentation Files

For additional details, refer to these documentation files:
- `IMPLEMENTATION_GUIDE.md`: Guide for frontend developers on integration
- `YASH.md`: Comprehensive technical summary of the project
- `QWEN.md`: Original project context and usage instructions
- `CLIMATE_DATA/PROJECT_DOCUMENTATION.md`: Detailed documentation of the climate data integration system

## Recent Work

Documentation files created:
1. `IMPLEMENTATION_GUIDE.md` - For frontend team integration
2. `YASH.md` - Technical summary of the project
3. `PROGRESS.md` - This file containing comprehensive project context

The climate data integration system was added to the project, providing real-time weather, air quality, and UV index data for 151+ Melbourne suburbs.

## Next Steps

Future enhancements could include:
- Implementing caching for climate data
- Adding historical climate data analysis
- Integrating soil quality data
- Adding pollen count data
- Implementing a web API for easier frontend integration