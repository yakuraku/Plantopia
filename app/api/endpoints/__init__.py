from fastapi import APIRouter

from app.api.endpoints import health, recommendations, plants, climate, admin

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(recommendations.router, prefix="", tags=["recommendations"])
api_router.include_router(plants.router, prefix="", tags=["plants"])
api_router.include_router(climate.router, prefix="", tags=["climate"])
api_router.include_router(admin.router, prefix="", tags=["admin"])  # admin router already has /admin prefix