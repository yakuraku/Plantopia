"""
Open-Meteo Weather API Client
Free weather data API - no key required
"""
import aiohttp
import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenMeteoClient:
    """Client for fetching weather data from Open-Meteo API"""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    async def get_weather(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data for given coordinates.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            
        Returns:
            Weather data dictionary or None if error
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "rain",
                "weather_code",
                "wind_speed_10m"
            ],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum"
            ],
            "timezone": "Australia/Melbourne",
            "forecast_days": 1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_weather_data(data)
                    else:
                        logger.warning(f"Open-Meteo API returned status {response.status}")
                        return None
                        
        except aiohttp.ClientTimeout:
            logger.error("Open-Meteo API request timed out")
            return None
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def _parse_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Open-Meteo API response into our format.
        
        Args:
            data: Raw API response
            
        Returns:
            Parsed weather data
        """
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        # Get daily values (arrays with single element for today)
        temp_max = daily.get("temperature_2m_max", [None])[0]
        temp_min = daily.get("temperature_2m_min", [None])[0]
        rainfall_daily = daily.get("precipitation_sum", [0])[0]
        
        return {
            "temperature_current": current.get("temperature_2m"),
            "temperature_max": temp_max,
            "temperature_min": temp_min,
            "humidity": current.get("relative_humidity_2m"),
            "rainfall": rainfall_daily if rainfall_daily else current.get("rain", 0),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "open_meteo"
        }
    
    async def get_batch_weather(self, locations: list) -> Dict[str, Dict[str, Any]]:
        """
        Fetch weather data for multiple locations.
        
        Args:
            locations: List of dicts with 'name', 'latitude', 'longitude'
            
        Returns:
            Dictionary mapping location names to weather data
        """
        results = {}
        
        # Process in batches to avoid overwhelming the API
        for location in locations:
            weather_data = await self.get_weather(
                location["latitude"],
                location["longitude"]
            )
            if weather_data:
                results[location["name"]] = weather_data
            
            # Small delay between requests to be respectful to the free API
            await asyncio.sleep(0.1)
        
        return results


# Add asyncio import at the top
import asyncio