from fastapi import APIRouter

from app.api.endpoints import health, recommendations, plants, climate, admin, markdown_content, quantification, uhi, auth, favorites, plant_tracking, plant_chat

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(recommendations.router, prefix="", tags=["recommendations"])
api_router.include_router(plants.router, prefix="", tags=["plants"])
api_router.include_router(climate.router, prefix="", tags=["climate"])
api_router.include_router(quantification.router, prefix="", tags=["quantification"])
api_router.include_router(admin.router, prefix="", tags=["admin"])  # admin router already has /admin prefix
api_router.include_router(markdown_content.router, prefix="", tags=["markdown-content"])
api_router.include_router(uhi.router, prefix="/uhi", tags=["uhi"])
api_router.include_router(plant_tracking.router, prefix="", tags=["plant-tracking"])
api_router.include_router(plant_chat.router, prefix="", tags=["plant-chat"])