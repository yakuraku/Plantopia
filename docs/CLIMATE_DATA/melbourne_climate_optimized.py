#!/usr/bin/env python3
"""
Optimized Melbourne Climate Data Integration
Uses best data source for each parameter
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional

from uv_index_client import ARPANSAUVClient
from open_meteo_client import OpenMeteoClient
from waqi_client import WAQIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedClimateIntegration:
    """Optimized integration using best source for each data type"""
    
    def __init__(self, waqi_token: str):
        """
        Initialize the optimized climate integration
        
        Args:
            waqi_token: WAQI API token for air quality
        """
        # Best source for each data type
        self.uv_client = ARPANSAUVClient()          # Best for UV
        self.weather_client = OpenMeteoClient()      # Best for weather
        self.air_quality_client = WAQIClient(waqi_token)  # Best for air quality
        
    def get_optimized_climate_data(self, suburb_name: str, lat: float, lon: float) -> Dict:
        """
        Get climate data using the best source for each parameter
        
        Args:
            suburb_name: Name of the suburb
            lat: Latitude
            lon: Longitude
            
        Returns:
            Optimized climate data dictionary
        """
        climate_data = {
            "suburb": suburb_name,
            "timestamp": datetime.now().isoformat(),
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "data_sources": {
                "weather": "Open-Meteo (primary)",
                "air_quality": "WAQI (primary)",
                "uv_index": "ARPANSA (primary)"
            }
        }
        
        # 1. UV Index from ARPANSA (best source)
        try:
            self.uv_client.fetch_current_uv()
            uv_data = self.uv_client.get_melbourne_uv()
            if uv_data:
                climate_data["uv_index"] = {
                    "value": uv_data.get("uv_index"),
                    "category": uv_data.get("category"),
                    "protection_required": uv_data.get("protection_required")
                }
        except Exception as e:
            logger.error(f"Error fetching UV: {e}")
        
        # 2. Weather from Open-Meteo (best source)
        try:
            weather = self.weather_client.get_weather_data(lat, lon, suburb_name)
            if weather and weather.get("weather"):
                climate_data["weather"] = {
                    "temperature": weather["weather"].get("temperature"),
                    "apparent_temperature": weather["weather"].get("apparent_temperature"),
                    "humidity": weather["weather"].get("humidity"),
                    "pressure": weather["weather"].get("pressure"),
                    "wind_speed": weather["weather"].get("wind_speed"),
                    "wind_direction": weather["weather"].get("wind_direction"),
                    "cloud_cover": weather["weather"].get("cloud_cover"),
                    "precipitation": weather["weather"].get("precipitation")
                }
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
        
        # 3. Air Quality from WAQI (best source, exclude weather data)
        try:
            air_quality = self.air_quality_client.get_geo_data(lat, lon)
            if air_quality:
                # Extract ONLY air quality metrics, not weather
                climate_data["air_quality"] = {
                    "aqi": air_quality.get("aqi"),
                    "category": air_quality.get("aqi_category"),
                    "dominant_pollutant": air_quality.get("dominant_pollutant"),
                    "station": air_quality.get("station"),
                    "pollutants": {
                        "pm25": air_quality.get("pollutants", {}).get("pm25"),
                        "pm10": air_quality.get("pollutants", {}).get("pm10"),
                        "o3": air_quality.get("pollutants", {}).get("o3"),
                        "no2": air_quality.get("pollutants", {}).get("no2"),
                        "so2": air_quality.get("pollutants", {}).get("so2"),
                        "co": air_quality.get("pollutants", {}).get("co")
                    }
                }
                # Remove None values from pollutants
                climate_data["air_quality"]["pollutants"] = {
                    k: v for k, v in climate_data["air_quality"]["pollutants"].items() 
                    if v is not None
                }
        except Exception as e:
            logger.error(f"Error fetching air quality: {e}")
        
        return climate_data
    
    def generate_summary(self, data: Dict) -> None:
        """
        Generate a human-readable summary of the climate data
        
        Args:
            data: Climate data dictionary
        """
        print(f"\n{'='*60}")
        print(f"Climate Report: {data.get('suburb', 'Unknown')}")
        print(f"{'='*60}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Weather summary
        weather = data.get("weather", {})
        if weather:
            print(f"\n📊 Weather (Open-Meteo):")
            print(f"  Temperature: {weather.get('temperature', 'N/A')}°C")
            print(f"  Feels like: {weather.get('apparent_temperature', 'N/A')}°C")
            print(f"  Humidity: {weather.get('humidity', 'N/A')}%")
            print(f"  Wind: {weather.get('wind_speed', 'N/A')} km/h")
            print(f"  Pressure: {weather.get('pressure', 'N/A')} hPa")
        
        # Air Quality summary
        air_quality = data.get("air_quality", {})
        if air_quality:
            print(f"\n💨 Air Quality (WAQI):")
            aqi = air_quality.get("aqi")
            print(f"  AQI: {aqi} ({air_quality.get('category', 'Unknown')})")
            print(f"  Main Pollutant: {air_quality.get('dominant_pollutant', 'N/A')}")
            
            if aqi and aqi <= 50:
                print("  ✅ Good air quality - enjoy outdoor activities!")
            elif aqi and aqi <= 100:
                print("  ⚠️ Moderate - sensitive individuals should limit prolonged outdoor exertion")
            elif aqi:
                print("  ⚠️ Poor air quality - consider limiting outdoor activities")
        
        # UV Index summary
        uv = data.get("uv_index", {})
        if uv:
            print(f"\n☀️ UV Index (ARPANSA):")
            print(f"  UV Index: {uv.get('value', 'N/A')} ({uv.get('category', 'Unknown')})")
            if uv.get("protection_required"):
                print("  ⚠️ Sun protection required!")
        
        print(f"\n{'='*60}")
    
    def process_suburbs(self, suburbs: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Process multiple suburbs with optimized data collection
        
        Args:
            suburbs: Dictionary of suburb names and coordinates
            
        Returns:
            Climate data for all suburbs
        """
        import time
        all_data = {}
        total = len(suburbs)
        
        for i, (suburb_name, coords) in enumerate(suburbs.items(), 1):
            print(f"[{i}/{total}] Processing {suburb_name}...")
            data = self.get_optimized_climate_data(
                suburb_name,
                coords["lat"],
                coords["lon"]
            )
            all_data[suburb_name] = data
            
            # Quick summary
            temp = data.get("weather", {}).get("temperature", "N/A")
            aqi = data.get("air_quality", {}).get("aqi", "N/A")
            uv = data.get("uv_index", {}).get("value", "N/A")
            print(f"  ✓ {suburb_name}: {temp}°C, AQI {aqi}, UV {uv}")
            
            # Rate limiting - small delay to avoid overwhelming APIs
            if i < total:
                time.sleep(0.2)  # 200ms delay between requests
        
        return all_data


def get_all_melbourne_suburbs():
    """Get comprehensive list of Melbourne suburbs with coordinates"""
    return {
        # Central Melbourne
        "Melbourne CBD": {"lat": -37.8136, "lon": 144.9631},
        "Carlton": {"lat": -37.8001, "lon": 144.9674},
        "Docklands": {"lat": -37.8147, "lon": 144.9394},
        "East Melbourne": {"lat": -37.8163, "lon": 144.9873},
        "North Melbourne": {"lat": -37.7964, "lon": 144.9427},
        "Parkville": {"lat": -37.7860, "lon": 144.9515},
        "Southbank": {"lat": -37.8265, "lon": 144.9595},
        "South Wharf": {"lat": -37.8265, "lon": 144.9526},
        "West Melbourne": {"lat": -37.8069, "lon": 144.9412},
        
        # Inner North
        "Brunswick": {"lat": -37.7666, "lon": 144.9596},
        "Brunswick East": {"lat": -37.7691, "lon": 144.9719},
        "Brunswick West": {"lat": -37.7628, "lon": 144.9437},
        "Carlton North": {"lat": -37.7842, "lon": 144.9686},
        "Clifton Hill": {"lat": -37.7880, "lon": 144.9953},
        "Collingwood": {"lat": -37.8020, "lon": 144.9838},
        "Fitzroy": {"lat": -37.7983, "lon": 144.9780},
        "Fitzroy North": {"lat": -37.7818, "lon": 144.9890},
        "Northcote": {"lat": -37.7703, "lon": 145.0032},
        "Princes Hill": {"lat": -37.7822, "lon": 144.9610},
        "Thornbury": {"lat": -37.7575, "lon": 145.0066},
        
        # Inner East
        "Abbotsford": {"lat": -37.8030, "lon": 144.9958},
        "Burnley": {"lat": -37.8272, "lon": 145.0074},
        "Cremorne": {"lat": -37.8287, "lon": 144.9936},
        "Hawthorn": {"lat": -37.8221, "lon": 145.0232},
        "Hawthorn East": {"lat": -37.8350, "lon": 145.0451},
        "Kew": {"lat": -37.8057, "lon": 145.0310},
        "Kew East": {"lat": -37.7960, "lon": 145.0511},
        "Richmond": {"lat": -37.8230, "lon": 144.9980},
        
        # Inner South
        "Albert Park": {"lat": -37.8416, "lon": 144.9526},
        "Balaclava": {"lat": -37.8677, "lon": 144.9947},
        "Elwood": {"lat": -37.8820, "lon": 144.9844},
        "Middle Park": {"lat": -37.8480, "lon": 144.9609},
        "Port Melbourne": {"lat": -37.8428, "lon": 144.9285},
        "Prahran": {"lat": -37.8505, "lon": 144.9929},
        "St Kilda": {"lat": -37.8678, "lon": 144.9740},
        "St Kilda East": {"lat": -37.8634, "lon": 145.0016},
        "St Kilda West": {"lat": -37.8567, "lon": 144.9737},
        "South Melbourne": {"lat": -37.8340, "lon": 144.9584},
        "South Yarra": {"lat": -37.8396, "lon": 144.9926},
        "Toorak": {"lat": -37.8401, "lon": 145.0092},
        "Windsor": {"lat": -37.8553, "lon": 144.9931},
        
        # Inner West
        "Flemington": {"lat": -37.7880, "lon": 144.9308},
        "Footscray": {"lat": -37.8016, "lon": 144.8995},
        "Kensington": {"lat": -37.7937, "lon": 144.9267},
        "Maribyrnong": {"lat": -37.7736, "lon": 144.8832},
        "Seddon": {"lat": -37.8067, "lon": 144.8906},
        "West Footscray": {"lat": -37.7991, "lon": 144.8741},
        "Yarraville": {"lat": -37.8156, "lon": 144.8896},
        
        # Northern Suburbs
        "Ascot Vale": {"lat": -37.7740, "lon": 144.9206},
        "Broadmeadows": {"lat": -37.6831, "lon": 144.9181},
        "Bundoora": {"lat": -37.7163, "lon": 145.0450},
        "Coburg": {"lat": -37.7454, "lon": 144.9640},
        "Craigieburn": {"lat": -37.6030, "lon": 144.9391},
        "Essendon": {"lat": -37.7527, "lon": 144.9188},
        "Fawkner": {"lat": -37.7076, "lon": 144.9608},
        "Glenroy": {"lat": -37.7031, "lon": 144.9294},
        "Heidelberg": {"lat": -37.7572, "lon": 145.0612},
        "Ivanhoe": {"lat": -37.7687, "lon": 145.0444},
        "Lalor": {"lat": -37.6665, "lon": 145.0173},
        "Mill Park": {"lat": -37.6641, "lon": 145.0619},
        "Moonee Ponds": {"lat": -37.7654, "lon": 144.9191},
        "Pascoe Vale": {"lat": -37.7313, "lon": 144.9397},
        "Preston": {"lat": -37.7415, "lon": 144.9949},
        "Reservoir": {"lat": -37.7200, "lon": 145.0070},
        "Thomastown": {"lat": -37.6810, "lon": 145.0141},
        
        # Eastern Suburbs
        "Balwyn": {"lat": -37.8089, "lon": 145.0805},
        "Balwyn North": {"lat": -37.7912, "lon": 145.0935},
        "Blackburn": {"lat": -37.8190, "lon": 145.1506},
        "Box Hill": {"lat": -37.8193, "lon": 145.1218},
        "Box Hill North": {"lat": -37.8071, "lon": 145.1286},
        "Box Hill South": {"lat": -37.8337, "lon": 145.1249},
        "Bulleen": {"lat": -37.7691, "lon": 145.0887},
        "Burwood": {"lat": -37.8513, "lon": 145.1150},
        "Burwood East": {"lat": -37.8516, "lon": 145.1514},
        "Camberwell": {"lat": -37.8421, "lon": 145.0578},
        "Canterbury": {"lat": -37.8244, "lon": 145.0677},
        "Doncaster": {"lat": -37.7861, "lon": 145.1245},
        "Doncaster East": {"lat": -37.7754, "lon": 145.1507},
        "Forest Hill": {"lat": -37.8347, "lon": 145.1670},
        "Glen Iris": {"lat": -37.8608, "lon": 145.0576},
        "Glen Waverley": {"lat": -37.8783, "lon": 145.1648},
        "Mitcham": {"lat": -37.8165, "lon": 145.1928},
        "Mont Albert": {"lat": -37.8199, "lon": 145.1021},
        "Mount Waverley": {"lat": -37.8756, "lon": 145.1274},
        "Nunawading": {"lat": -37.8200, "lon": 145.1770},
        "Ringwood": {"lat": -37.8142, "lon": 145.2295},
        "Ringwood East": {"lat": -37.8098, "lon": 145.2562},
        "Surrey Hills": {"lat": -37.8152, "lon": 145.0980},
        "Vermont": {"lat": -37.8358, "lon": 145.1959},
        "Wantirna": {"lat": -37.8520, "lon": 145.2179},
        
        # South Eastern Suburbs
        "Ashwood": {"lat": -37.8663, "lon": 145.1019},
        "Bentleigh": {"lat": -37.9181, "lon": 145.0360},
        "Bentleigh East": {"lat": -37.9200, "lon": 145.0540},
        "Carnegie": {"lat": -37.8867, "lon": 145.0551},
        "Caulfield": {"lat": -37.8820, "lon": 145.0266},
        "Chadstone": {"lat": -37.8860, "lon": 145.0890},
        "Clayton": {"lat": -37.9248, "lon": 145.1198},
        "Dandenong": {"lat": -37.9874, "lon": 145.2149},
        "Endeavour Hills": {"lat": -37.9764, "lon": 145.2585},
        "Glen Huntly": {"lat": -37.8981, "lon": 145.0421},
        "Hughesdale": {"lat": -37.8959, "lon": 145.0842},
        "Huntingdale": {"lat": -37.9099, "lon": 145.1034},
        "Keysborough": {"lat": -37.9908, "lon": 145.1740},
        "Malvern": {"lat": -37.8635, "lon": 145.0296},
        "Malvern East": {"lat": -37.8768, "lon": 145.0477},
        "Moorabbin": {"lat": -37.9414, "lon": 145.0442},
        "Mulgrave": {"lat": -37.9284, "lon": 145.1712},
        "Noble Park": {"lat": -37.9665, "lon": 145.1744},
        "Oakleigh": {"lat": -37.8997, "lon": 145.0888},
        "Ormond": {"lat": -37.9033, "lon": 145.0400},
        "Springvale": {"lat": -37.9480, "lon": 145.1534},
        "Wheelers Hill": {"lat": -37.9089, "lon": 145.1881},
        
        # Southern Suburbs
        "Beaumaris": {"lat": -37.9881, "lon": 145.0360},
        "Black Rock": {"lat": -37.9736, "lon": 145.0153},
        "Brighton": {"lat": -37.9098, "lon": 145.0000},
        "Brighton East": {"lat": -37.9036, "lon": 145.0232},
        "Cheltenham": {"lat": -37.9667, "lon": 145.0543},
        "Hampton": {"lat": -37.9373, "lon": 145.0104},
        "Highett": {"lat": -37.9491, "lon": 145.0415},
        "Mentone": {"lat": -37.9832, "lon": 145.0665},
        "Mordialloc": {"lat": -38.0064, "lon": 145.0865},
        "Parkdale": {"lat": -37.9926, "lon": 145.0781},
        "Sandringham": {"lat": -37.9536, "lon": 145.0104},
        
        # Bayside & Peninsula (closer suburbs)
        "Aspendale": {"lat": -38.0273, "lon": 145.1029},
        "Bonbeach": {"lat": -38.0628, "lon": 145.1204},
        "Carrum": {"lat": -38.0747, "lon": 145.1223},
        "Chelsea": {"lat": -38.0519, "lon": 145.1158},
        "Edithvale": {"lat": -38.0378, "lon": 145.1078},
        "Frankston": {"lat": -38.1413, "lon": 145.1226},
        "Patterson Lakes": {"lat": -38.0746, "lon": 145.1405},
        "Seaford": {"lat": -38.1041, "lon": 145.1293},
        
        # Western Suburbs
        "Altona": {"lat": -37.8681, "lon": 144.8301},
        "Altona Meadows": {"lat": -37.8811, "lon": 144.7777},
        "Altona North": {"lat": -37.8495, "lon": 144.8514},
        "Ardeer": {"lat": -37.7821, "lon": 144.8183},
        "Braybrook": {"lat": -37.7819, "lon": 144.8605},
        "Brooklyn": {"lat": -37.8160, "lon": 144.8500},
        "Deer Park": {"lat": -37.7708, "lon": 144.7747},
        "Hoppers Crossing": {"lat": -37.8827, "lon": 144.7005},
        "Laverton": {"lat": -37.8628, "lon": 144.7583},
        "Maidstone": {"lat": -37.7822, "lon": 144.8739},
        "Newport": {"lat": -37.8425, "lon": 144.8834},
        "Point Cook": {"lat": -37.9106, "lon": 144.7532},
        "Spotswood": {"lat": -37.8313, "lon": 144.8857},
        "Sunshine": {"lat": -37.7881, "lon": 144.8324},
        "Sydenham": {"lat": -37.7010, "lon": 144.7658},
        "Tarneit": {"lat": -37.8355, "lon": 144.6579},
        "Truganina": {"lat": -37.8101, "lon": 144.7506},
        "Werribee": {"lat": -37.8999, "lon": 144.6596},
        "Williamstown": {"lat": -37.8585, "lon": 144.8947},
        "Wyndham Vale": {"lat": -37.8915, "lon": 144.6237}
    }


def main():
    """Demonstrate optimized climate data integration"""
    
    print("Optimized Melbourne Climate Data Integration")
    print("Using best data source for each parameter")
    print("="*60)
    
    # Your WAQI token
    WAQI_TOKEN = "8f165ed38392c6e9659cc35b122eedd534fde40d"
    
    # Initialize optimized integration
    integration = OptimizedClimateIntegration(waqi_token=WAQI_TOKEN)
    
    # Get all Melbourne suburbs
    all_suburbs = get_all_melbourne_suburbs()
    print(f"\nTotal suburbs available: {len(all_suburbs)}")
    
    # Option to process all or subset
    process_all = False  # Set to True to process all 150+ suburbs
    
    if process_all:
        suburbs_to_process = all_suburbs
        print(f"Processing ALL {len(suburbs_to_process)} suburbs...")
    else:
        # Process a representative sample across Melbourne
        sample_suburbs = {
            # Central
            "Melbourne CBD": all_suburbs["Melbourne CBD"],
            "Carlton": all_suburbs["Carlton"],
            # North
            "Brunswick": all_suburbs["Brunswick"],
            "Preston": all_suburbs["Preston"],
            "Craigieburn": all_suburbs["Craigieburn"],
            # East
            "Box Hill": all_suburbs["Box Hill"],
            "Ringwood": all_suburbs["Ringwood"],
            "Glen Waverley": all_suburbs["Glen Waverley"],
            # South
            "St Kilda": all_suburbs["St Kilda"],
            "Brighton": all_suburbs["Brighton"],
            "Frankston": all_suburbs["Frankston"],
            # West
            "Footscray": all_suburbs["Footscray"],
            "Sunshine": all_suburbs["Sunshine"],
            "Werribee": all_suburbs["Werribee"],
            # Southeast
            "Dandenong": all_suburbs["Dandenong"],
            "Clayton": all_suburbs["Clayton"],
        }
        suburbs_to_process = sample_suburbs
        print(f"Processing sample of {len(suburbs_to_process)} suburbs...")
        print("(Set process_all=True in script to process all suburbs)")
    
    print("\nProcessing suburbs with optimized data sources:")
    print("-"*60)
    all_data = integration.process_suburbs(suburbs_to_process)
    
    # Show detailed report for CBD
    print("\nDetailed Report:")
    if "Melbourne CBD" in all_data:
        integration.generate_summary(all_data["Melbourne CBD"])
    
    # Save optimized data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"melbourne_climate_optimized_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n✓ Optimized data saved to: {filename}")
    
    print("\n" + "="*60)
    print("Data Source Selection:")
    print("  • Weather (temp, humidity, wind, pressure) → Open-Meteo")
    print("  • Air Quality (AQI, pollutants) → WAQI")  
    print("  • UV Index → ARPANSA")
    print("\nThis ensures maximum accuracy for each parameter!")


if __name__ == "__main__":
    main()