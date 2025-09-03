# Plantopia Recommendation Engine

## General Guidelines
Refer to the PROGRESS.md file for reference of the Project
Refer to other .md files in the directory for additional context on the Project

## Setup

```bash
python -m venv .venv
.venv\\Scripts\\activate  # On Windows
# .venv/bin/activate    # On Unix/macOS
pip install -r requirements.txt
```

## Running the Engine

Basic usage:
```bash
python main.py --suburb "Richmond" --n 5 --climate climate_data.json --prefs user_preferences.json --out recommendations.json --pretty
```

Other examples:
```bash
# Use default fallbacks
python main.py --suburb "Unknown Suburb" --out recommendations.json

# Change number of recommendations
python main.py --suburb "Richmond" --n 3 --out recommendations.json
```

## How It Works

### Data Normalization
The engine reads plant data from three CSV files (flowers, herbs, vegetables) and normalizes the data into a consistent format:
- Cleans text fields by removing markdown markers
- Parses time-to-maturity values
- Extracts sowing months by climate zone
- Derives plant characteristics like sun needs, container suitability, etc.

### Environment Selection
The engine selects environmental data based on:
1. Exact suburb match in climate_data.json
2. Fallback to "Richmond" if available
3. System defaults if neither is available

### Scoring System
Each plant is scored based on multiple factors:
- **Season compatibility** (25% weight): How well the plant's sowing period matches the current month
- **Sun compatibility** (20% weight): Match between plant's sun needs and site conditions
- **Maintainability** (15% weight): How well the plant matches user's maintenance preferences
- **Time to results** (10% weight): How quickly the plant produces results
- **Site fit** (10% weight): Compatibility with containers, space, and location
- **User preferences** (12% weight): Edible/ornamental types, colors, fragrance
- **Wind penalty** (3% weight): Reduction for tall plants in windy conditions
- **Eco bonus** (5% weight): Bonus for pollinator-friendly plants

### Recommendation Process
1. Load and normalize all plant data
2. Select environment based on suburb
3. Apply hard filters (season, goal, site requirements)
4. Relax filters if needed to reach target number of recommendations
5. Score and rank candidates
6. Apply category diversity cap (max 2 per category initially)
7. Generate explanations for top recommendations

### Customization
You can adjust the scoring weights in `recommender/scoring.py`:
```python
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
```

## Scenario Testing (Deterministic & Climate-Aware)

We default Melbourne/VIC to **cool** climate. You can override with `--climate-zone`.

Run the scenario harness:

```powershell
cd D:\\Plantopia_Backend
python tests\\run_scenarios.py
```