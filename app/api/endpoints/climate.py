from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.climate_repository import ClimateRepository
from app.core.database import get_async_db

router = APIRouter(tags=["climate"])


# Dependency injection
async def get_climate_repository(
    db: AsyncSession = Depends(get_async_db)
) -> ClimateRepository:
    """Get climate repository instance"""
    return ClimateRepository(db)


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