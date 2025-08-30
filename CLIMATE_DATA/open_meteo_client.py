#!/usr/bin/env python3
"""
Open-Meteo Weather API Client for Melbourne
Free alternative to BOM for weather data
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenMeteoClient:
    """Client for accessing Open-Meteo weather data"""
    
    # Major Melbourne suburbs with coordinates
    MELBOURNE_SUBURBS = {
        "Melbourne CBD": {"lat": -37.8136, "lon": 144.9631, "postcode": "3000"},
        "Carlton": {"lat": -37.8001, "lon": 144.9674, "postcode": "3053"},
        "St Kilda": {"lat": -37.8678, "lon": 144.9740, "postcode": "3182"},
        "Richmond": {"lat": -37.8230, "lon": 144.9980, "postcode": "3121"},
        "South Yarra": {"lat": -37.8396, "lon": 144.9926, "postcode": "3141"},
        "Footscray": {"lat": -37.8016, "lon": 144.8995, "postcode": "3011"},
        "Brunswick": {"lat": -37.7666, "lon": 144.9596, "postcode": "3056"},
        "Camberwell": {"lat": -37.8421, "lon": 145.0578, "postcode": "3124"},
        "Brighton": {"lat": -37.9098, "lon": 145.0000, "postcode": "3186"},
        "Box Hill": {"lat": -37.8193, "lon": 145.1218, "postcode": "3128"},
        "Dandenong": {"lat": -37.9874, "lon": 145.2149, "postcode": "3175"},
        "Frankston": {"lat": -38.1413, "lon": 145.1226, "postcode": "3199"},
        "Glen Waverley": {"lat": -37.8783, "lon": 145.1648, "postcode": "3150"},
        "Heidelberg": {"lat": -37.7572, "lon": 145.0612, "postcode": "3084"},
        "Moonee Ponds": {"lat": -37.7654, "lon": 144.9191, "postcode": "3039"},
        "Preston": {"lat": -37.7415, "lon": 144.9949, "postcode": "3072"},
        "Ringwood": {"lat": -37.8142, "lon": 145.2295, "postcode": "3134"},
        "Sunshine": {"lat": -37.7881, "lon": 144.8324, "postcode": "3020"},
        "Werribee": {"lat": -37.8999, "lon": 144.6596, "postcode": "3030"},
        "Williamstown": {"lat": -37.8585, "lon": 144.8947, "postcode": "3016"}
    }
    
    def __init__(self):
        """Initialize the Open-Meteo client"""
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.air_quality_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        
    def get_weather_data(self, lat: float, lon: float, suburb_name: str = "") -> Optional[Dict]:
        """
        Fetch weather data for specific coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            suburb_name: Optional suburb name for reference
            
        Returns:
            Weather data dictionary or None if error
        """
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "rain",
                    "weather_code",
                    "cloud_cover",
                    "pressure_msl",
                    "surface_pressure",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "wind_gusts_10m"
                ],
                "timezone": "Australia/Melbourne"
            }
            
            logger.info(f"Fetching weather for {suburb_name if suburb_name else f'{lat},{lon}'}")
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_weather_data(data, suburb_name)
            else:
                logger.warning(f"Failed to fetch weather: Status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def get_air_quality_data(self, lat: float, lon: float, suburb_name: str = "") -> Optional[Dict]:
        """
        Fetch air quality data for specific coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            suburb_name: Optional suburb name for reference
            
        Returns:
            Air quality data dictionary or None if error
        """
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "pm10",
                    "pm2_5",
                    "carbon_monoxide",
                    "nitrogen_dioxide",
                    "sulphur_dioxide",
                    "ozone",
                    "dust",
                    "uv_index",
                    "uv_index_clear_sky",
                    "aqi"
                ],
                "timezone": "Australia/Melbourne"
            }
            
            logger.info(f"Fetching air quality for {suburb_name if suburb_name else f'{lat},{lon}'}")
            response = requests.get(self.air_quality_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_air_quality_data(data, suburb_name)
            else:
                logger.warning(f"Failed to fetch air quality: Status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching air quality data: {e}")
            return None
    
    def _parse_weather_data(self, data: Dict, suburb_name: str) -> Dict:
        """Parse Open-Meteo weather response"""
        current = data.get("current", {})
        
        return {
            "suburb": suburb_name,
            "timestamp": current.get("time", ""),
            "coordinates": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude")
            },
            "weather": {
                "temperature": current.get("temperature_2m"),
                "apparent_temperature": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m"),
                "precipitation": current.get("precipitation"),
                "rain": current.get("rain"),
                "cloud_cover": current.get("cloud_cover"),
                "pressure": current.get("pressure_msl"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "wind_gusts": current.get("wind_gusts_10m"),
                "weather_code": current.get("weather_code")
            }
        }
    
    def _parse_air_quality_data(self, data: Dict, suburb_name: str) -> Dict:
        """Parse Open-Meteo air quality response"""
        current = data.get("current", {})
        
        return {
            "suburb": suburb_name,
            "timestamp": current.get("time", ""),
            "air_quality": {
                "aqi": current.get("aqi"),
                "pm10": current.get("pm10"),
                "pm2_5": current.get("pm2_5"),
                "carbon_monoxide": current.get("carbon_monoxide"),
                "nitrogen_dioxide": current.get("nitrogen_dioxide"),
                "sulphur_dioxide": current.get("sulphur_dioxide"),
                "ozone": current.get("ozone"),
                "dust": current.get("dust"),
                "uv_index": current.get("uv_index"),
                "uv_index_clear_sky": current.get("uv_index_clear_sky")
            }
        }
    
    def get_all_suburbs_weather(self) -> Dict[str, Dict]:
        """Fetch weather for all configured Melbourne suburbs"""
        all_weather = {}
        
        for suburb_name, coords in self.MELBOURNE_SUBURBS.items():
            weather = self.get_weather_data(coords["lat"], coords["lon"], suburb_name)
            if weather:
                all_weather[suburb_name] = weather
                
        return all_weather
    
    def get_all_suburbs_air_quality(self) -> Dict[str, Dict]:
        """Fetch air quality for all configured Melbourne suburbs"""
        all_air_quality = {}
        
        for suburb_name, coords in self.MELBOURNE_SUBURBS.items():
            air_quality = self.get_air_quality_data(coords["lat"], coords["lon"], suburb_name)
            if air_quality:
                all_air_quality[suburb_name] = air_quality
                
        return all_air_quality
    
    def get_complete_climate_data(self, lat: float, lon: float, suburb_name: str = "") -> Dict:
        """
        Get complete climate data (weather + air quality) for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            suburb_name: Optional suburb name
            
        Returns:
            Combined climate data
        """
        weather = self.get_weather_data(lat, lon, suburb_name)
        air_quality = self.get_air_quality_data(lat, lon, suburb_name)
        
        return {
            "suburb": suburb_name,
            "timestamp": datetime.now().isoformat(),
            "coordinates": {"latitude": lat, "longitude": lon},
            "weather": weather.get("weather") if weather else None,
            "air_quality": air_quality.get("air_quality") if air_quality else None
        }
    
    def display_weather(self, weather_data: Dict) -> None:
        """Display weather data in formatted output"""
        print(f"\n{'='*60}")
        print(f"Weather Report - {weather_data.get('suburb', 'Unknown Location')}")
        print(f"{'='*60}")
        print(f"Time: {weather_data.get('timestamp', 'Unknown')}")
        
        weather = weather_data.get("weather", {})
        print(f"\nTemperature: {weather.get('temperature', 'N/A')}°C")
        print(f"Feels like: {weather.get('apparent_temperature', 'N/A')}°C")
        print(f"Humidity: {weather.get('humidity', 'N/A')}%")
        print(f"Wind: {weather.get('wind_speed', 'N/A')} km/h from {weather.get('wind_direction', 'N/A')}°")
        print(f"Pressure: {weather.get('pressure', 'N/A')} hPa")
        print(f"Cloud cover: {weather.get('cloud_cover', 'N/A')}%")
        print(f"Rain: {weather.get('rain', 0)} mm")
    
    def display_air_quality(self, aq_data: Dict) -> None:
        """Display air quality data in formatted output"""
        print(f"\n{'='*60}")
        print(f"Air Quality Report - {aq_data.get('suburb', 'Unknown Location')}")
        print(f"{'='*60}")
        
        aq = aq_data.get("air_quality", {})
        aqi = aq.get('aqi')
        
        if aqi is not None:
            print(f"\nAir Quality Index (AQI): {aqi}")
            if aqi <= 50:
                print("Category: Good ✓")
            elif aqi <= 100:
                print("Category: Moderate ⚠")
            elif aqi <= 150:
                print("Category: Unhealthy for Sensitive Groups ⚠")
            elif aqi <= 200:
                print("Category: Unhealthy ❌")
            else:
                print("Category: Very Unhealthy ❌")
        
        print(f"\nPM2.5: {aq.get('pm2_5', 'N/A')} μg/m³")
        print(f"PM10: {aq.get('pm10', 'N/A')} μg/m³")
        print(f"Ozone: {aq.get('ozone', 'N/A')} μg/m³")
        print(f"NO₂: {aq.get('nitrogen_dioxide', 'N/A')} μg/m³")
        print(f"UV Index: {aq.get('uv_index', 'N/A')}")


def main():
    """Test Open-Meteo API client"""
    
    print("Open-Meteo Climate Data Client for Melbourne")
    print("Free weather and air quality data - No API key required!")
    print("="*60)
    
    client = OpenMeteoClient()
    
    # Test Melbourne CBD
    print("\nFetching data for Melbourne CBD...")
    cbd_coords = client.MELBOURNE_SUBURBS["Melbourne CBD"]
    
    # Get weather
    weather = client.get_weather_data(cbd_coords["lat"], cbd_coords["lon"], "Melbourne CBD")
    if weather:
        print("✓ Weather data retrieved successfully!")
        client.display_weather(weather)
    
    # Get air quality
    air_quality = client.get_air_quality_data(cbd_coords["lat"], cbd_coords["lon"], "Melbourne CBD")
    if air_quality:
        print("\n✓ Air quality data retrieved successfully!")
        client.display_air_quality(air_quality)
    
    # Save sample data for multiple suburbs
    print("\n\nFetching data for multiple suburbs...")
    sample_suburbs = ["Melbourne CBD", "St Kilda", "Richmond", "Box Hill", "Frankston"]
    
    all_data = {}
    for suburb in sample_suburbs:
        if suburb in client.MELBOURNE_SUBURBS:
            coords = client.MELBOURNE_SUBURBS[suburb]
            data = client.get_complete_climate_data(
                coords["lat"], coords["lon"], suburb
            )
            all_data[suburb] = data
            temp = data['weather']['temperature'] if data['weather'] else 'N/A'
            aqi = 'N/A'
            if data['air_quality'] and data['air_quality'].get('aqi'):
                aqi = data['air_quality']['aqi']
            print(f"✓ {suburb}: Temp {temp}°C, AQI {aqi}")
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"melbourne_climate_data_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n✓ Climate data saved to: {filename}")
    print("\n" + "="*60)
    print("Success! Open-Meteo provides free, reliable climate data.")
    print("No API key required, unlimited requests for non-commercial use.")


if __name__ == "__main__":
    main()