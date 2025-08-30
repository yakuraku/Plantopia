# Melbourne Climate Data Integration - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Data Sources](#data-sources)
3. [API Access & Limits](#api-access--limits)
4. [Implementation Guide](#implementation-guide)
5. [File Structure](#file-structure)
6. [Usage Instructions](#usage-instructions)
7. [Data Coverage](#data-coverage)
8. [Troubleshooting](#troubleshooting)
9. [Code Examples](#code-examples)
10. [Future Enhancements](#future-enhancements)

---

## Project Overview

### Purpose
Comprehensive climate data integration system for Melbourne suburbs, collecting real-time weather, air quality, and UV index data for 151+ suburbs across Greater Melbourne.

### Key Features
- **Real-time data** from multiple authoritative sources
- **151 Melbourne suburbs** with GPS coordinates
- **Optimized data collection** using best source for each parameter
- **Free tier APIs** - no cost for reasonable usage
- **JSON output** for easy integration with other systems

### Data Parameters Collected
- Temperature (current and apparent)
- Humidity
- Wind speed and direction
- Atmospheric pressure
- Air Quality Index (AQI)
- Pollutant levels (PM2.5, PM10, O3, NO2, SO2, CO)
- UV Index and sun protection recommendations
- Cloud cover and precipitation

---

## Data Sources

### 1. Open-Meteo (Weather Data)
**Purpose**: Primary source for weather data  
**Website**: https://open-meteo.com/  
**Data Provided**:
- Temperature, humidity, wind, pressure
- Precipitation, cloud cover
- Weather codes

**Advantages**:
- No API key required
- No rate limits
- GPS coordinate-based (any location)
- High accuracy weather models

### 2. WAQI - World Air Quality Index (Air Quality)
**Purpose**: Primary source for air quality data  
**Website**: https://aqicn.org/  
**API Token**: `8f165ed38392c6e9659cc35b122eedd534fde40d`  
**Data Provided**:
- Air Quality Index (AQI)
- PM2.5, PM10, O3, NO2, SO2, CO levels
- Dominant pollutant identification

**Melbourne Monitoring Stations**:
- Melbourne CBD (@8850)
- Footscray (@11388)
- Alphington (@8831)
- Brighton (@8833)
- Box Hill (@8832)
- Dandenong (@8834)
- Melton (@8837)
- Mooroolbark (@12411)
- Point Cook (@10135)

### 3. ARPANSA (UV Index)
**Purpose**: UV radiation monitoring  
**Website**: https://www.arpansa.gov.au/  
**Data Provided**:
- Real-time UV Index
- UV category (Low/Moderate/High/Very High/Extreme)
- Sun protection recommendations

**Advantages**:
- No API key required
- Official Australian government source
- Updates every minute during daylight

### 4. EPA Victoria (Backup - Currently Issues)
**Purpose**: Alternative air quality source  
**Status**: 403 Forbidden errors - subscription issues  
**API Key**: `8963cdcd394644a7a475a8c6c645671e`  
**Fix Required**: 
1. Visit https://portal.api.epa.vic.gov.au
2. Subscribe to "Environment Monitoring" product
3. Contact: contact@epa.vic.gov.au

---

## API Access & Limits

### Summary Table

| Service | Free Tier Limit | Rate Limit | Key Required | Status |
|---------|-----------------|------------|--------------|---------|
| **Open-Meteo** | 10000/day       | None       | No | ✅ Working |
| **WAQI** | Unlimited       | 1000/min   | Yes (have) | ✅ Working |
| **ARPANSA** | Unlimited       | None       | No | ✅ Working |
| **EPA Victoria** | Unknown         | 5/second   | Yes (have) | ❌ 403 Error |

### Detailed Limits

#### Open-Meteo
- **Daily Limit**: 10000/day
- **Rate Limit**: No restrictions
- **Commercial Use**: Free for non-commercial
- **Notes**: Most reliable, no authentication needed

#### WAQI (World Air Quality Index)
- **Daily Limit**: None specified
- **Rate Limit**: 1000 requests/second, 60 per request
- **Token**: Required (free registration)
- **Commercial Use**: Requires permission
- **Our Token**: `8f165ed38392c6e9659cc35b122eedd534fde40d`

#### ARPANSA
- **Daily Limit**: None
- **Rate Limit**: Reasonable use expected
- **Authentication**: None
- **Attribution**: Required ("UV observations courtesy of ARPANSA")

#### Alternative APIs (Not Currently Used)

**OpenWeatherMap Air Pollution**
- Free: 1,000 calls/day
- 60 calls/minute max
- Sign up: https://openweathermap.org/api

---

## Implementation Guide

### Prerequisites
```bash
# Python 3.7+ required
python3 --version

# Install required packages
pip3 install requests
```

### Quick Start

#### 1. Test Individual APIs
```bash
# Test WAQI air quality
python3 waqi_client.py

# Test ARPANSA UV
python3 uv_index_client.py

# Test Open-Meteo weather
python3 open_meteo_client.py
```

#### 2. Run Optimized Integration (Sample)
```bash
# Process 16 representative suburbs
python3 melbourne_climate_optimized.py
```

#### 3. Process All Suburbs
```bash
# Process all 151 suburbs (~40 seconds)
python3 process_all_suburbs.py
```

### Configuration

#### Setting WAQI Token
Edit in files:
- `waqi_client.py` (line 19)
- `melbourne_climate_optimized.py` (line 382)
- `melbourne_climate_integration.py` (line 347)

```python
WAQI_TOKEN = "8f165ed38392c6e9659cc35b122eedd534fde40d"
```

#### Enabling All Suburbs Processing
In `melbourne_climate_optimized.py`:
```python
process_all = True  # Change from False to True
```

---

## File Structure

```
/Users/kevin/dev/projects/FIT5120_Climate/
│
├── Core API Clients
│   ├── waqi_client.py                 # WAQI air quality client
│   ├── uv_index_client.py            # ARPANSA UV client
│   ├── open_meteo_client.py          # Open-Meteo weather client
│   └── epa_api_client.py            # EPA Victoria client (has issues)
│   
│
├── Integration Scripts
│   ├── melbourne_climate_optimized.py     # Main optimized integration
│   ├── melbourne_climate_integration.py   # Original integration
│   └── process_all_suburbs.py            # Process all 151 suburbs
│
├── Documentation
│   ├── PROJECT_DOCUMENTATION.md      # This file
│   ├── INTEGRATION_GUIDE.md         # Integration guide
│   └── AIR_QUALITY_APIS.md          # Air quality API comparison
│
└── Output Files (Generated)
    ├── melbourne_climate_optimized_*.json
    ├── melbourne_climate_full_*.json
    ├── waqi_melbourne_air_quality_*.json
    └── arpansa_uv_data_*.json
```

---

## Usage Instructions

### Basic Usage

#### Get Climate Data for Specific Suburb

```python
from backend.Plantopia.CLIMATE_DATA.melbourne_climate_optimized import OptimizedClimateIntegration

# Initialize
integration = OptimizedClimateIntegration(waqi_token="YOUR_TOKEN")

# Get data for one suburb
data = integration.get_optimized_climate_data(
    "Melbourne CBD",
    -37.8136,
    144.9631
)
```

#### Process Multiple Suburbs
```python
suburbs = {
    "Melbourne CBD": {"lat": -37.8136, "lon": 144.9631},
    "St Kilda": {"lat": -37.8678, "lon": 144.9740}
}

all_data = integration.process_suburbs(suburbs)
```

### Command Line Usage

#### Quick Test
```bash
# Test with 3 suburbs
python3 -c "
from melbourne_climate_optimized import *
client = OptimizedClimateIntegration('8f165ed38392c6e9659cc35b122eedd534fde40d')
data = client.get_optimized_climate_data('Melbourne CBD', -37.8136, 144.9631)
client.generate_summary(data)
"
```

#### Full Processing
```bash
# Process all suburbs and save to JSON
python3 process_all_suburbs.py
```

### Output Format

#### JSON Structure
```json
{
  "Melbourne CBD": {
    "suburb": "Melbourne CBD",
    "timestamp": "2025-08-30T00:00:00",
    "location": {
      "latitude": -37.8136,
      "longitude": 144.9631
    },
    "weather": {
      "temperature": 8.2,
      "humidity": 85,
      "pressure": 998.2,
      "wind_speed": 17.7
    },
    "air_quality": {
      "aqi": 22,
      "category": "Good",
      "pollutants": {
        "pm25": 22,
        "pm10": 11
      }
    },
    "uv_index": {
      "value": 0.0,
      "category": "Low"
    }
  }
}
```

---

## Data Coverage

### Geographic Coverage
- **Total Suburbs**: 151
- **Area Covered**: Greater Melbourne (~9,990 km²)
- **Radius**: ~50km from CBD
- **Population Coverage**: ~5 million people

### Suburbs by Region

| Region | Count | Example Suburbs |
|--------|-------|-----------------|
| Central Melbourne | 9 | CBD, Carlton, Docklands |
| Inner North | 20 | Brunswick, Fitzroy, Northcote |
| Inner East | 8 | Richmond, Hawthorn, Kew |
| Inner South | 13 | St Kilda, Prahran, South Yarra |
| Inner West | 7 | Footscray, Yarraville |
| Northern | 17 | Preston, Bundoora, Craigieburn |
| Eastern | 25 | Box Hill, Ringwood, Glen Waverley |
| South Eastern | 22 | Dandenong, Clayton, Springvale |
| Southern | 11 | Brighton, Frankston, Mentone |
| Western | 19 | Sunshine, Werribee, Point Cook |

### Data Accuracy

#### Temperature
- **Inner suburbs** (< 5km): ±0.5°C
- **Middle suburbs** (5-15km): ±1.0°C
- **Outer suburbs** (> 15km): ±1.5°C

#### Air Quality
- Mapped to nearest monitoring station
- Maximum distance: ~20km
- Updates: Hourly

#### UV Index
- Melbourne-wide reading
- Same value for all suburbs
- Updates: Every minute (daylight hours)

---

## Troubleshooting

### Common Issues

#### 1. 403 Forbidden from EPA
**Problem**: EPA API returns 403  
**Solution**: API subscription issue - contact EPA support

#### 2. WAQI Returns Wrong City
**Problem**: Demo token returns Shanghai data  
**Solution**: Use proper API token (not "demo")

#### 3. Slow Processing
**Problem**: Takes too long for all suburbs  
**Solution**: 
- Process in batches
- Increase rate limit delay
- Use sample suburbs for testing

#### 4. Missing Data Fields
**Problem**: Some fields show "N/A"  
**Solution**: Normal for nighttime (UV) or station outages

### Error Handling

```python
try:
    data = integration.get_optimized_climate_data(suburb, lat, lon)
except Exception as e:
    print(f"Error processing {suburb}: {e}")
    # Use cached data or skip
```

---

## Code Examples

### Example 1: Get Current Temperature for Suburb

```python
from backend.Plantopia.CLIMATE_DATA.melbourne_climate_optimized import OptimizedClimateIntegration

client = OptimizedClimateIntegration(waqi_token="8f165ed38392c6e9659cc35b122eedd534fde40d")
data = client.get_optimized_climate_data("St Kilda", -37.8678, 144.9740)

temperature = data.get("weather", {}).get("temperature", "N/A")
print(f"Current temperature in St Kilda: {temperature}°C")
```

### Example 2: Find Suburbs with Poor Air Quality

```python
from backend.Plantopia.CLIMATE_DATA.melbourne_climate_optimized import OptimizedClimateIntegration,
    get_all_melbourne_suburbs

client = OptimizedClimateIntegration(waqi_token="8f165ed38392c6e9659cc35b122eedd534fde40d")
all_suburbs = get_all_melbourne_suburbs()

poor_air_quality = []
for suburb, coords in all_suburbs.items():
    data = client.get_optimized_climate_data(suburb, coords["lat"], coords["lon"])
    aqi = data.get("air_quality", {}).get("aqi", 0)
    if aqi > 100:  # AQI > 100 is unhealthy
        poor_air_quality.append((suburb, aqi))

for suburb, aqi in poor_air_quality:
    print(f"{suburb}: AQI {aqi}")
```

### Example 3: Export to CSV
```python
import csv
import json

# Load JSON data
with open("melbourne_climate_optimized_20250830_000900.json", "r") as f:
    data = json.load(f)

# Write to CSV
with open("climate_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Suburb", "Temperature", "Humidity", "AQI", "UV Index"])
    
    for suburb, climate in data.items():
        temp = climate.get("weather", {}).get("temperature", "")
        humidity = climate.get("weather", {}).get("humidity", "")
        aqi = climate.get("air_quality", {}).get("aqi", "")
        uv = climate.get("uv_index", {}).get("value", "")
        writer.writerow([suburb, temp, humidity, aqi, uv])
```

---

## Future Enhancements

### Planned Features
1. **Database Integration**
   - SQLite/PostgreSQL storage
   - Historical data tracking
   - Trend analysis

2. **Web API**
   - REST API endpoint
   - Real-time WebSocket updates
   - GraphQL interface

3. **Visualization**
   - Interactive map
   - Charts and graphs
   - Heatmaps for temperature/AQI

4. **Alerts System**
   - High UV warnings
   - Poor air quality alerts
   - Extreme weather notifications

5. **Additional Data Sources**
   - Pollen count (Ambee API)
   - Traffic data
   - Solar radiation

### Performance Improvements
- Parallel API calls
- Redis caching
- CDN for static data
- Webhook updates

### Machine Learning
- Weather prediction
- AQI forecasting
- Pattern recognition
- Anomaly detection

---

## Contact & Support

### API Support
- **WAQI**: https://aqicn.org/contact/
- **ARPANSA**: uv.index@arpansa.gov.au
- **EPA Victoria**: contact@epa.vic.gov.au
- **Open-Meteo**: https://open-meteo.com/en/contact

### Project Information
- **Created**: August 30, 2025
- **Purpose**: FIT5120 Climate Project
- **Location**: Melbourne, Australia

### Data Attribution
When using this data, please include:
- "UV observations courtesy of ARPANSA"
- "Air quality data from World Air Quality Index Project"
- "Weather data from Open-Meteo"

---

## Appendix

### A. Complete Suburb List
All 151 suburbs are defined in `get_all_melbourne_suburbs()` function in `melbourne_climate_optimized.py`

### B. API Response Formats
Detailed API response formats are documented in individual client files

### C. Rate Limiting Strategy
- 200ms delay between requests
- Exponential backoff on errors
- Cache duration: 5 minutes

### D. License
This project uses publicly available APIs. Check individual API terms for commercial use.

---

*Last Updated: August 30, 2025*