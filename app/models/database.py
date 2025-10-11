"""
Database models for Plantopia using SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, JSON, ForeignKey, UniqueConstraint, Index
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

    # Position and characteristics from CSV
    position = Column(Text)  # e.g., "Full sun, well drained soil"
    characteristics = Column(Text)  # e.g., "Fast growing, drought tolerant"

    # Additional CSV fields
    plant_type = Column(Text)  # e.g., "Dwarf perennial to 25cm; Lavender coloured flower spikes"
    season = Column(String(100))  # e.g., "Spring", "Spring and summer"
    germination = Column(String(200))  # e.g., "10-14 days @ 18-20°C"
    additional_information = Column(Text)  # Extra details about the plant
    days_to_maturity = Column(String(100))  # Raw days to maturity string from CSV
    plant_spacing = Column(String(100))  # Raw spacing string from CSV
    sowing_depth = Column(String(100))  # Raw sowing depth string from CSV
    hardiness_life_cycle = Column(String(200))  # e.g., "Half Hardy Annual", "Hardy Perennial"
    seed_type = Column(String(100))  # Type of seed

    # Companion planting fields
    beneficial_companions = Column(Text)  # Plants that grow well together
    harmful_companions = Column(Text)  # Plants to avoid planting nearby
    neutral_companions = Column(Text)  # Compatible plants

    # Climate-specific sowing periods
    cool_climate_sowing_period = Column(String(200))
    temperate_climate_sowing_period = Column(String(200))
    subtropical_climate_sowing_period = Column(String(200))
    tropical_climate_sowing_period = Column(String(200))
    arid_climate_sowing_period = Column(String(200))

    # Fields for recommendation engine
    sun_need = Column(String(50))  # full_sun, part_sun, bright_shade
    indoor_ok = Column(Boolean, default=False)
    container_ok = Column(Boolean, default=False)
    edible = Column(Boolean, default=False)
    sowing_months_by_climate = Column(JSON)  # {"temperate": ["March", "April"], ...}
    maintainability_score = Column(Float)  # 0.0 to 1.0
    time_to_maturity_days = Column(Integer)
    habit = Column(String(100))  # growth habit
    fragrant = Column(Boolean, default=False)
    flower_colors = Column(JSON)  # ["purple", "white", ...]
    sowing_depth_mm = Column(Integer)
    spacing_cm = Column(Integer)
    sowing_method = Column(Text)
    
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

    # Urban Heat Island data
    suburb_heat_category = Column(String(50))  # Low Heat, Moderate Heat, High Heat, Extreme Heat
    suburb_heat_intensity = Column(Float)  # Heat intensity value in Celsius

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


class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)  # Nullable - auth handled by frontend
    email = Column(String(255), unique=True, nullable=False, index=True)  # Primary identifier
    name = Column(String(255))
    avatar_url = Column(Text)
    suburb_id = Column(Integer, ForeignKey('suburbs.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    suburb = relationship("Suburb")
    profile = relationship("UserProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_user_google_id', 'google_id'),
        Index('idx_user_email', 'email'),
    )


class UserProfile(Base):
    """User profile model for personalization and preferences"""
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    experience_level = Column(String(50))  # beginner/intermediate/advanced
    garden_type = Column(String(100))  # balcony/backyard/indoor/courtyard/community_garden
    climate_goals = Column(Text)
    available_space_m2 = Column(Float)
    sun_exposure = Column(String(50))  # full_sun/part_sun/bright_shade/low_light
    has_containers = Column(Boolean, default=False)
    organic_preference = Column(Boolean, default=True)
    budget_level = Column(String(50))  # low/medium/high
    notification_preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="profile")


class UserFavorite(Base):
    """User favorite plants model"""
    __tablename__ = 'user_favorites'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plant_id = Column(Integer, ForeignKey('plants.id'), nullable=False)
    notes = Column(Text)
    priority_level = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="favorites")
    plant = relationship("Plant")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'plant_id', name='unique_user_plant_favorite'),
        Index('idx_user_favorites_user_created', 'user_id', 'created_at'),
    )


class UserGuideFavorite(Base):
    """User favorite plant guides model"""
    __tablename__ = 'user_guide_favorites'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    guide_name = Column(String(255), nullable=False)  # Filename of the guide (e.g., "beginner_guide.md")
    category = Column(String(100))  # Optional category for organization
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'guide_name', name='unique_user_guide_favorite'),
        Index('idx_user_guide_favorites_user_created', 'user_id', 'created_at'),
    )


# ============================================================================
# PLANT TRACKING MODELS (Iteration 3)
# ============================================================================

class PlantGrowthData(Base):
    """
    Plant growth data model - Stores external API-generated growth data
    shared across all users for each plant type.
    """
    __tablename__ = 'plant_growth_data'

    plant_id = Column(Integer, ForeignKey('plants.id'), primary_key=True)
    requirements_checklist = Column(JSON, nullable=False)  # Array of required materials/tools by category
    setup_instructions = Column(JSON, nullable=False)  # Step-by-step growing instructions
    growth_stages = Column(JSON, nullable=False)  # Timeline stages with descriptions and indicators
    care_tips = Column(JSON, nullable=False)  # Stage-based care tips (15-20 per plant)
    data_source_info = Column(JSON)  # API metadata for tracking
    last_updated = Column(DateTime, default=datetime.utcnow)
    version = Column(String(50), default='1.0')

    # Relationships
    plant = relationship("Plant")

    # Indexes
    __table_args__ = (
        Index('idx_plant_growth_data_updated', 'last_updated'),
    )


class UserPlantInstance(Base):
    """
    User plant instance model - Tracks individual user's plant growing sessions.
    Allows users to grow multiple instances of the same plant with unique timelines.
    """
    __tablename__ = 'user_plant_instances'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plant_id = Column(Integer, ForeignKey('plants.id'), nullable=False)
    plant_nickname = Column(String(100), nullable=False)  # User's custom name
    start_date = Column(Date, nullable=False)
    expected_maturity_date = Column(Date, nullable=False)  # Calculated from start_date + time_to_maturity_days
    current_stage = Column(String(50), default='germination')  # Current growth stage
    is_active = Column(Boolean, default=True)  # Whether still actively growing
    user_notes = Column(Text)  # User's personal notes
    location_details = Column(String(200))  # Where planted (e.g., "balcony pot 1")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    plant = relationship("Plant")
    progress_tracking = relationship("UserProgressTracking", back_populates="plant_instance", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_user_plant_instances_user_active', 'user_id', 'is_active'),
        Index('idx_user_plant_instances_plant', 'plant_id'),
        Index('idx_user_plant_instances_stage', 'current_stage'),
    )


class UserProgressTracking(Base):
    """
    User progress tracking model - Tracks checklist completion and milestones
    for each user's plant instance.
    """
    __tablename__ = 'user_progress_tracking'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_plant_instance_id = Column(Integer, ForeignKey('user_plant_instances.id', ondelete='CASCADE'), nullable=False)
    checklist_item_key = Column(String(200), nullable=False)  # Maps to plant_growth_data.requirements_checklist
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    user_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    plant_instance = relationship("UserPlantInstance", back_populates="progress_tracking")

    # Indexes and constraints
    __table_args__ = (
        Index('idx_user_progress_tracking_instance', 'user_plant_instance_id'),
        Index('idx_user_progress_tracking_completed', 'user_plant_instance_id', 'is_completed'),
        UniqueConstraint('user_plant_instance_id', 'checklist_item_key', name='unique_instance_checklist_item'),
    )


# ============================================================================
# AI CHAT MODELS (Iteration 3 - Session 3)
# ============================================================================

class UserPlantChat(Base):
    """
    User plant chat model - Stores AI chat sessions for users.
    Supports both general agriculture Q&A and plant-specific conversations.
    Auto-expires after 6 hours for privacy and token management.
    """
    __tablename__ = 'user_plant_chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_plant_instance_id = Column(Integer, ForeignKey('user_plant_instances.id'), nullable=True)
    # NULL = general chat, NOT NULL = plant-specific chat

    chat_type = Column(String(20), nullable=False)  # 'general' or 'plant_specific'
    total_tokens = Column(Integer, default=0)  # Cumulative token count for conversation
    message_count = Column(Integer, default=0)  # Total messages in conversation
    is_active = Column(Boolean, default=True)  # Whether chat is still active

    created_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # created_at + 6 hours

    # Relationships
    user = relationship("User")
    plant_instance = relationship("UserPlantInstance")
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")

    # Indexes for performance and cleanup
    __table_args__ = (
        Index('idx_user_plant_chats_user', 'user_id'),
        Index('idx_user_plant_chats_type', 'chat_type'),
        Index('idx_user_plant_chats_active', 'is_active'),
        Index('idx_user_plant_chats_expires', 'expires_at'),  # For cleanup job
        Index('idx_user_plant_chats_created', 'created_at'),
    )


class ChatMessage(Base):
    """
    Chat message model - Stores individual messages in chat conversations.
    Supports both text and image inputs with token tracking.
    """
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('user_plant_chats.id', ondelete='CASCADE'), nullable=False)

    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)  # Message text content

    # Image support
    image_url = Column(String(500), nullable=True)  # GCS URL if image uploaded
    has_image = Column(Boolean, default=False)

    tokens_used = Column(Integer, default=0)  # Tokens consumed by this message
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat = relationship("UserPlantChat", back_populates="messages")

    # Indexes for performance
    __table_args__ = (
        Index('idx_chat_messages_chat', 'chat_id'),
        Index('idx_chat_messages_created', 'created_at'),
    )