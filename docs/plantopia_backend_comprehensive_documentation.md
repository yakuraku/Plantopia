# Plantopia Backend Comprehensive Technical Documentation

## Architecture Overview

FastAPI-based REST API using async SQLAlchemy with PostgreSQL (Supabase). Implements recommendation engine using pandas-based scoring system with climate data integration.

**Tech Stack:**
- Framework: FastAPI (async)
- Database: PostgreSQL + asyncpg driver
- ORM: SQLAlchemy (async mode)
- Data Processing: pandas
- Deployment: Vercel/Railway compatible

**Directory Structure:**
```
app/
├── api/endpoints/      # API route handlers
├── core/              # Config, database setup
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic request/response models
├── services/          # Business logic layer
├── repositories/      # Data access layer
├── recommender/       # Recommendation algorithm
├── utils/             # Helper functions
└── static/uhi/        # Urban heat island data
data/
├── csv/               # Plant CSV files (3 files: flower, herb, vegetable)
├── json/              # Climate reference data
└── MARKDOWN_FILES/    # Educational content (10 categories, 465+ files)
```

## Database Models

### Plant Table
```python
# app/models/database.py: Plant
Fields:
- id: Integer PK
- plant_name: String(255), indexed
- scientific_name: String(255)
- plant_category: String(50), indexed (flower/herb/vegetable)

# Growing Requirements
- water_requirements: String(100)
- sunlight_requirements: String(100)
- soil_type: String(200)
- growth_time: String(100)
- maintenance_level: String(50)
- climate_zone: String(100)

# Characteristics
- mature_height: String(100)
- mature_width: String(100)
- flower_color: String(200)
- flowering_season: String(200)
- description: Text
- position: Text
- characteristics: Text

# CSV Fields
- plant_type: Text
- season: String(100)
- germination: String(200)
- additional_information: Text
- days_to_maturity: String(100)
- plant_spacing: String(100)
- sowing_depth: String(100)
- hardiness_life_cycle: String(200)
- seed_type: String(100)

# Companion Planting (comma-separated strings)
- beneficial_companions: Text
- harmful_companions: Text
- neutral_companions: Text

# Climate Sowing Periods
- cool_climate_sowing_period: String(200)
- temperate_climate_sowing_period: String(200)
- subtropical_climate_sowing_period: String(200)
- tropical_climate_sowing_period: String(200)
- arid_climate_sowing_period: String(200)

# Recommendation Engine Fields
- sun_need: String(50) # full_sun/part_sun/bright_shade
- indoor_ok: Boolean
- container_ok: Boolean
- edible: Boolean
- sowing_months_by_climate: JSON # {"temperate": ["March", "April"]}
- maintainability_score: Float (0.0-1.0)
- time_to_maturity_days: Integer
- habit: String(100)
- fragrant: Boolean
- flower_colors: JSON # ["purple", "white"]
- sowing_depth_mm: Integer
- spacing_cm: Integer
- sowing_method: Text
- image_url: Text

# Metadata
- created_at: DateTime
- updated_at: DateTime

# Index
idx_plant_category_name on (plant_category, plant_name)
```

### Suburb Table
```python
# app/models/database.py: Suburb
Fields:
- id: Integer PK
- name: String(100), unique, indexed
- postcode: String(10)
- latitude: Float
- longitude: Float
- state: String(50), default='VIC'

# Urban Heat Island Data
- suburb_heat_category: String(50) # Low/Moderate/High/Extreme Heat
- suburb_heat_intensity: Float # Celsius

# Relationships
- climate_data: One-to-Many -> ClimateData
- recommendations: One-to-Many -> UserRecommendation

# Metadata
- created_at: DateTime
- updated_at: DateTime
```

### ClimateData Table
```python
# app/models/database.py: ClimateData
Fields:
- id: Integer PK
- suburb_id: Integer FK(suburbs.id)

# Weather Data (Open-Meteo)
- temperature_current: Float
- temperature_max: Float
- temperature_min: Float
- humidity: Integer
- rainfall: Float
- wind_speed: Float
- weather_code: Integer # WMO code

# UV Data (ARPANSA)
- uv_index: Float
- uv_category: String(50) # Low/Moderate/High/Very High/Extreme
- uv_protection_required: String(10) # Yes/No

# Air Quality (WAQI/EPA)
- air_quality_index: Integer
- air_quality_category: String(50)
- pm25: Float
- pm10: Float
- ozone: Float
- nitrogen_dioxide: Float
- sulfur_dioxide: Float
- carbon_monoxide: Float

# Metadata
- recorded_date: Date, default=today
- data_source: JSON # Tracks API sources
- created_at: DateTime

# Constraints
UniqueConstraint('suburb_id', 'recorded_date')
Index('idx_climate_suburb_date', 'suburb_id', 'recorded_date')
```

### APICache Table
```python
# app/models/database.py: APICache
Fields:
- id: Integer PK
- api_name: String(100), unique # open_meteo/arpansa/waqi/epa
- last_update: DateTime
- last_success: DateTime
- status: String(50) # success/error/timeout/rate_limited
- error_message: Text
- response_time_ms: Integer
- records_updated: Integer
- created_at: DateTime
- updated_at: DateTime
```

### UserRecommendation Table
```python
# app/models/database.py: UserRecommendation
Fields:
- id: Integer PK
- suburb_id: Integer FK(suburbs.id)
- preferences: JSON # User preference object
- recommended_plants: JSON # Array of {plant_id, score}
- request_ip: String(50)
- user_agent: Text
- response_time_ms: Integer
- created_at: DateTime

# Index
idx_recommendations_created on (created_at)
```

## Database Configuration

```python
# app/core/database.py

# Connection
DATABASE_URL from env, convert to postgresql+asyncpg:// for async

# Engines
Sync engine: pool_size=3, max_overflow=5, pool_pre_ping=True
Async engine: same config with AsyncSession

# Session Factories
SessionLocal: sync sessions
AsyncSessionLocal: async sessions with expire_on_commit=False

# Dependency Functions
get_db() -> Session # sync
get_async_db() -> AsyncSession # async, yields then closes

# Lifecycle
init_db(): Creates all tables via Base.metadata.create_all
close_db(): Disposes async_engine
```

## API Endpoints

### Health
```
GET / -> {message, version}
GET /api/v1/ -> HealthCheckResponse
```

### Plants
```
GET /api/v1/plants
Returns: AllPlantsResponse {plants[], total_count}
Notes: Includes companion data (beneficial/harmful/neutral_companions)

GET /api/v1/plants/paginated?page=1&limit=12&category=herb&search=basil
Query Params:
  - page: int, default=1
  - limit: int, default=12, max=100
  - category: flower/herb/vegetable (optional)
  - search: string (searches name, scientific_name, description)
Returns: PaginatedPlantsResponse {plants[], page, limit, total, total_pages, has_next, has_previous}

GET /api/v1/plants/{plant_id}/image-url
Returns: {image_url: string} # Primary GCS URL

GET /api/v1/plants/{plant_id}/all-images
Returns: {image_urls: string[]} # All GCS URLs (2-4 per plant)

GET /api/v1/plants/{plant_id}/companions
Returns: {plant_id, plant_name, scientific_name, plant_category, companion_planting: {
  beneficial_companions: string[],
  harmful_companions: string[],
  neutral_companions: string[]
}}
Notes: Parses comma-separated strings into arrays
```

### Recommendations
```
POST /api/v1/recommendations
Body: RecommendationRequest {
  suburb: string,
  n: int (1-9),
  climate_zone?: string,
  user_preferences: UserRequest {
    user_id: string,
    site: SitePreferences {
      location_type: string, # balcony/backyard/indoor
      area_m2: float,
      sun_exposure: string, # full_sun/part_sun/bright_shade
      wind_exposure: string,
      containers: boolean,
      container_sizes: string[]
    },
    preferences: UserPreferences {
      goal: string, # edible/ornamental/mixed
      edible_types: string[],
      ornamental_types: string[],
      colors: string[],
      fragrant: boolean,
      maintainability: string, # low/medium/high
      watering: string,
      time_to_results: string, # quick/standard/patient
      season_intent: string,
      pollen_sensitive: boolean
    },
    practical: PracticalPreferences {
      budget: string,
      has_basic_tools: boolean,
      organic_only: boolean
    },
    environment: EnvironmentPreferences {
      climate_zone: string,
      month_now: string,
      uv_index: float,
      temperature_c: float,
      humidity_pct: int,
      wind_speed_kph: int
    }
  }
}
Returns: {
  recommendations: PlantRecommendation[] {
    plant_name, scientific_name, plant_category, score, why_recommended,
    sowing: {climate_zone, months[], method, depth_mm, spacing_cm, season_label},
    media: {image_path, image_base64, has_image},
    care_tips: string[]
  },
  context: object,
  summary: object,
  suburb: string,
  climate_zone: string,
  month_now: string
}

POST /api/v1/plant-score
Body: PlantScoreRequest {plant_name, suburb, climate_zone?, user_preferences}
Returns: PlantScoreResponse {plant_name, score, score_breakdown, fit, sowing, media}

POST /api/v1/recommendations-with-impact
Body: Same as /recommendations
Returns: Same as /recommendations but each recommendation includes quantified_impact field
```

### Quantification
```
POST /api/v1/quantify-plant
Body: PlantQuantificationRequest {
  plant_name: string,
  suburb: string,
  climate_zone?: string,
  plant_count: int (1-100),
  user_preferences: UserRequest
}
Returns: PlantQuantificationResponse {
  plant_name, scientific_name, plant_category,
  quantified_impact: {
    temperature_reduction_c: float,
    air_quality_points: int (0-15),
    co2_absorption_kg_year: float,
    water_processed_l_week: float,
    pollinator_support: string, # Minimal/Low/Medium/High
    edible_yield?: string,
    maintenance_time: string,
    water_requirement: string,
    risk_badge: string, # low/medium/high
    confidence_level: string, # with percentage
    why_this_plant: string,
    community_impact_potential?: string
  },
  suitability_score: {total_score: float, breakdown: object},
  suburb, climate_zone, plant_count
}

POST /api/v1/batch-quantify
Body: PlantQuantificationRequest[] (max 20)
Returns: PlantQuantificationResponse[]
Notes: Skips 404 plants, continues with others

GET /api/v1/quantification-info
Returns: Framework metadata, methodology, metrics descriptions, factors, confidence levels, limitations
```

### Climate
```
GET /api/v1/suburbs
Returns: {suburbs: Suburb[], total: int}

GET /api/v1/climate/{suburb_name}
Returns: Latest ClimateData for suburb {weather, uv, air_quality}
404 if not found

GET /api/v1/climate/{suburb_name}/history?days=7
Query Params: days (1-30, default=7)
Returns: {suburb, days, history: ClimateData[]}
```

### Admin (development: no auth, production: x-api-key header)
```
POST /api/v1/admin/climate/update
Background task: Updates all suburbs climate data
Returns: {message, status: "processing", suburbs_count}

POST /api/v1/admin/climate/update/{suburb_name}
Synchronously updates single suburb
Returns: {message, data: ClimateData} or 400 with error

GET /api/v1/admin/climate/status
Returns: Update status for all APIs {api_name, last_update, status, etc}
```

### Urban Heat Island (UHI)
```
GET /api/v1/uhi/boundaries?simplified=true
Returns: {url: GCS URL, size, description}
Notes: simplified=true returns 726KB version, false returns 8.8MB

GET /api/v1/uhi/data
Returns: melbourne_heat_data.json {suburbs[], heat_categories, metadata, statistics}
Notes: Cleans inf/nan values before returning

GET /api/v1/uhi/suburb/{suburb_id}
Returns: {suburb: object, heat_categories}

GET /api/v1/uhi/metadata
Returns: {metadata, statistics, heat_categories}

GET /api/v1/uhi/suburbs/search?q=richmond&limit=10
Returns: {suburbs[], total, query}

GET /api/v1/uhi/suburbs/by-heat?category=extreme&limit=10
Returns: {suburbs[], total, filter} sorted by heat intensity DESC

GET /api/v1/uhi/summary
Returns: CSV file (heat_category_summary.csv)

GET /api/v1/uhi/chart-data
Returns: CSV file (melbourne_heat_chart_data.csv)
```

### Markdown Content
```
GET /api/v1/markdown/categories
Returns: {categories: [{name, slug, file_count}], total_categories}

GET /api/v1/markdown/{category-slug}
Specific endpoints:
  - /beneficial-insects
  - /companion-planting
  - /composting
  - /craft
  - /fertiliser-soil
  - /flowers
  - /grow-guide (255 files)
  - /herbs
  - /informational
  - /pests-diseases
Returns: {category, files: [{filename, title, content, file_size, file_path}]}

GET /api/v1/markdown/category/{category_slug}
Dynamic endpoint, same response as specific endpoints

GET /api/v1/markdown/file/{category_slug}/{filename}
Returns: {category, file: {filename, title, content, file_size, file_path}}
Notes: .md extension optional
```

## Recommendation Engine

### Pipeline (app/recommender/engine.py)
```python
1. load_all_plants(csv_paths) -> Plant[]
   - Loads 3 CSV files (flower/herb/vegetable)
   - Calls normalize_dataframe() per category
   - Returns unified list

2. select_environment(suburb, climate_json, cli_override_climate_zone?) -> env
   - Gets climate data or uses Melbourne CBD default
   - Defaults: climate_zone="cool", month_now=current, temp=15C, humidity=60%, wind=10kph
   - CLI override has highest priority

3. get_user_preferences(json_path) -> user_prefs
   - Loads JSON, extracts site/preferences/practical/environment

4. hard_filter(plants, user_prefs, env) -> eligible[]
   - Filters by sowing_months_by_climate (current month)
   - Filters by sun_need (user site.sun_exposure)
   - Filters by container_ok if site.containers=true
   - Filters by edible/fragrant/pollen_sensitive
   - Returns strict matches

5. relax_if_needed(eligible, all_plants, user_prefs, env, target_n) -> candidates[]
   - If len(eligible) < target_n: relaxes sowing month filter
   - Returns expanded list or original if sufficient

6. score_and_rank(candidates, user_prefs, env, weights) -> scored[]
   - Calls calculate_scores() for each plant
   - Returns [(score, plant, breakdown)] sorted DESC
   - Uses weights from app/recommender/scoring.py

7. category_diversity(scored, max_per_cat, target_count) -> diverse[]
   - Two-pass: first caps at max_per_cat (default=2)
   - Second pass fills to target_count if needed
   - Ensures balanced category distribution

8. assemble_output(top_plants, user_prefs, env, feedback) -> output
   - Builds response with why_recommended explanations
   - Adds sowing info, care tips
   - Returns structured recommendation object
```

### Scoring System (app/recommender/scoring.py)
```python
weights = {
  'goal_match': 0.25,           # Edible/ornamental alignment
  'sun_match': 0.20,            # Sun exposure fit
  'time_to_results': 0.15,      # Maturity speed preference
  'maintenance_match': 0.15,    # Maintainability fit
  'container_suitability': 0.10,# Container compatibility
  'fragrance_bonus': 0.05,      # Fragrance preference
  'color_match': 0.05,          # Color preferences
  'season_timeliness': 0.05     # Sowing season alignment
}

calculate_scores(plant, user_prefs, env, weights) -> (total_score, breakdown)
  - goal_match: 0-100 based on edible/ornamental/mixed goal
  - sun_match: 0-100, 100 for perfect match, 50 for partial, 0 for mismatch
  - time_to_results_score: quick=<75 days, standard=75-120, patient=>120
  - maintenance_score: low/medium/high vs plant maintainability
  - container_score: 100 if container_ok=true, 0 otherwise
  - fragrance_score: 100 if fragrant and user prefers, -20 if user pollen_sensitive
  - color_score: percentage of user colors matching plant.flower_colors
  - season_score: 100 if sowing month matches, 50 otherwise

Total = weighted sum, normalized to 0-100
```

### Normalization (app/recommender/normalization.py)
```python
normalize_dataframe(df, category) -> dict[]
  - Parses CSV columns into structured format
  - Extracts sun_need from 'position' field (full sun/part sun/shade patterns)
  - Parses days_to_maturity string -> time_to_maturity_days int
  - Parses sowing periods -> sowing_months_by_climate JSON
  - Detects edible/container_ok/indoor_ok/fragrant from text fields
  - Extracts flower_colors from text (purple, white, pink, etc)
  - Returns list of normalized plant dicts
```

## Services Layer

### RecommendationService (app/services/recommendation_service.py)
```python
Dependencies: DatabasePlantRepository, ClimateRepository

generate_recommendations(request) -> RecommendationResponse
  - Creates temp file for user prefs JSON
  - Loads all plants from DB
  - Gets climate data for suburb
  - Runs recommendation pipeline
  - Enhances with GCS image URLs
  - Returns structured response

score_plant(request) -> PlantScoreResponse
  - Same pipeline but for single plant
  - Returns detailed score breakdown

_enhance_recommendations_with_images(output) -> output
  - Adds GCS URLs using PlantService.generate_gcs_image_urls()
  - URL format: {GCS_BUCKET_URL}/{category}_plant_images/{PlantName}_{ScientificName}/{PlantName}_{ScientificName}_{1-4}.jpg
  - Removes special chars: ' ( ) , . / : &
```

### PlantService (app/services/plant_service.py)
```python
Dependencies: DatabasePlantRepository

get_all_plants_with_images() -> AllPlantsResponse
  - Gets all plants from DB
  - Adds media object with GCS URLs + base64 fallback

find_plant_with_details(plant_name) -> Plant
  - Searches by plant_name or scientific_name (case-insensitive, partial match)
  - Adds media object

get_plants_paginated(page, limit, category?, search?) -> PaginatedPlantsResponse
  - Calls repository.get_plants_paginated()
  - Adds media objects to each plant
  - Calculates pagination metadata (total_pages, has_next, has_previous)

get_plant_companions(plant_id) -> CompanionData
  - Gets plant by ID
  - Parses comma-separated companion strings into arrays
  - Returns structured {plant_id, plant_name, companion_planting}

generate_gcs_image_urls(plant_name, category, scientific_name) -> string[]
  - Cleans special chars from names
  - Generates 4 URLs: {base}/{name}_{1-4}.jpg
  - Returns array

get_primary_image_url(plant_name, category, scientific_name) -> string
  - Returns first URL from generate_gcs_image_urls()
```

### QuantificationService (app/services/quantification_service.py)
```python
Framework: Per-plant climate impact quantification

quantify_plant_impact(plant, site, preferences, suburb, plant_count) -> QuantifiedImpact
  1. _normalize_context(): Calculates area/sun/wind/uhi/season factors
  2. _derive_plant_biophysics(): Estimates LAI, canopy_area, transpiration_class
  3. _calculate_impact_indices(): Computes raw metrics
  4. _calculate_suitability_score(): Scores vs user prefs
  5. _convert_to_user_impact(): Formats for user display
  6. _calculate_community_impact(): Projects community-scale impact

Impact Metrics:
  - temperature_reduction_c: 0.1-2.0°C based on LAI, canopy, transpiration, UHI context
  - air_quality_points: 0-15 based on leaf area, roughness, aromatics
  - co2_absorption_kg_year: 0.5-50 kg/year based on plant type, canopy, growth speed
  - water_processed_l_week: 1-50 L/week based on transpiration class, canopy, sun
  - pollinator_support: Minimal/Low/Medium/High from flower presence, fragrance, bloom period
  - edible_yield: Estimated from edible=true plants
  - maintenance_time: mins/week from maintainability + plant type
  - water_requirement: L/week based on transpiration + sun + containers
  - risk_badge: low/medium/high from thorns, toxicity, allergens
  - confidence_level: percentage based on data completeness

Biophysics Estimation:
  - LAI (Leaf Area Index): 1.0-4.5 from plant type, habit, mature size
  - canopy_area: m2 from spacing_cm or mature width
  - transpiration_class: low/medium/high from sun_need + water_requirements

Z-score normalization constants:
  - LAI_MEAN=2.5, LAI_STD=0.8
  - CANOPY_MEAN=0.8, CANOPY_STD=0.4

Community impact:
  - Projects to 100 households * impact
  - Formats readable summaries (e.g., "50kg CO2/year = 200km driving")
```

### ClimateUpdateService (app/services/climate_updater.py)
```python
Dependencies: ClimateRepository

update_all_suburbs() -> void
  - Gets all suburbs from DB
  - For each: calls update_single_suburb()
  - Updates APICache table

update_single_suburb(suburb_name) -> {success, data?, error?}
  - Calls Open-Meteo API for weather
  - Calls ARPANSA API for UV index
  - Calls WAQI API for air quality
  - Merges into single ClimateData record
  - Upserts to DB (unique on suburb_id + recorded_date)

get_update_status() -> APICache[]
  - Returns last update status for all APIs
```

## Repositories Layer

### DatabasePlantRepository (app/repositories/database_plant_repository.py)
```python
Dependencies: AsyncSession

get_all_plants() -> Plant[]
  - select(Plant).execute().scalars().all()
  - Converts to dicts via _plant_to_dict()

find_plant_by_name(plant_name) -> Plant?
  - WHERE lower(plant_name) == lower(input) OR contains(input)
  - Same for scientific_name
  - Returns first match or None

get_plant_object_by_name(plant_name) -> Plant ORM object
  - Same query as find_plant_by_name but returns ORM model
  - Used by quantification_service (needs attributes not dict keys)

get_plants_by_category(category) -> Plant[]

search_plants(search_term?, category?, water_requirements?, sunlight_requirements?, maintenance_level?) -> Plant[]
  - Builds WHERE clause with filters
  - LIKE search on plant_name, scientific_name, description

get_plant_by_id(plant_id) -> Plant?

count_plants_by_category() -> {category: count}

get_plants_paginated(page, limit, category?, search_term?) -> (Plant[], total_count)
  - Builds query with filters
  - Gets total count first
  - Applies offset = (page-1)*limit, limit
  - Returns (plants, total)

count_plants(category?, search_term?) -> int

_plant_to_dict(plant) -> dict
  - Converts all Plant fields to dict
  - Includes companion data (beneficial_companions, harmful_companions, neutral_companions)
  - Formats created_at/updated_at as ISO strings
```

### ClimateRepository (app/repositories/climate_repository.py)
```python
Dependencies: AsyncSession

get_all_suburbs() -> Suburb[]

get_suburb_by_name(suburb_name) -> Suburb?
  - Case-insensitive match on name

get_latest_climate_by_suburb(suburb_name) -> ClimateData?
  - Joins Suburb + ClimateData
  - Orders by recorded_date DESC
  - Returns most recent record

get_climate_history(suburb_name, days) -> ClimateData[]
  - Joins Suburb + ClimateData
  - WHERE recorded_date >= today - days
  - Orders by recorded_date DESC

create_or_update_climate(suburb_id, climate_data) -> ClimateData
  - Upserts based on (suburb_id, recorded_date)
  - Uses merge() or update/insert pattern

get_api_cache(api_name) -> APICache?

update_api_cache(api_name, status, error?, response_time_ms?, records_updated?) -> APICache
```

## Configuration (app/core/config.py)

```python
Settings class:
  API_V1_STR = "/api/v1"
  PROJECT_NAME = "Plantopia Recommendation Engine API"
  VERSION = "1.0.0"

  BACKEND_CORS_ORIGINS = [
    "https://plantopia-frontend-theta.vercel.app",
    "https://plantopia-frontend-*.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080"
  ]

  BASE_DIR = Path(__file__).parent.parent.parent
  DATA_DIR = BASE_DIR / "data"

  CSV_PATHS = {
    "flower": "data/csv/flower_plants_data.csv",
    "herb": "data/csv/herbs_plants_data.csv",
    "vegetable": "data/csv/vegetable_plants_data.csv"
  }

  IMAGE_DIRS = {flower/herb/vegetable directories} # Not used, images on GCS

  DEFAULT_SUBURB = "Richmond"
  DEFAULT_RECOMMENDATIONS = 5
  DEFAULT_MAX_PER_CATEGORY = 2

  # Environment Variables (from .env)
  DATABASE_URL: str
  SUPABASE_URL: str
  SUPABASE_ANON_KEY: str
  SUPABASE_SERVICE_KEY: str
  WAQI_API_TOKEN: str
  OPEN_METEO_API_KEY: str
  EPA_VIC_API_KEY: str
  GCS_BUCKET_URL: str (default: gs://plantopia-images-1757656642/plant_images)
  ENVIRONMENT: str (development/production)
  DEBUG: bool

settings = Settings() # Singleton
```

## CORS Middleware (app/main.py)

```python
Smart CORS with dynamic origin checking:
  - OPTIONS preflight: Returns specific origin (not wildcard)
  - Actual requests: Adds CORS headers if origin in allowed list
  - Headers: Access-Control-Allow-Origin (specific origin), -Allow-Credentials: true,
             -Allow-Methods: GET/POST/PUT/DELETE/OPTIONS/PATCH,
             -Allow-Headers: Content-Type/Authorization/X-Requested-With
  - Max-Age: 86400 (24 hours)
```

## Data Files

### CSV Structure
```
data/csv/
├── flower_plants_data.csv (25 columns, 800+ rows)
├── herbs_plants_data.csv (25 columns, 200+ rows)
└── vegetable_plants_data.csv (25 columns, 1100+ rows)

Columns:
  plant_name, scientific_name, plant_category, plant_type, days_to_maturity,
  plant_spacing, sowing_depth, position, season, germination, sowing_method,
  hardiness_life_cycle, characteristics, description, additional_information,
  seed_type, image_filename, cool_climate_sowing_period, temperate_climate_sowing_period,
  subtropical_climate_sowing_period, tropical_climate_sowing_period, arid_climate_sowing_period,
  beneficial_companions, harmful_companions, neutral_companions
```

### JSON Structure
```
data/json/
└── climate_data.json # Legacy, now using ClimateData table

Structure: {
  "suburb_name": {
    "temperature": float,
    "humidity": int,
    "rainfall": float,
    "uv_index": float,
    "air_quality": int,
    "environment": {climate_zone, month_now, etc}
  }
}
```

### Markdown Files
```
data/MARKDOWN_FILES/
├── Beneficial Insects/ (6 files)
├── Companion Planting/ (4 files)
├── Composting/ (8 files)
├── Craft/ (8 files)
├── Fertiliser Soil/ (22 files)
├── flowers/ (36 files)
├── grow_guide/ (255 files)
├── herbs/ (12 files)
├── informational/ (69 files)
└── pests-diseases/ (45 files)

Total: 465+ markdown files
```

### UHI Data
```
app/static/uhi/
├── melbourne_heat_data.json
├── heat_category_summary.csv
└── melbourne_heat_chart_data.csv

GCS Files:
- melbourne_suburbs_simplified.geojson (726KB)
- melbourne_suburb_boundaries_with_heat.geojson (8.8MB)

melbourne_heat_data.json structure: {
  metadata: {dataset, source, date},
  statistics: {min_heat, max_heat, avg_heat},
  heat_categories: {Low Heat, Moderate Heat, High Heat, Extreme Heat: {color, range}},
  suburbs: [{id, name, heat: {intensity, category}, vegetation_pct, postcode}]
}
```

## Utilities

### Image Utils (app/utils/image_utils.py)
```python
image_to_base64(image_path) -> str
  - Reads image file from local path
  - Encodes to base64 string
  - Returns data URI: "data:image/{ext};base64,{data}"
  - Returns "" if file not found
```

## External API Integrations

### Open-Meteo (app/services/apis/open_meteo.py)
```python
Endpoint: https://api.open-meteo.com/v1/forecast
Params: latitude, longitude, current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m,weather_code
Returns: {current: {temperature, humidity, rain, wind_speed, weather_code}}
```

### ARPANSA (app/services/apis/arpansa.py)
```python
Endpoint: https://uvdata.arpansa.gov.au/xml/uvvalues.xml
Parses XML for location_id matching suburb
Returns: {uv_index, uv_category, uv_protection_required}
```

### WAQI (app/services/apis/waqi.py)
```python
Endpoint: https://api.waqi.info/feed/{city}/?token={WAQI_API_TOKEN}
Returns: {aqi, pm25, pm10, o3, no2, so2, co}
Falls back to EPA VIC if WAQI fails
```

## Deployment Considerations

### Environment Variables Required
```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
GCS_BUCKET_URL=https://storage.googleapis.com/...
WAQI_API_TOKEN=... (optional)
OPEN_METEO_API_KEY=... (optional, public API)
EPA_VIC_API_KEY=... (optional)
ENVIRONMENT=production
DEBUG=false
```

### Database Migrations
```
Manual: Run init_db() on startup (creates tables if not exist)
For production: Use alembic for schema migrations
```

### Async Considerations
- All endpoints use async/await
- Database operations use AsyncSession
- Background tasks for climate updates (FastAPI BackgroundTasks)
- Pool size: 3 connections, max_overflow: 5

### Performance Notes
- Plant pagination essential (2117 total plants)
- Climate data: One record per suburb per day (unique constraint)
- GCS image URLs generated on-demand (no DB storage of URLs)
- Recommendation engine: In-memory pandas operations (temp file for user prefs)
- No caching layer (implement Redis for production)

### File Paths
- CSV files: Relative to BASE_DIR/data/csv
- Markdown: Relative to BASE_DIR/data/MARKDOWN_FILES
- UHI static: Relative to BASE_DIR/app/static/uhi
- All paths use Path objects for cross-platform compatibility

## Request/Response Flow Examples

### Recommendation Request Flow
```
1. POST /api/v1/recommendations
2. RecommendationService.generate_recommendations()
3. Create temp JSON file with user_preferences
4. DatabasePlantRepository.get_all_plants() # Load 2117 plants
5. ClimateRepository.get_latest_climate_by_suburb()
6. Recommendation pipeline:
   - select_environment() -> env object
   - get_user_preferences(temp_file) -> user_prefs
   - hard_filter(plants, user_prefs, env) -> eligible
   - relax_if_needed() -> candidates
   - score_and_rank() -> scored (with weights)
   - category_diversity() -> diverse (max 2 per category)
   - top N plants
   - assemble_output() -> structured response
7. Enhance with GCS image URLs
8. Delete temp file
9. Return RecommendationResponse
```

### Quantification Request Flow
```
1. POST /api/v1/quantify-plant
2. DatabasePlantRepository.get_plant_object_by_name() # ORM object
3. ClimateRepository.get_suburb_by_name()
4. QuantificationService.quantify_plant_impact():
   - _normalize_context() # site/suburb/preferences -> factors
   - _derive_plant_biophysics() # estimate LAI, canopy, transpiration
   - _calculate_impact_indices() # raw metrics calculation
   - _calculate_suitability_score() # score vs user prefs
   - _convert_to_user_impact() # format for display
   - _calculate_community_impact() # project to community scale
5. Return PlantQuantificationResponse
```

### Plant Pagination Flow
```
1. GET /api/v1/plants/paginated?page=2&limit=12&category=herb&search=basil
2. PlantService.get_plants_paginated()
3. DatabasePlantRepository.get_plants_paginated():
   - Build query with filters (category, search)
   - Get total count
   - Apply offset=(page-1)*limit, limit
   - Execute query
4. PlantService adds GCS image URLs to each plant
5. Calculate metadata: total_pages=ceil(total/limit), has_next, has_previous
6. Return PaginatedPlantsResponse
```

## Critical Code Patterns

### Dependency Injection
```python
# Standard pattern in all endpoints
async def get_repository(db: AsyncSession = Depends(get_async_db)) -> Repo:
    return Repo(db)

async def get_service(repo: Repo = Depends(get_repository)) -> Service:
    return Service(repo)

@router.get("/endpoint")
async def handler(service: Service = Depends(get_service)):
    return await service.method()
```

### Error Handling
```python
try:
    result = await service.operation()
    return result
except HTTPException:
    raise # Re-raise FastAPI exceptions
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    print(f"Error: {str(e)}")
    print(f"Traceback: {traceback.format_exc()}")
    raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### Repository Pattern
```python
# All DB operations in repositories
class Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Model]:
        result = await self.db.execute(select(Model))
        return result.scalars().all()

    async def find_by_name(self, name: str) -> Optional[Model]:
        query = select(Model).where(func.lower(Model.name) == name.lower())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
```

### Service Pattern
```python
# Business logic in services
class Service:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def operation(self, params) -> Response:
        # Fetch data from repository
        data = await self.repository.get_data(params)
        # Apply business logic
        processed = self._process(data)
        # Return formatted response
        return Response(**processed)
```

## Testing Endpoints (cURL)

```bash
# Health
curl http://localhost:8000/api/v1/

# Get plants paginated
curl "http://localhost:8000/api/v1/plants/paginated?page=1&limit=5&category=herb"

# Get companion data
curl http://localhost:8000/api/v1/plants/1/companions

# Get recommendations
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{"suburb":"Richmond","n":5,"user_preferences":{...}}'

# Quantify plant
curl -X POST http://localhost:8000/api/v1/quantify-plant \
  -H "Content-Type: application/json" \
  -d '{"plant_name":"Basil","suburb":"Richmond","plant_count":5,"user_preferences":{...}}'

# Get climate data
curl http://localhost:8000/api/v1/climate/Richmond

# Get UHI boundaries
curl "http://localhost:8000/api/v1/uhi/boundaries?simplified=true"

# Get markdown categories
curl http://localhost:8000/api/v1/markdown/categories

# Get specific markdown category
curl http://localhost:8000/api/v1/markdown/herbs
```

## Key Algorithms

### Companion String Parsing
```python
def parse_companions(companion_str: Optional[str]) -> List[str]:
    if not companion_str or companion_str.strip() == '':
        return []
    return [c.strip() for c in companion_str.split(',') if c.strip()]
```

### GCS URL Generation
```python
def generate_gcs_image_urls(plant_name, category, scientific_name):
    # Remove special chars: ' ( ) , . / : &
    cleaned_name = re.sub(r"['(),./:]&", "", plant_name).strip()
    cleaned_sci = re.sub(r"['(),./:]&", "", scientific_name or "unknown").strip()

    folder = f"{category}_plant_images"
    folder_name = f"{cleaned_name}_{cleaned_sci}" if cleaned_sci != "unknown" else f"{cleaned_name}_unknown"

    base_url = f"{GCS_BUCKET_URL}/{folder}/{folder_name}"
    return [f"{base_url}/{folder_name}_{i}.jpg" for i in range(1, 5)]
```

### Diversity Capping (Two-Pass)
```python
def category_diversity(scored_plants, max_per_cat, target_count):
    # Pass 1: Cap at max_per_cat
    category_counts = {}
    capped = []
    for item in scored_plants:
        cat = item[1]['plant_category']
        if category_counts.get(cat, 0) < max_per_cat:
            capped.append(item)
            category_counts[cat] = category_counts.get(cat, 0) + 1

    # Pass 2: Fill to target_count if needed
    if len(capped) < target_count:
        for item in scored_plants:
            if item not in capped:
                capped.append(item)
                if len(capped) >= target_count:
                    break

    return capped[:target_count]
```

## Important Constants

```python
# Recommendation weights
GOAL_MATCH_WEIGHT = 0.25
SUN_MATCH_WEIGHT = 0.20
TIME_TO_RESULTS_WEIGHT = 0.15
MAINTENANCE_MATCH_WEIGHT = 0.15
CONTAINER_SUITABILITY_WEIGHT = 0.10
FRAGRANCE_BONUS_WEIGHT = 0.05
COLOR_MATCH_WEIGHT = 0.05
SEASON_TIMELINESS_WEIGHT = 0.05

# Quantification constants
LAI_MEAN = 2.5
LAI_STD = 0.8
CANOPY_MEAN = 0.8
CANOPY_STD = 0.4

# Time to results thresholds (days)
QUICK_THRESHOLD = 75
PATIENT_THRESHOLD = 120

# Default values
DEFAULT_SUBURB = "Richmond"
DEFAULT_CLIMATE_ZONE = "cool" # Melbourne VIC
DEFAULT_RECOMMENDATIONS = 5
DEFAULT_MAX_PER_CATEGORY = 2
```

## Database Indexes
```sql
-- Plants table
CREATE INDEX idx_plant_category_name ON plants(plant_category, plant_name);

-- Suburbs table
CREATE UNIQUE INDEX ON suburbs(name);

-- ClimateData table
CREATE UNIQUE INDEX ON climate_data(suburb_id, recorded_date);
CREATE INDEX idx_climate_suburb_date ON climate_data(suburb_id, recorded_date);

-- UserRecommendations table
CREATE INDEX idx_recommendations_created ON user_recommendations(created_at);
```

## Critical Notes for LLM

1. Plant data source: 3 CSV files (2117 total plants), loaded into PostgreSQL
2. Companion data: Comma-separated strings in DB, parsed to arrays in /companions endpoint
3. Images: GCS URLs generated on-demand, no DB storage
4. Recommendation engine: Temp file pattern for user prefs, pandas-based filtering/scoring
5. Climate data: One record per suburb per day, upsert pattern
6. Async everywhere: All DB ops use AsyncSession
7. Repository pattern: Data access separated from business logic
8. Service pattern: Business logic separated from API handlers
9. Dependency injection: Standard FastAPI pattern throughout
10. GCS URL cleaning: Remove special chars: ' ( ) , . / : &
11. Pagination required: 2117 plants, default limit=12
12. Two-pass diversity: Ensures target count while capping categories
13. Quantification framework: Biophysics-based impact estimation
14. UHI data: Static files in app/static/uhi, GCS for GeoJSON
15. Markdown content: 465+ files in 10 categories
16. Default climate zone: "cool" for Melbourne VIC
17. CORS: Dynamic origin matching from allowed list
18. Admin endpoints: No auth in development, x-api-key in production
19. Background tasks: Climate updates use FastAPI BackgroundTasks
20. Error handling: Catch all, log, return 500 with detail
