from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.request import RecommendationRequest, PlantScoreRequest
from app.schemas.response import PlantScoreResponse
from app.services.recommendation_service import RecommendationService
from app.repositories.database_plant_repository import DatabasePlantRepository
from app.repositories.climate_repository import ClimateRepository
from app.core.database import get_async_db

router = APIRouter(tags=["recommendations"])


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


async def get_recommendation_service(
    plant_repository: DatabasePlantRepository = Depends(get_plant_repository),
    climate_repository: ClimateRepository = Depends(get_climate_repository)
) -> RecommendationService:
    """Get recommendation service instance"""
    return RecommendationService(plant_repository, climate_repository)


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