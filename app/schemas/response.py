from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class PlantMedia(BaseModel):
    """Media information for a plant"""
    image_path: str = Field(default="", description="Path to the plant image")
    image_base64: str = Field(default="", description="Base64 encoded image data")
    has_image: bool = Field(default=False, description="Whether an image is available")


class PlantFit(BaseModel):
    """Plant fit characteristics"""
    sun_need: Optional[str] = Field(default=None, description="Sunlight requirements")
    time_to_maturity_days: Optional[int] = Field(default=None, description="Days to maturity")
    maintainability: Optional[str] = Field(default=None, description="Maintenance level")
    container_ok: Optional[bool] = Field(default=None, description="Suitable for containers")
    indoor_ok: Optional[bool] = Field(default=None, description="Suitable for indoor growing")
    habit: Optional[str] = Field(default=None, description="Plant growth habit")


class PlantSowing(BaseModel):
    """Plant sowing information"""
    climate_zone: str = Field(..., description="Climate zone")
    months: List[str] = Field(default_factory=list, description="Suitable sowing months")
    method: Optional[str] = Field(default=None, description="Sowing method")
    depth_mm: Optional[int] = Field(default=None, description="Sowing depth in millimeters")
    spacing_cm: Optional[int] = Field(default=None, description="Plant spacing in centimeters")
    season_label: str = Field(..., description="Season label (Start now or Plan ahead)")


class PlantRecommendation(BaseModel):
    """Individual plant recommendation"""
    plant_name: str = Field(..., description="Name of the plant")
    scientific_name: Optional[str] = Field(default=None, description="Scientific name")
    plant_category: str = Field(..., description="Plant category (flower, herb, vegetable)")
    score: float = Field(..., description="Recommendation score")
    why_recommended: str = Field(..., description="Reason for recommendation")
    sowing: PlantSowing = Field(..., description="Sowing information")
    media: Optional[PlantMedia] = Field(default=None, description="Media information")
    care_tips: Optional[List[str]] = Field(default=None, description="Care tips")
    quantified_impact: Optional[QuantifiedImpactResponse] = Field(default=None, description="Quantified climate impact")


class RecommendationResponse(BaseModel):
    """Response containing plant recommendations"""
    recommendations: List[PlantRecommendation] = Field(..., description="List of recommendations")
    context: Dict[str, Any] = Field(..., description="Context information")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")
    suburb: str = Field(..., description="Suburb used for recommendations")
    climate_zone: str = Field(..., description="Climate zone")
    month_now: str = Field(..., description="Current month")


class PlantScoreResponse(BaseModel):
    """Response for plant scoring request"""
    plant_name: str = Field(..., description="Name of the plant")
    scientific_name: Optional[str] = Field(default=None, description="Scientific name")
    plant_category: str = Field(..., description="Plant category")
    score: float = Field(..., description="Plant score")
    score_breakdown: Dict[str, float] = Field(..., description="Score breakdown by factors")
    fit: PlantFit = Field(..., description="Plant fit characteristics")
    sowing: PlantSowing = Field(..., description="Sowing information")
    media: PlantMedia = Field(..., description="Media information")
    suburb: str = Field(..., description="Suburb")
    climate_zone: str = Field(..., description="Climate zone")
    month_now: str = Field(..., description="Current month")


class AllPlantsResponse(BaseModel):
    """Response containing all plants"""
    plants: List[Dict[str, Any]] = Field(..., description="List of all plants")
    total_count: int = Field(..., description="Total number of plants")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    message: str = Field(default="Plantopia Recommendation Engine API", description="API status message")


class QuantifiedImpactResponse(BaseModel):
    """Response containing quantified climate impact for a plant"""
    temperature_reduction_c: float = Field(..., description="Temperature reduction in Celsius")
    air_quality_points: int = Field(..., description="Air quality improvement points")
    co2_absorption_kg_year: float = Field(..., description="CO2 absorption in kg/year")
    water_processed_l_week: float = Field(..., description="Water processed in L/week")
    pollinator_support: str = Field(..., description="Pollinator support level")
    edible_yield: Optional[str] = Field(default=None, description="Edible yield if applicable")
    maintenance_time: str = Field(..., description="Maintenance time requirement")
    water_requirement: str = Field(..., description="Water requirement")
    risk_badge: str = Field(..., description="Risk level (low/medium/high)")
    confidence_level: str = Field(..., description="Confidence level with percentage")
    why_this_plant: str = Field(..., description="Explanation of why this plant is suitable")
    community_impact_potential: Optional[str] = Field(default=None, description="Potential community-wide impact")


class SuitabilityScoreResponse(BaseModel):
    """Response containing suitability score with breakdown"""
    total_score: float = Field(..., description="Total suitability score (0-100)")
    breakdown: Dict[str, float] = Field(..., description="Score breakdown by factors")


class PlantQuantificationResponse(BaseModel):
    """Complete response for plant quantification"""
    plant_name: str = Field(..., description="Name of the plant")
    scientific_name: Optional[str] = Field(default=None, description="Scientific name")
    plant_category: str = Field(..., description="Plant category")
    quantified_impact: QuantifiedImpactResponse = Field(..., description="Quantified climate impact")
    suitability_score: SuitabilityScoreResponse = Field(..., description="Suitability score")
    suburb: str = Field(..., description="Suburb")
    climate_zone: str = Field(..., description="Climate zone")
    plant_count: int = Field(default=1, description="Number of plants quantified")