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


@router.get("/plants/{plant_id}/image-url")
async def get_plant_image_url(
    plant_id: int,
    plant_service: PlantService = Depends(get_plant_service)
):
    """Get the primary GCS image URL for a specific plant"""
    try:
        image_url = await plant_service.get_plant_image_url(plant_id)
        if not image_url:
            raise HTTPException(status_code=404, detail="Plant or image not found")
        return {"image_url": image_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting image URL: {str(e)}")


@router.get("/plants/{plant_id}/all-images")
async def get_all_plant_images(
    plant_id: int,
    plant_service: PlantService = Depends(get_plant_service)
):
    """Get all GCS image URLs for a specific plant (usually 2-4 images)"""
    try:
        image_urls = await plant_service.get_all_plant_image_urls(plant_id)
        if not image_urls:
            raise HTTPException(status_code=404, detail="Plant not found")
        return {"image_urls": image_urls}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting image URLs: {str(e)}")