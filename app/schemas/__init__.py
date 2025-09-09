"""Request and response schemas"""

from app.schemas.request import (
    SitePreferences,
    UserPreferences,
    PracticalPreferences,
    EnvironmentPreferences,
    UserRequest,
    RecommendationRequest,
    PlantScoreRequest
)

from app.schemas.response import (
    PlantMedia,
    PlantFit,
    PlantSowing,
    PlantRecommendation,
    RecommendationResponse,
    PlantScoreResponse,
    AllPlantsResponse,
    HealthCheckResponse
)

__all__ = [
    # Request schemas
    "SitePreferences",
    "UserPreferences",
    "PracticalPreferences",
    "EnvironmentPreferences",
    "UserRequest",
    "RecommendationRequest",
    "PlantScoreRequest",
    # Response schemas
    "PlantMedia",
    "PlantFit",
    "PlantSowing",
    "PlantRecommendation",
    "RecommendationResponse",
    "PlantScoreResponse",
    "AllPlantsResponse",
    "HealthCheckResponse"
]