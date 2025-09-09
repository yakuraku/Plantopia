#!/usr/bin/env python3
"""
Melbourne Climate Data Integration System
Combines multiple data sources to provide comprehensive climate information
for all Melbourne suburbs
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import time

# Import our custom clients
from uv_index_client import ARPANSAUVClient
from open_meteo_client import OpenMeteoClient
from epa_api_client import EPAVictoriaClient
from waqi_client import WAQIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MelbourneClimateIntegration:
    """Main integration class for Melbourne climate data"""
    
    def __init__(self, epa_api_key: Optional[str] = None, waqi_token: Optional[str] = None):
        """
        Initialize the climate integration system
        
        Args:
            epa_api_key: Optional EPA Victoria API key
            waqi_token: Optional WAQI API token
        """
        # Initialize clients
        self.uv_client = ARPANSAUVClient()
        self.weather_client = OpenMeteoClient()
        self.epa_client = EPAVictoriaClient(epa_api_key) if epa_api_key else None
        self.waqi_client = WAQIClient(waqi_token) if waqi_token else None
        
        # Cache for data
        self.cache = {
            'uv': None,
            'uv_timestamp': None,
            'weather': {},
            'air_quality': {}
        }
        
        # Cache duration in seconds
        self.cache_duration = 300  # 5 minutes
        
    def get_uv_data(self) -> Optional[Dict]:
        """
        Get UV data from ARPANSA (Melbourne-wide)
        
        Returns:
            UV data dictionary or None
        """
        try:
            # Check cache
            if self.cache['uv_timestamp']:
                age = (datetime.now() - self.cache['uv_timestamp']).seconds
                if age < self.cache_duration and self.cache['uv']:
                    logger.info("Using cached UV data")
                    return self.cache['uv']
            
            # Fetch fresh data
            logger.info("Fetching fresh UV data from ARPANSA...")
            self.uv_client.fetch_current_uv()
            melbourne_uv = self.uv_client.get_melbourne_uv()
            
            if melbourne_uv:
                self.cache['uv'] = melbourne_uv
                self.cache['uv_timestamp'] = datetime.now()
                return melbourne_uv
            
        except Exception as e:
            logger.error(f"Error fetching UV data: {e}")
        
        return None
    
    def get_weather_for_location(self, lat: float, lon: float, suburb_name: str = "") -> Optional[Dict]:
        """
        Get weather data for specific location
        
        Args:
            lat: Latitude
            lon: Longitude
            suburb_name: Suburb name for reference
            
        Returns:
            Weather data dictionary or None
        """
        try:
            # Check cache
            cache_key = f"{lat},{lon}"
            if cache_key in self.cache['weather']:
                cached = self.cache['weather'][cache_key]
                age = (datetime.now() - cached['timestamp']).seconds
                if age < self.cache_duration:
                    logger.info(f"Using cached weather data for {suburb_name}")
                    return cached['data']
            
            # Fetch fresh data
            logger.info(f"Fetching weather for {suburb_name}...")
            weather = self.weather_client.get_weather_data(lat, lon, suburb_name)
            
            if weather:
                self.cache['weather'][cache_key] = {
                    'data': weather,
                    'timestamp': datetime.now()
                }
                return weather
                
        except Exception as e:
            logger.error(f"Error fetching weather for {suburb_name}: {e}")
        
        return None
    
    def get_air_quality_for_location(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get air quality data from WAQI or EPA Victoria
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Air quality data or None
        """
        # Try WAQI first (working)
        if self.waqi_client:
            try:
                logger.info(f"Fetching air quality from WAQI...")
                air_data = self.waqi_client.get_geo_data(lat, lon)
                if air_data:
                    return air_data
            except Exception as e:
                logger.error(f"Error fetching WAQI data: {e}")
        
        # Fallback to EPA if available
        if self.epa_client:
            try:
                return self.epa_client.get_latest_measurements()
            except Exception as e:
                logger.error(f"Error fetching EPA data: {e}")
        
        return None
    
    def get_complete_climate_data(self, suburb_name: str, lat: float, lon: float) -> Dict:
        """
        Get all available climate data for a suburb
        
        Args:
            suburb_name: Name of the suburb
            lat: Latitude
            lon: Longitude
            
        Returns:
            Complete climate data dictionary
        """
        climate_data = {
            "suburb": suburb_name,
            "timestamp": datetime.now().isoformat(),
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "data_sources": []
        }
        
        # Get UV data (Melbourne-wide)
        uv_data = self.get_uv_data()
        if uv_data:
            climate_data["uv"] = {
                "index": uv_data.get("uv_index"),
                "category": uv_data.get("category"),
                "protection_required": uv_data.get("protection_required"),
                "time": uv_data.get("time"),
                "source": "ARPANSA"
            }
            climate_data["data_sources"].append("ARPANSA UV")
        
        # Get weather data
        weather = self.get_weather_for_location(lat, lon, suburb_name)
        if weather and weather.get("weather"):
            climate_data["weather"] = weather["weather"]
            climate_data["weather"]["source"] = "Open-Meteo"
            climate_data["data_sources"].append("Open-Meteo Weather")
        
        # Get air quality data (WAQI or EPA)
        air_quality = self.get_air_quality_for_location(lat, lon)
        if air_quality:
            # Check if it's WAQI data (has 'aqi' field) or EPA data
            if 'aqi' in air_quality:
                climate_data["air_quality"] = {
                    "aqi": air_quality.get("aqi"),
                    "category": air_quality.get("aqi_category"),
                    "dominant_pollutant": air_quality.get("dominant_pollutant"),
                    "pollutants": air_quality.get("pollutants", {}),
                    "station": air_quality.get("station"),
                    "source": "WAQI"
                }
                climate_data["data_sources"].append("WAQI Air Quality")
            else:
                climate_data["air_quality"] = air_quality
                climate_data["air_quality"]["source"] = "EPA Victoria"
                climate_data["data_sources"].append("EPA Victoria Air Quality")
        
        return climate_data
    
    def process_all_suburbs(self) -> Dict[str, Dict]:
        """
        Process climate data for all configured Melbourne suburbs
        
        Returns:
            Dictionary with climate data for all suburbs
        """
        all_data = {}
        suburbs = self.weather_client.MELBOURNE_SUBURBS
        
        print(f"\nProcessing {len(suburbs)} Melbourne suburbs...")
        print("="*60)
        
        for i, (suburb_name, coords) in enumerate(suburbs.items(), 1):
            print(f"[{i}/{len(suburbs)}] Processing {suburb_name}...")
            
            climate_data = self.get_complete_climate_data(
                suburb_name,
                coords["lat"],
                coords["lon"]
            )
            
            all_data[suburb_name] = climate_data
            
            # Display summary
            temp = "N/A"
            if climate_data.get("weather", {}).get("temperature"):
                temp = f"{climate_data['weather']['temperature']}°C"
            
            uv = "N/A"
            if climate_data.get("uv", {}).get("index") is not None:
                uv = climate_data["uv"]["index"]
            
            aqi = "N/A"
            if climate_data.get("air_quality", {}).get("aqi"):
                aqi = climate_data["air_quality"]["aqi"]
            
            print(f"  ✓ {suburb_name}: Temp {temp}, UV {uv}, AQI {aqi}")
            
            # Rate limiting
            time.sleep(0.1)
        
        return all_data
    
    def save_data(self, data: Dict, filename: str = None) -> str:
        """
        Save climate data to JSON file
        
        Args:
            data: Climate data to save
            filename: Optional filename
            
        Returns:
            Filename where data was saved
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"melbourne_climate_full_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Climate data saved to {filename}")
        return filename
    
    def generate_summary_report(self, data: Dict) -> None:
        """
        Generate a summary report of the climate data
        
        Args:
            data: Climate data dictionary
        """
        print("\n" + "="*60)
        print("MELBOURNE CLIMATE DATA SUMMARY")
        print("="*60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Suburbs processed: {len(data)}")
        
        # Find extremes
        hottest = None
        coldest = None
        highest_uv = None
        
        for suburb, climate in data.items():
            if climate.get("weather", {}).get("temperature"):
                temp = climate["weather"]["temperature"]
                if hottest is None or temp > hottest[1]:
                    hottest = (suburb, temp)
                if coldest is None or temp < coldest[1]:
                    coldest = (suburb, temp)
            
            if climate.get("uv", {}).get("index") is not None:
                uv = climate["uv"]["index"]
                if highest_uv is None or uv > highest_uv[1]:
                    highest_uv = (suburb, uv)
        
        print("\nCurrent Conditions:")
        if hottest:
            print(f"  Warmest suburb: {hottest[0]} ({hottest[1]}°C)")
        if coldest:
            print(f"  Coolest suburb: {coldest[0]} ({coldest[1]}°C)")
        if highest_uv:
            print(f"  UV Index: {highest_uv[1]} ({self.uv_client._get_uv_category(highest_uv[1])})")
        
        # Data source summary
        print("\nData Sources:")
        print("  ✓ ARPANSA - UV Index (real-time)")
        print("  ✓ Open-Meteo - Weather data (free, no key required)")
        print("  ✓ WAQI - Air quality data (real-time)")
        if self.epa_client:
            print("  ⚠ EPA Victoria - Air quality (backup, if configured)")
        
        print("\nData Attribution:")
        print("  • UV observations courtesy of ARPANSA")
        print("  • Weather data from Open-Meteo")
        print("  • Air quality data from World Air Quality Index Project")
        if self.epa_client:
            print("  • Additional air quality from EPA Victoria (if available)")


def main():
    """Main function to run the climate integration"""
    
    print("Melbourne Climate Data Integration System")
    print("="*60)
    print("Combining data from multiple sources:")
    print("  • ARPANSA (UV Index)")
    print("  • Open-Meteo (Weather)")
    print("  • WAQI (Air Quality)")
    print()
    
    # Initialize integration system
    # EPA API key (optional - currently not working due to subscription issues)
    epa_key = "8963cdcd394644a7a475a8c6c645671e"
    
    # WAQI API token (working!)
    waqi_token = "8f165ed38392c6e9659cc35b122eedd534fde40d"
    
    # Create integration instance with WAQI
    integration = MelbourneClimateIntegration(epa_api_key=None, waqi_token=waqi_token)
    
    # Process all suburbs
    all_climate_data = integration.process_all_suburbs()
    
    # Save data
    filename = integration.save_data(all_climate_data)
    print(f"\n✓ All climate data saved to: {filename}")
    
    # Generate summary report
    integration.generate_summary_report(all_climate_data)
    
    print("\n" + "="*60)
    print("Integration complete!")
    print("\nNote: For EPA air quality data, you need to:")
    print("1. Visit https://portal.api.epa.vic.gov.au")
    print("2. Subscribe to the 'Environment Monitoring' product")
    print("3. Contact EPA at contact@epa.vic.gov.au if issues persist")


if __name__ == "__main__":
    main()