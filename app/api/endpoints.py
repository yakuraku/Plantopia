from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.schemas.request import RecommendationRequest, PlantScoreRequest
from app.schemas.response import (
    RecommendationResponse, PlantScoreResponse, 
    AllPlantsResponse, HealthCheckResponse
)
from app.services.plant_service import PlantService
from app.services.recommendation_service import RecommendationService
from app.repositories.plant_repository import PlantRepository

# Create router
router = APIRouter()

# Dependency injection
def get_plant_repository() -> PlantRepository:
    """Get plant repository instance"""
    return PlantRepository()

def get_plant_service(
    plant_repository: PlantRepository = Depends(get_plant_repository)
) -> PlantService:
    """Get plant service instance"""
    return PlantService(plant_repository)

def get_recommendation_service(
    plant_repository: PlantRepository = Depends(get_plant_repository)
) -> RecommendationService:
    """Get recommendation service instance"""
    return RecommendationService(plant_repository)


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse()


@router.post("/recommendations")
async def get_recommendations(
    request: RecommendationRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """Generate plant recommendations based on user preferences"""
    try:
        recommendations = recommendation_service.generate_recommendations(request)
        return recommendations
    except Exception as e:
        import traceback
        print(f"Error in recommendations endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get("/plants", response_model=AllPlantsResponse)
async def get_all_plants(
    plant_service: PlantService = Depends(get_plant_service)
):
    """Get all plants from the database"""
    try:
        return plant_service.get_all_plants_with_images()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading plants: {str(e)}")


@router.post("/plant-score", response_model=PlantScoreResponse)
async def get_plant_score(
    request: PlantScoreRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """Score a specific plant based on user preferences"""
    try:
        return recommendation_service.score_plant(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")