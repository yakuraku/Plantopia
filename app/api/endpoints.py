from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.request import RecommendationRequest, PlantScoreRequest
from app.schemas.response import (
    RecommendationResponse, PlantScoreResponse, 
    AllPlantsResponse, HealthCheckResponse
)
from app.services.plant_service import PlantService
from app.services.recommendation_service import RecommendationService
from app.repositories.database_plant_repository import DatabasePlantRepository
from app.repositories.climate_repository import ClimateRepository
from app.core.database import get_async_db

# Create router
router = APIRouter()

# Dependency injection
async def get_plant_repository(
    db: AsyncSession = Depends(get_async_db)
) -> DatabasePlantRepository:
    """Get plant repository instance"""
    return DatabasePlantRepository(db)

async def get_climate_repository(
    db: AsyncSession = Depends(get_async_db)
) -> ClimateRepository:
    """Get climate repository instance"""
    return ClimateRepository(db)

async def get_plant_service(
    plant_repository: DatabasePlantRepository = Depends(get_plant_repository)
) -> PlantService:
    """Get plant service instance"""
    return PlantService(plant_repository)

async def get_recommendation_service(
    plant_repository: DatabasePlantRepository = Depends(get_plant_repository),
    climate_repository: ClimateRepository = Depends(get_climate_repository)
) -> RecommendationService:
    """Get recommendation service instance"""
    return RecommendationService(plant_repository, climate_repository)


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
        recommendations = await recommendation_service.generate_recommendations(request)
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
        return await plant_service.get_all_plants_with_images()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading plants: {str(e)}")


@router.post("/plant-score", response_model=PlantScoreResponse)
async def get_plant_score(
    request: PlantScoreRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """Score a specific plant based on user preferences"""
    try:
        return await recommendation_service.score_plant(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get("/suburbs")
async def get_suburbs(
    climate_repository: ClimateRepository = Depends(get_climate_repository)
):
    """Get all available suburbs"""
    try:
        suburbs = await climate_repository.get_all_suburbs()
        return {"suburbs": suburbs, "total": len(suburbs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading suburbs: {str(e)}")


@router.get("/climate/{suburb_name}")
async def get_climate_data(
    suburb_name: str,
    climate_repository: ClimateRepository = Depends(get_climate_repository)
):
    """Get latest climate data for a suburb"""
    try:
        climate_data = await climate_repository.get_latest_climate_by_suburb(suburb_name)
        if not climate_data:
            raise HTTPException(status_code=404, detail=f"Climate data not found for suburb: {suburb_name}")
        return climate_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading climate data: {str(e)}")


@router.get("/climate/{suburb_name}/history")
async def get_climate_history(
    suburb_name: str,
    days: int = 7,
    climate_repository: ClimateRepository = Depends(get_climate_repository)
):
    """Get climate history for a suburb"""
    try:
        if days < 1 or days > 30:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 30")
        
        history = await climate_repository.get_climate_history(suburb_name, days)
        if not history:
            raise HTTPException(status_code=404, detail=f"No climate history found for suburb: {suburb_name}")
        
        return {"suburb": suburb_name, "days": days, "history": history}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading climate history: {str(e)}")