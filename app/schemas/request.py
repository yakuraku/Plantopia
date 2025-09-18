from pydantic import BaseModel, Field
from typing import Optional, List


class SitePreferences(BaseModel):
    """Site-specific preferences for plant recommendations"""
    location_type: str = Field(default="balcony", description="Type of location (balcony, backyard, indoor)")
    area_m2: float = Field(default=2.0, description="Available area in square meters")
    sun_exposure: str = Field(default="part_sun", description="Sun exposure level")
    wind_exposure: str = Field(default="moderate", description="Wind exposure level")
    containers: bool = Field(default=True, description="Whether using containers")
    container_sizes: List[str] = Field(default=["small", "medium"], description="Available container sizes")


class UserPreferences(BaseModel):
    """User preferences for plant characteristics"""
    goal: str = Field(default="mixed", description="Gardening goal (edible, ornamental, mixed)")
    edible_types: List[str] = Field(default=["herbs", "leafy"], description="Preferred edible plant types")
    ornamental_types: List[str] = Field(default=["flowers"], description="Preferred ornamental plant types")
    colors: List[str] = Field(default=["purple", "white"], description="Preferred flower colors")
    fragrant: bool = Field(default=True, description="Whether fragrant plants are preferred")
    maintainability: str = Field(default="low", description="Maintenance level preference")
    watering: str = Field(default="medium", description="Watering frequency preference")
    time_to_results: str = Field(default="quick", description="Time to results preference")
    season_intent: str = Field(default="start_now", description="Planting season intention")
    pollen_sensitive: bool = Field(default=False, description="Whether user is pollen sensitive")


class PracticalPreferences(BaseModel):
    """Practical considerations for plant recommendations"""
    budget: str = Field(default="medium", description="Budget level")
    has_basic_tools: bool = Field(default=True, description="Whether user has basic gardening tools")
    organic_only: bool = Field(default=False, description="Whether only organic options are preferred")


class EnvironmentPreferences(BaseModel):
    """Environmental conditions for plant recommendations"""
    climate_zone: str = Field(default="temperate", description="Climate zone")
    month_now: str = Field(default="", description="Current month")
    uv_index: float = Field(default=0.0, description="UV index")
    temperature_c: float = Field(default=8.0, description="Temperature in Celsius")
    humidity_pct: int = Field(default=75, description="Humidity percentage")
    wind_speed_kph: int = Field(default=15, description="Wind speed in km/h")


class UserRequest(BaseModel):
    """Complete user request with all preferences"""
    user_id: str = Field(default="anon_mvp", description="User identifier")
    site: SitePreferences = Field(default_factory=SitePreferences, description="Site preferences")
    preferences: UserPreferences = Field(default_factory=UserPreferences, description="User preferences")
    practical: PracticalPreferences = Field(default_factory=PracticalPreferences, description="Practical preferences")
    environment: EnvironmentPreferences = Field(default_factory=EnvironmentPreferences, description="Environment preferences")


class RecommendationRequest(BaseModel):
    """Request for plant recommendations"""
    suburb: str = Field(default="Richmond", description="Suburb for climate data")
    n: int = Field(default=6, ge=1, le=9, description="Number of recommendations")
    climate_zone: Optional[str] = Field(default=None, description="Override climate zone")
    user_preferences: UserRequest = Field(..., description="User preferences")


class PlantScoreRequest(BaseModel):
    """Request for scoring a specific plant"""
    plant_name: str = Field(..., description="Name of the plant to score")
    suburb: str = Field(default="Richmond", description="Suburb for climate data")
    climate_zone: Optional[str] = Field(default=None, description="Override climate zone")
    user_preferences: UserRequest = Field(..., description="User preferences")


class PlantQuantificationRequest(BaseModel):
    """Request for quantifying climate impact of a specific plant"""
    plant_name: str = Field(..., description="Name of the plant to quantify")
    suburb: str = Field(default="Richmond", description="Suburb for climate data")
    climate_zone: Optional[str] = Field(default=None, description="Override climate zone")
    plant_count: int = Field(default=1, ge=1, le=100, description="Number of plants to quantify")
    user_preferences: UserRequest = Field(..., description="User preferences")