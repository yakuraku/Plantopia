from fastapi import APIRouter
from app.schemas.response import HealthCheckResponse

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse()