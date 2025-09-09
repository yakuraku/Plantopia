#!/usr/bin/env python3
"""
World Air Quality Index (WAQI) API Client
Free air quality data from aqicn.org
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WAQIClient:
    """Client for accessing World Air Quality Index data"""
    
    def __init__(self, api_token: str = "8f165ed38392c6e9659cc35b122eedd534fde40d"):
        """
        Initialize the WAQI client
        
        Args:
            api_token: WAQI API token
        """
        self.api_token = api_token
        self.base_url = "https://api.waqi.info"
        
        # Melbourne monitoring stations from WAQI
        self.melbourne_stations = {
            "melbourne-cbd": "@8850",  # Melbourne CBD station ID
            "footscray": "@11388",
            "alphington": "@8831",
            "brighton": "@8833",
            "box-hill": "@8832",
            "dandenong": "@8834",
            "geelong-south": "@8835",
            "melton": "@8837",
            "mooroolbark": "@12411",
            "point-cook": "@10135",
            "traralgon": "@8839"
        }
        
    def get_station_data(self, station_id: str) -> Optional[Dict]:
        """
        Get air quality data for a specific station
        
        Args:
            station_id: Station ID or name
            
        Returns:
            Air quality data dictionary or None
        """
        try:
            # Check if it's a known station name
            if station_id in self.melbourne_stations:
                station_id = self.melbourne_stations[station_id]
            
            # If it's a station ID (starts with @), use feed endpoint
            if station_id.startswith("@"):
                url = f"{self.base_url}/feed/{station_id}/?token={self.api_token}"
            else:
                # Otherwise search by name
                url = f"{self.base_url}/feed/{station_id}/?token={self.api_token}"
            
            logger.info(f"Fetching data from WAQI: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    return self._parse_waqi_data(data["data"])
                else:
                    logger.warning(f"WAQI API error: {data.get('data', 'Unknown error')}")
            else:
                logger.warning(f"Failed to fetch WAQI data: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching WAQI data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
        return None
    
    def search_melbourne(self) -> Optional[List[Dict]]:
        """
        Search for all Melbourne stations
        
        Returns:
            List of Melbourne stations or None
        """
        try:
            url = f"{self.base_url}/search/?keyword=melbourne&token={self.api_token}"
            logger.info("Searching for Melbourne stations...")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    return data.get("data", [])
                    
        except Exception as e:
            logger.error(f"Error searching Melbourne stations: {e}")
            
        return None
    
    def get_geo_data(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get air quality data for specific coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Air quality data for nearest station
        """
        try:
            url = f"{self.base_url}/feed/geo:{lat};{lon}/?token={self.api_token}"
            logger.info(f"Fetching data for coordinates: {lat}, {lon}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    return self._parse_waqi_data(data["data"])
                    
        except Exception as e:
            logger.error(f"Error fetching geo data: {e}")
            
        return None
    
    def _parse_waqi_data(self, data: Dict) -> Dict:
        """
        Parse WAQI API response data
        
        Args:
            data: Raw WAQI data
            
        Returns:
            Parsed air quality data
        """
        # Extract station info
        city_info = data.get("city", {})
        station_name = city_info.get("name", "Unknown")
        
        # Extract coordinates
        geo = city_info.get("geo", [])
        lat = geo[0] if len(geo) > 0 else None
        lon = geo[1] if len(geo) > 1 else None
        
        # Extract AQI
        aqi = data.get("aqi", None)
        
        # Extract individual pollutants
        iaqi = data.get("iaqi", {})
        pollutants = {
            "pm25": iaqi.get("pm25", {}).get("v"),
            "pm10": iaqi.get("pm10", {}).get("v"),
            "o3": iaqi.get("o3", {}).get("v"),
            "no2": iaqi.get("no2", {}).get("v"),
            "so2": iaqi.get("so2", {}).get("v"),
            "co": iaqi.get("co", {}).get("v"),
            "temperature": iaqi.get("t", {}).get("v"),
            "pressure": iaqi.get("p", {}).get("v"),
            "humidity": iaqi.get("h", {}).get("v"),
            "wind_speed": iaqi.get("w", {}).get("v")
        }
        
        # Remove None values
        pollutants = {k: v for k, v in pollutants.items() if v is not None}
        
        # Get time
        time_info = data.get("time", {})
        
        return {
            "station": station_name,
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "aqi": aqi,
            "aqi_category": self._get_aqi_category(aqi),
            "pollutants": pollutants,
            "timestamp": time_info.get("iso", ""),
            "local_time": time_info.get("s", ""),
            "timezone": time_info.get("tz", ""),
            "dominant_pollutant": data.get("dominentpol", ""),
            "attributions": [attr.get("name", "") for attr in data.get("attributions", [])]
        }
    
    def _get_aqi_category(self, aqi: Optional[int]) -> str:
        """
        Get AQI category description
        
        Args:
            aqi: Air Quality Index value
            
        Returns:
            Category description
        """
        if aqi is None:
            return "Unknown"
        elif aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    def get_all_melbourne_stations(self) -> Dict[str, Dict]:
        """
        Get air quality data for all Melbourne stations
        
        Returns:
            Dictionary of station data
        """
        all_data = {}
        
        for station_name, station_id in self.melbourne_stations.items():
            logger.info(f"Fetching {station_name}...")
            data = self.get_station_data(station_id)
            if data:
                all_data[station_name] = data
                
        return all_data
    
    def display_air_quality(self, data: Dict) -> None:
        """
        Display air quality data in formatted output
        
        Args:
            data: Air quality data dictionary
        """
        print(f"\n{'='*60}")
        print(f"Air Quality Report - {data.get('station', 'Unknown')}")
        print(f"{'='*60}")
        print(f"Time: {data.get('local_time', 'Unknown')}")
        
        aqi = data.get('aqi')
        if aqi:
            print(f"\nAir Quality Index: {aqi}")
            print(f"Category: {data.get('aqi_category', 'Unknown')}")
            
            if aqi > 100:
                print("⚠️  Air quality is concerning - consider limiting outdoor activities")
            elif aqi > 50:
                print("⚠️  Moderate air quality - sensitive individuals should be cautious")
            else:
                print("✓ Good air quality")
        
        pollutants = data.get('pollutants', {})
        if pollutants:
            print("\nPollutant Levels:")
            if 'pm25' in pollutants:
                print(f"  PM2.5: {pollutants['pm25']} μg/m³")
            if 'pm10' in pollutants:
                print(f"  PM10: {pollutants['pm10']} μg/m³")
            if 'o3' in pollutants:
                print(f"  Ozone: {pollutants['o3']} μg/m³")
            if 'no2' in pollutants:
                print(f"  NO₂: {pollutants['no2']} μg/m³")
            if 'so2' in pollutants:
                print(f"  SO₂: {pollutants['so2']} μg/m³")
            if 'co' in pollutants:
                print(f"  CO: {pollutants['co']} mg/m³")
                
            if 'temperature' in pollutants:
                print(f"\nWeather:")
                print(f"  Temperature: {pollutants['temperature']}°C")
            if 'humidity' in pollutants:
                print(f"  Humidity: {pollutants['humidity']}%")
            if 'pressure' in pollutants:
                print(f"  Pressure: {pollutants['pressure']} hPa")
                
        if data.get('dominant_pollutant'):
            print(f"\nDominant Pollutant: {data['dominant_pollutant']}")


def main():
    """Test WAQI API client"""
    
    print("World Air Quality Index (WAQI) API Client")
    print("Real-time air quality data from aqicn.org")
    print("="*60)

    client = WAQIClient(api_token="8f165ed38392c6e9659cc35b122eedd534fde40d")
    
    print("\nNote: Using 'demo' token with limited access.")
    print("Get your free API token at: https://aqicn.org/data-platform/token/")
    
    # Test Melbourne CBD
    print("\n1. Testing Melbourne CBD station...")
    cbd_data = client.get_station_data("melbourne")
    if cbd_data:
        print("✓ Successfully fetched Melbourne CBD data!")
        client.display_air_quality(cbd_data)
    else:
        print("✗ Failed to fetch Melbourne CBD data")
    
    # Test geo-based query for Melbourne coordinates
    print("\n2. Testing geo-based query for Melbourne...")
    geo_data = client.get_geo_data(-37.8136, 144.9631)
    if geo_data:
        print("✓ Successfully fetched nearest station data!")
        client.display_air_quality(geo_data)
    
    # Search for Melbourne stations
    print("\n3. Searching for Melbourne stations...")
    stations = client.search_melbourne()
    if stations:
        print(f"✓ Found {len(stations)} Melbourne stations:")
        for station in stations[:5]:  # Show first 5
            print(f"  • {station.get('station', {}).get('name', 'Unknown')}")
    
    # Save sample data
    if cbd_data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"waqi_melbourne_air_quality_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(cbd_data, f, indent=2)
        print(f"\n✓ Air quality data saved to: {filename}")
    
    print("\n" + "="*60)
    print("Data Attribution: World Air Quality Index Project")
    print("Visit https://waqi.info for more information")


if __name__ == "__main__":
    main()