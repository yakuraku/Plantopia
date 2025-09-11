"""
World Air Quality Index (WAQI) API Client
Provides air quality data for cities worldwide
"""
import aiohttp
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class WAQIClient:
    """Client for fetching air quality data from WAQI"""
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize WAQI client.
        
        Args:
            api_token: WAQI API token (optional, uses default if not provided)
        """
        # Use provided token or default token from existing code
        self.api_token = api_token or "8f165ed38392c6e9659cc35b122eedd534fde40d"
        self.base_url = "https://api.waqi.info"
        
        # Melbourne monitoring stations from WAQI
        self.melbourne_stations = {
            "melbourne-cbd": "@8850",
            "footscray": "@11388",
            "alphington": "@8831",
            "brighton": "@8833",
            "box-hill": "@8832",
            "dandenong": "@8834",
            "geelong-south": "@8835",
            "melton": "@8837",
            "mooroolbark": "@12411",
            "point-cook": "@10135"
        }
    
    async def get_air_quality_by_coords(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Fetch air quality data for given coordinates.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            
        Returns:
            Air quality data dictionary or None if error
        """
        url = f"{self.base_url}/feed/geo:{latitude};{longitude}/?token={self.api_token}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "ok":
                            return self._parse_aqi_data(data.get("data", {}))
                        else:
                            logger.warning(f"WAQI API error: {data.get('data', 'Unknown error')}")
                            return None
                    else:
                        logger.warning(f"WAQI API returned status {response.status}")
                        return None
                        
        except aiohttp.ClientTimeout:
            logger.error("WAQI API request timed out")
            return None
        except Exception as e:
            logger.error(f"Error fetching air quality data: {e}")
            return None
    
    async def get_melbourne_stations_aqi(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetch air quality data from all Melbourne monitoring stations.
        
        Returns:
            Dictionary mapping station names to air quality data
        """
        results = {}
        
        for station_name, station_id in self.melbourne_stations.items():
            url = f"{self.base_url}/feed/{station_id}/?token={self.api_token}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("status") == "ok":
                                aqi_data = self._parse_aqi_data(data.get("data", {}))
                                if aqi_data:
                                    results[station_name] = aqi_data
            except Exception as e:
                logger.error(f"Error fetching data for {station_name}: {e}")
                continue
        
        return results
    
    def _parse_aqi_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse WAQI API response into our format.
        
        Args:
            data: Raw API response data
            
        Returns:
            Parsed air quality data
        """
        try:
            # Get AQI value
            aqi = data.get("aqi")
            if aqi is None or aqi == "-":
                return None
            
            # Try to convert AQI to integer
            try:
                aqi = int(aqi)
            except (ValueError, TypeError):
                return None
            
            # Get pollutant values
            iaqi = data.get("iaqi", {})
            
            return {
                "air_quality_index": aqi,
                "air_quality_category": self._get_aqi_category(aqi),
                "pm25": iaqi.get("pm25", {}).get("v"),
                "pm10": iaqi.get("pm10", {}).get("v"),
                "ozone": iaqi.get("o3", {}).get("v"),
                "nitrogen_dioxide": iaqi.get("no2", {}).get("v"),
                "sulfur_dioxide": iaqi.get("so2", {}).get("v"),
                "carbon_monoxide": iaqi.get("co", {}).get("v"),
                "dominant_pollutant": data.get("dominentpol"),
                "station_name": data.get("city", {}).get("name"),
                "measurement_time": data.get("time", {}).get("s"),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "waqi"
            }
            
        except Exception as e:
            logger.error(f"Error parsing AQI data: {e}")
            return None
    
    def _get_aqi_category(self, aqi: int) -> str:
        """
        Get AQI category based on index value.
        
        Args:
            aqi: Air Quality Index value
            
        Returns:
            AQI category string
        """
        if aqi <= 50:
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
    
    async def get_nearest_station_aqi(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Get air quality from the nearest monitoring station.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            
        Returns:
            Air quality data from nearest station
        """
        # For Melbourne suburbs, we'll use coordinate-based search
        # which returns data from the nearest station
        return await self.get_air_quality_by_coords(latitude, longitude)