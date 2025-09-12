from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.response import AllPlantsResponse
from app.services.plant_service import PlantService
from app.repositories.database_plant_repository import DatabasePlantRepository
from app.core.database import get_async_db

router = APIRouter(tags=["plants"])


# Dependency injection
async def get_plant_repository(
    db: AsyncSession = Depends(get_async_db)
) -> DatabasePlantRepository:
    """Get plant repository instance"""
    return DatabasePlantRepository(db)


async def get_plant_service(
    plant_repository: DatabasePlantRepository = Depends(get_plant_repository)
) -> PlantService:
    """Get plant service instance"""
    return PlantService(plant_repository)


@router.get("/plants", response_model=AllPlantsResponse)
async def get_all_plants(
    plant_service: PlantService = Depends(get_plant_service)
):
    """Get all plants from the database"""
    try:
        return await plant_service.get_all_plants_with_images()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading plants: {str(e)}")