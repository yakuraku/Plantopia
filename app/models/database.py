"""
Database models for Plantopia using SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, JSON, ForeignKey, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Plant(Base):
    """Plant model - stores all plant information from CSV files"""
    __tablename__ = 'plants'
    
    id = Column(Integer, primary_key=True, index=True)
    plant_name = Column(String(255), nullable=False, index=True)
    scientific_name = Column(String(255))
    plant_category = Column(String(50), index=True)  # flower, herb, vegetable
    
    # Growing requirements
    water_requirements = Column(String(100))
    sunlight_requirements = Column(String(100))
    soil_type = Column(String(200))
    growth_time = Column(String(100))
    maintenance_level = Column(String(50))
    climate_zone = Column(String(100))
    
    # Plant characteristics
    mature_height = Column(String(100))
    mature_width = Column(String(100))
    flower_color = Column(String(200))
    flowering_season = Column(String(200))
    
    # Additional information
    description = Column(Text)
    planting_tips = Column(Text)
    care_instructions = Column(Text)
    companion_plants = Column(Text)
    image_url = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_plant_category_name', 'plant_category', 'plant_name'),
    )


class Suburb(Base):
    """Suburb model - stores Melbourne suburb information"""
    __tablename__ = 'suburbs'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    postcode = Column(String(10))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    state = Column(String(50), default='VIC')
    
    # Relationships
    climate_data = relationship("ClimateData", back_populates="suburb", cascade="all, delete-orphan")
    recommendations = relationship("UserRecommendation", back_populates="suburb", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ClimateData(Base):
    """Climate data model - stores daily climate information for suburbs"""
    __tablename__ = 'climate_data'
    
    id = Column(Integer, primary_key=True, index=True)
    suburb_id = Column(Integer, ForeignKey('suburbs.id'), nullable=False)
    
    # Weather data (from Open-Meteo)
    temperature_current = Column(Float)
    temperature_max = Column(Float)
    temperature_min = Column(Float)
    humidity = Column(Integer)
    rainfall = Column(Float)
    wind_speed = Column(Float)
    weather_code = Column(Integer)  # WMO weather code
    
    # UV data (from ARPANSA)
    uv_index = Column(Float)
    uv_category = Column(String(50))  # Low, Moderate, High, Very High, Extreme
    uv_protection_required = Column(String(10))  # Yes/No
    
    # Air quality data (from WAQI/EPA)
    air_quality_index = Column(Integer)
    air_quality_category = Column(String(50))  # Good, Moderate, Poor, etc.
    pm25 = Column(Float)  # PM2.5 concentration
    pm10 = Column(Float)  # PM10 concentration
    ozone = Column(Float)
    nitrogen_dioxide = Column(Float)
    sulfur_dioxide = Column(Float)
    carbon_monoxide = Column(Float)
    
    # Record metadata
    recorded_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    data_source = Column(JSON)  # Track which APIs provided data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    suburb = relationship("Suburb", back_populates="climate_data")
    
    # Ensure unique climate records per suburb per day
    __table_args__ = (
        UniqueConstraint('suburb_id', 'recorded_date', name='unique_suburb_date'),
        Index('idx_climate_suburb_date', 'suburb_id', 'recorded_date'),
    )


class APICache(Base):
    """API cache model - tracks API update status and errors"""
    __tablename__ = 'api_cache'
    
    id = Column(Integer, primary_key=True, index=True)
    api_name = Column(String(100), nullable=False, unique=True)  # open_meteo, arpansa, waqi, epa
    last_update = Column(DateTime)
    last_success = Column(DateTime)
    status = Column(String(50))  # success, error, timeout, rate_limited
    error_message = Column(Text)
    response_time_ms = Column(Integer)
    records_updated = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserRecommendation(Base):
    """User recommendation model - stores recommendation history"""
    __tablename__ = 'user_recommendations'
    
    id = Column(Integer, primary_key=True, index=True)
    suburb_id = Column(Integer, ForeignKey('suburbs.id'))
    
    # User preferences (stored as JSON)
    preferences = Column(JSON)
    # Recommended plants (stored as JSON array of plant IDs and scores)
    recommended_plants = Column(JSON)
    
    # Request metadata
    request_ip = Column(String(50))
    user_agent = Column(Text)
    response_time_ms = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    suburb = relationship("Suburb", back_populates="recommendations")
    
    # Index for analytics
    __table_args__ = (
        Index('idx_recommendations_created', 'created_at'),
    )