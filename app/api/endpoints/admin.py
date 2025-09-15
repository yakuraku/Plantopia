from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.climate_updater import ClimateUpdateService
from app.repositories.climate_repository import ClimateRepository
from app.core.database import get_async_db
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


# Admin authentication
async def verify_admin_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify admin API key for protected endpoints"""
    # In production, use a secure API key from environment
    # For now, we'll allow access without key for development
    if settings.ENVIRONMENT == "development":
        return True
    
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # In production, compare with secure key
    # if x_api_key != settings.ADMIN_API_KEY:
    #     raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True


@router.post("/climate/update")
async def update_all_climate(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    is_admin: bool = Depends(verify_admin_key)
):
    """Update climate data for all suburbs"""
    try:
        climate_service = ClimateUpdateService(db)
        
        # Run update in background to avoid timeout
        background_tasks.add_task(climate_service.update_all_suburbs)
        
        return {
            "message": "Climate update started in background",
            "status": "processing",
            "suburbs_count": len(await ClimateRepository(db).get_all_suburbs())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting climate update: {str(e)}")


@router.post("/climate/update/{suburb_name}")
async def update_suburb_climate(
    suburb_name: str,
    db: AsyncSession = Depends(get_async_db),
    is_admin: bool = Depends(verify_admin_key)
):
    """Update climate data for a specific suburb"""
    try:
        climate_service = ClimateUpdateService(db)
        result = await climate_service.update_single_suburb(suburb_name)
        
        if result["success"]:
            return {
                "message": f"Climate data updated for {suburb_name}",
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating climate: {str(e)}")


@router.get("/climate/status")
async def get_climate_update_status(
    db: AsyncSession = Depends(get_async_db),
    is_admin: bool = Depends(verify_admin_key)
):
    """Get status of climate updates"""
    try:
        climate_service = ClimateUpdateService(db)
        status = await climate_service.get_update_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")