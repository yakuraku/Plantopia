"""
Climate data repository for managing weather and environmental data
"""
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from app.models.database import ClimateData, Suburb, APICache


class ClimateRepository:
    """Repository for managing climate data"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_latest_climate_by_suburb(self, suburb_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent climate data for a suburb.
        
        Args:
            suburb_name: Name of the suburb
            
        Returns:
            Climate data dictionary or None if not found
        """
        # First get the suburb
        suburb_query = select(Suburb).where(
            func.lower(Suburb.name) == suburb_name.lower()
        )
        suburb_result = await self.db.execute(suburb_query)
        suburb = suburb_result.scalar_one_or_none()
        
        if not suburb:
            return None
        
        # Get latest climate data
        climate_query = select(ClimateData).where(
            ClimateData.suburb_id == suburb.id
        ).order_by(desc(ClimateData.recorded_date)).limit(1)
        
        result = await self.db.execute(climate_query)
        climate = result.scalar_one_or_none()
        
        if not climate:
            return None
        
        return self._climate_to_dict(climate, suburb)
    
    async def get_climate_history(
        self,
        suburb_name: str,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get historical climate data for a suburb.
        
        Args:
            suburb_name: Name of the suburb
            days: Number of days of history to retrieve
            
        Returns:
            List of climate data dictionaries
        """
        # Get the suburb
        suburb_query = select(Suburb).where(
            func.lower(Suburb.name) == suburb_name.lower()
        )
        suburb_result = await self.db.execute(suburb_query)
        suburb = suburb_result.scalar_one_or_none()
        
        if not suburb:
            return []
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get climate history
        climate_query = select(ClimateData).where(
            and_(
                ClimateData.suburb_id == suburb.id,
                ClimateData.recorded_date >= start_date,
                ClimateData.recorded_date <= end_date
            )
        ).order_by(desc(ClimateData.recorded_date))
        
        result = await self.db.execute(climate_query)
        climate_records = result.scalars().all()
        
        return [self._climate_to_dict(record, suburb) for record in climate_records]
    
    async def save_climate_data(
        self,
        suburb_id: int,
        climate_data: Dict[str, Any]
    ) -> ClimateData:
        """Save or update climate data for a suburb.
        
        Args:
            suburb_id: Database ID of the suburb
            climate_data: Dictionary containing climate information
            
        Returns:
            Created or updated ClimateData instance
        """
        # Check if we already have data for today
        today = date.today()
        existing_query = select(ClimateData).where(
            and_(
                ClimateData.suburb_id == suburb_id,
                ClimateData.recorded_date == today
            )
        )
        existing_result = await self.db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            # Update existing record
            for key, value in climate_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            climate_record = existing
        else:
            # Create new record
            climate_record = ClimateData(
                suburb_id=suburb_id,
                recorded_date=today,
                **climate_data
            )
            self.db.add(climate_record)
        
        await self.db.commit()
        await self.db.refresh(climate_record)
        
        return climate_record
    
    async def get_suburb_by_name(self, suburb_name: str) -> Optional[Suburb]:
        """Get a suburb by name.
        
        Args:
            suburb_name: Name of the suburb
            
        Returns:
            Suburb instance or None if not found
        """
        query = select(Suburb).where(
            func.lower(Suburb.name) == suburb_name.lower()
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_suburb(
        self,
        name: str,
        latitude: float,
        longitude: float,
        postcode: Optional[str] = None
    ) -> Suburb:
        """Create a new suburb.
        
        Args:
            name: Suburb name
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            postcode: Optional postcode
            
        Returns:
            Created Suburb instance
        """
        suburb = Suburb(
            name=name,
            latitude=latitude,
            longitude=longitude,
            postcode=postcode,
            state='VIC'
        )
        self.db.add(suburb)
        await self.db.commit()
        await self.db.refresh(suburb)
        
        return suburb
    
    async def get_all_suburbs(self) -> List[Dict[str, Any]]:
        """Get all suburbs.
        
        Returns:
            List of suburb dictionaries
        """
        result = await self.db.execute(select(Suburb).order_by(Suburb.name))
        suburbs = result.scalars().all()
        
        return [
            {
                'id': suburb.id,
                'name': suburb.name,
                'postcode': suburb.postcode,
                'latitude': suburb.latitude,
                'longitude': suburb.longitude,
                'state': suburb.state
            }
            for suburb in suburbs
        ]
    
    async def update_api_cache(
        self,
        api_name: str,
        status: str,
        error_message: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        records_updated: Optional[int] = None
    ) -> APICache:
        """Update API cache status.
        
        Args:
            api_name: Name of the API
            status: Status of the last update
            error_message: Optional error message
            response_time_ms: Response time in milliseconds
            records_updated: Number of records updated
            
        Returns:
            Updated APICache instance
        """
        # Check if cache entry exists
        query = select(APICache).where(APICache.api_name == api_name)
        result = await self.db.execute(query)
        cache_entry = result.scalar_one_or_none()
        
        now = datetime.utcnow()
        
        if cache_entry:
            cache_entry.last_update = now
            if status == 'success':
                cache_entry.last_success = now
            cache_entry.status = status
            cache_entry.error_message = error_message
            cache_entry.response_time_ms = response_time_ms
            cache_entry.records_updated = records_updated
        else:
            cache_entry = APICache(
                api_name=api_name,
                last_update=now,
                last_success=now if status == 'success' else None,
                status=status,
                error_message=error_message,
                response_time_ms=response_time_ms,
                records_updated=records_updated
            )
            self.db.add(cache_entry)
        
        await self.db.commit()
        await self.db.refresh(cache_entry)
        
        return cache_entry
    
    async def get_api_cache_status(self) -> List[Dict[str, Any]]:
        """Get status of all API caches.
        
        Returns:
            List of API cache status dictionaries
        """
        result = await self.db.execute(select(APICache))
        cache_entries = result.scalars().all()
        
        return [
            {
                'api_name': entry.api_name,
                'last_update': entry.last_update.isoformat() if entry.last_update else None,
                'last_success': entry.last_success.isoformat() if entry.last_success else None,
                'status': entry.status,
                'error_message': entry.error_message,
                'response_time_ms': entry.response_time_ms,
                'records_updated': entry.records_updated
            }
            for entry in cache_entries
        ]
    
    def _climate_to_dict(self, climate: ClimateData, suburb: Suburb) -> Dict[str, Any]:
        """Convert ClimateData model to dictionary.
        
        Args:
            climate: ClimateData model instance
            suburb: Associated Suburb instance
            
        Returns:
            Dictionary representation of climate data
        """
        return {
            'suburb': {
                'name': suburb.name,
                'postcode': suburb.postcode,
                'latitude': suburb.latitude,
                'longitude': suburb.longitude
            },
            'weather': {
                'temperature_current': climate.temperature_current,
                'temperature_max': climate.temperature_max,
                'temperature_min': climate.temperature_min,
                'humidity': climate.humidity,
                'rainfall': climate.rainfall,
                'wind_speed': climate.wind_speed,
                'weather_code': climate.weather_code
            },
            'uv': {
                'index': climate.uv_index,
                'category': climate.uv_category,
                'protection_required': climate.uv_protection_required
            },
            'air_quality': {
                'aqi': climate.air_quality_index,
                'category': climate.air_quality_category,
                'pm25': climate.pm25,
                'pm10': climate.pm10,
                'ozone': climate.ozone,
                'nitrogen_dioxide': climate.nitrogen_dioxide,
                'sulfur_dioxide': climate.sulfur_dioxide,
                'carbon_monoxide': climate.carbon_monoxide
            },
            'recorded_date': climate.recorded_date.isoformat() if climate.recorded_date else None,
            'data_source': climate.data_source,
            'created_at': climate.created_at.isoformat() if climate.created_at else None
        }