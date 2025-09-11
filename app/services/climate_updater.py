"""
Climate Update Service
Orchestrates fetching climate data from multiple APIs and storing in database
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.apis.open_meteo import OpenMeteoClient
from app.services.apis.arpansa import ARPANSAClient
from app.services.apis.waqi import WAQIClient
from app.repositories.climate_repository import ClimateRepository
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClimateUpdateService:
    """Service for updating climate data from multiple sources"""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize climate update service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.climate_repo = ClimateRepository(db)
        self.weather_client = OpenMeteoClient()
        self.uv_client = ARPANSAClient()
        self.aqi_client = WAQIClient(settings.WAQI_API_TOKEN)
        
        # Statistics for tracking update progress
        self.stats = {
            "suburbs_processed": 0,
            "suburbs_succeeded": 0,
            "suburbs_failed": 0,
            "api_errors": [],
            "start_time": None,
            "end_time": None
        }
    
    async def update_all_suburbs(self, batch_size: int = 10) -> Dict[str, Any]:
        """
        Update climate data for all suburbs.
        
        Args:
            batch_size: Number of suburbs to process in parallel
            
        Returns:
            Update statistics
        """
        self.stats["start_time"] = datetime.utcnow()
        logger.info("Starting climate update for all suburbs")
        
        try:
            # Get all suburbs from database
            suburbs = await self.climate_repo.get_all_suburbs()
            total_suburbs = len(suburbs)
            logger.info(f"Found {total_suburbs} suburbs to update")
            
            # Get Melbourne-wide UV data once (same for all suburbs)
            uv_data = await self.uv_client.get_melbourne_uv()
            if not uv_data:
                logger.warning("Failed to fetch UV data from ARPANSA")
            
            # Process suburbs in batches
            for i in range(0, total_suburbs, batch_size):
                batch = suburbs[i:i + batch_size]
                await self._process_suburb_batch(batch, uv_data)
                
                # Log progress
                processed = min(i + batch_size, total_suburbs)
                logger.info(f"Progress: {processed}/{total_suburbs} suburbs processed")
                
                # Small delay between batches to avoid overwhelming APIs
                if i + batch_size < total_suburbs:
                    await asyncio.sleep(1)
            
            # Update API cache status
            await self._update_api_cache_status()
            
        except Exception as e:
            logger.error(f"Error during climate update: {e}")
            self.stats["api_errors"].append(str(e))
        
        self.stats["end_time"] = datetime.utcnow()
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        logger.info(f"Climate update completed in {duration:.2f} seconds")
        logger.info(f"Succeeded: {self.stats['suburbs_succeeded']}, Failed: {self.stats['suburbs_failed']}")
        
        return self.stats
    
    async def update_single_suburb(self, suburb_name: str) -> Dict[str, Any]:
        """
        Update climate data for a single suburb.
        
        Args:
            suburb_name: Name of the suburb to update
            
        Returns:
            Update result
        """
        logger.info(f"Updating climate data for {suburb_name}")
        
        # Get suburb from database
        suburb = await self.climate_repo.get_suburb_by_name(suburb_name)
        if not suburb:
            return {"success": False, "error": f"Suburb '{suburb_name}' not found"}
        
        # Fetch data from all APIs
        climate_data = await self._fetch_climate_for_suburb(
            suburb.name,
            suburb.latitude,
            suburb.longitude
        )
        
        if climate_data:
            # Save to database
            await self.climate_repo.save_climate_data(suburb.id, climate_data)
            return {"success": True, "data": climate_data}
        else:
            return {"success": False, "error": "Failed to fetch climate data"}
    
    async def _process_suburb_batch(self, suburbs: List[Dict], uv_data: Optional[Dict]) -> None:
        """
        Process a batch of suburbs in parallel.
        
        Args:
            suburbs: List of suburb dictionaries
            uv_data: UV data for Melbourne (same for all suburbs)
        """
        tasks = []
        for suburb in suburbs:
            task = self._update_suburb_climate(suburb, uv_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for suburb, result in zip(suburbs, results):
            if isinstance(result, Exception):
                logger.error(f"Error updating {suburb['name']}: {result}")
                self.stats["suburbs_failed"] += 1
                self.stats["api_errors"].append(f"{suburb['name']}: {str(result)}")
            elif result:
                self.stats["suburbs_succeeded"] += 1
            else:
                self.stats["suburbs_failed"] += 1
            
            self.stats["suburbs_processed"] += 1
    
    async def _update_suburb_climate(self, suburb: Dict, uv_data: Optional[Dict]) -> bool:
        """
        Update climate data for a single suburb.
        
        Args:
            suburb: Suburb dictionary with id, name, latitude, longitude
            uv_data: UV data for Melbourne
            
        Returns:
            True if successful, False otherwise
        """
        try:
            climate_data = await self._fetch_climate_for_suburb(
                suburb["name"],
                suburb["latitude"],
                suburb["longitude"],
                uv_data
            )
            
            if climate_data:
                await self.climate_repo.save_climate_data(suburb["id"], climate_data)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating climate for {suburb['name']}: {e}")
            return False
    
    async def _fetch_climate_for_suburb(
        self,
        suburb_name: str,
        latitude: float,
        longitude: float,
        uv_data: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch climate data from all APIs for a suburb.
        
        Args:
            suburb_name: Name of the suburb
            latitude: Suburb latitude
            longitude: Suburb longitude
            uv_data: Optional pre-fetched UV data
            
        Returns:
            Combined climate data or None if all APIs fail
        """
        climate_data = {
            "data_source": {}
        }
        
        # Fetch weather data from Open-Meteo
        try:
            weather = await self.weather_client.get_weather(latitude, longitude)
            if weather:
                climate_data.update({
                    "temperature_current": weather.get("temperature_current"),
                    "temperature_max": weather.get("temperature_max"),
                    "temperature_min": weather.get("temperature_min"),
                    "humidity": weather.get("humidity"),
                    "rainfall": weather.get("rainfall"),
                    "wind_speed": weather.get("wind_speed"),
                    "weather_code": weather.get("weather_code")
                })
                climate_data["data_source"]["weather"] = "open_meteo"
        except Exception as e:
            logger.error(f"Error fetching weather for {suburb_name}: {e}")
        
        # Use provided UV data or fetch new
        if uv_data is None:
            try:
                uv_data = await self.uv_client.get_melbourne_uv()
            except Exception as e:
                logger.error(f"Error fetching UV data: {e}")
        
        if uv_data:
            climate_data.update({
                "uv_index": uv_data.get("uv_index"),
                "uv_category": uv_data.get("uv_category"),
                "uv_protection_required": uv_data.get("uv_protection_required")
            })
            climate_data["data_source"]["uv"] = "arpansa"
        
        # Fetch air quality data from WAQI
        try:
            aqi = await self.aqi_client.get_nearest_station_aqi(latitude, longitude)
            if aqi:
                climate_data.update({
                    "air_quality_index": aqi.get("air_quality_index"),
                    "air_quality_category": aqi.get("air_quality_category"),
                    "pm25": aqi.get("pm25"),
                    "pm10": aqi.get("pm10"),
                    "ozone": aqi.get("ozone"),
                    "nitrogen_dioxide": aqi.get("nitrogen_dioxide"),
                    "sulfur_dioxide": aqi.get("sulfur_dioxide"),
                    "carbon_monoxide": aqi.get("carbon_monoxide")
                })
                climate_data["data_source"]["air_quality"] = "waqi"
        except Exception as e:
            logger.error(f"Error fetching AQI for {suburb_name}: {e}")
        
        # Return None if no data was fetched
        if not climate_data["data_source"]:
            return None
        
        return climate_data
    
    async def _update_api_cache_status(self) -> None:
        """Update API cache status in database"""
        try:
            # Update cache status for each API
            for api_name, status in [
                ("open_meteo", "success" if self.stats["suburbs_succeeded"] > 0 else "error"),
                ("arpansa", "success" if self.stats["suburbs_succeeded"] > 0 else "error"),
                ("waqi", "success" if self.stats["suburbs_succeeded"] > 0 else "error")
            ]:
                duration_ms = None
                if self.stats["start_time"] and self.stats["end_time"]:
                    duration_ms = int((self.stats["end_time"] - self.stats["start_time"]).total_seconds() * 1000)
                
                await self.climate_repo.update_api_cache(
                    api_name=api_name,
                    status=status,
                    response_time_ms=duration_ms,
                    records_updated=self.stats["suburbs_succeeded"]
                )
        except Exception as e:
            logger.error(f"Error updating API cache status: {e}")
    
    async def get_update_status(self) -> Dict[str, Any]:
        """
        Get the status of climate updates.
        
        Returns:
            Status information including last update times
        """
        api_status = await self.climate_repo.get_api_cache_status()
        
        # Get count of suburbs with current data
        suburbs = await self.climate_repo.get_all_suburbs()
        today = date.today()
        current_count = 0
        
        for suburb in suburbs:
            latest = await self.climate_repo.get_latest_climate_by_suburb(suburb["name"])
            if latest and latest.get("recorded_date") == today.isoformat():
                current_count += 1
        
        return {
            "api_status": api_status,
            "suburbs_total": len(suburbs),
            "suburbs_current": current_count,
            "suburbs_outdated": len(suburbs) - current_count,
            "last_update": self.stats.get("end_time"),
            "update_in_progress": self.stats.get("start_time") and not self.stats.get("end_time")
        }