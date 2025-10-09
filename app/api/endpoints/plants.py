from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.schemas.response import AllPlantsResponse, PaginatedPlantsResponse
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


@router.get("/plants/paginated", response_model=PaginatedPlantsResponse)
async def get_plants_paginated(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(12, ge=1, le=100, description="Number of items per page"),
    category: Optional[str] = Query(None, description="Filter by category (flower, herb, vegetable)"),
    search: Optional[str] = Query(None, description="Search term for plant name, scientific name, or description"),
    plant_service: PlantService = Depends(get_plant_service)
):
    """Get paginated plants with optional filtering.

    This endpoint supports:
    - Pagination with customizable page size
    - Filtering by plant category
    - Searching by plant name, scientific name, or description

    Args:
        page: Page number (1-based indexing)
        limit: Number of plants per page (max 100)
        category: Optional category filter
        search: Optional search term

    Returns:
        PaginatedPlantsResponse with plants and pagination metadata
    """
    try:
        return await plant_service.get_plants_paginated(
            page=page,
            limit=limit,
            category=category,
            search_term=search
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading plants: {str(e)}")


@router.get("/plants/{plant_id}/companions")
async def get_plant_companions(
    plant_id: int,
    plant_service: PlantService = Depends(get_plant_service)
):
    """Get companion planting information for a specific plant.

    Returns detailed companion planting data including:
    - Beneficial companions: Plants that grow well together and provide mutual benefits
    - Harmful companions: Plants that should be avoided as they may compete or harm each other
    - Neutral companions: Compatible plants that can be grown together without issues

    Args:
        plant_id: Database ID of the plant

    Returns:
        Dictionary containing companion planting information
    """
    try:
        companion_data = await plant_service.get_plant_companions(plant_id)
        if not companion_data:
            raise HTTPException(status_code=404, detail="Plant not found")
        return companion_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting companion data: {str(e)}")