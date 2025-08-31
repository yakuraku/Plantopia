# Plantopia Recommendation Engine

The Plantopia Recommendation Engine provides personalized plant recommendations based on user preferences and environmental data.

## Features

- Personalized plant recommendations based on location and preferences
- Support for flowers, herbs, and vegetables
- Seasonal planting advice
- Detailed care instructions
- API for frontend integration

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Unix or MacOS
# .venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
python main.py --suburb "Richmond" --n 5 --climate climate_data.json --prefs user_preferences.json --out recommendations.json --pretty
```

### API Server

To start the API server:

```bash
uvicorn api:app --reload
```

Or alternatively:

```bash
python api.py
```

The API will be available at `http://localhost:8000`.

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

- `GET /` - Health check endpoint
- `POST /recommendations` - Generate plant recommendations

## Project Structure

- `main.py` - Command line interface
- `api.py` - FastAPI web server
- `recommender/` - Core recommendation engine
- `flower_plants_data.csv` - Flower data
- `herbs_plants_data.csv` - Herb data
- `vegetable_plants_data.csv` - Vegetable data
- `climate_data.json` - Climate information for Melbourne suburbs
- `user_preferences.json` - Sample user preferences

## Development

See `IMPLEMENTATION_GUIDE.md` for detailed information about the engine and API.