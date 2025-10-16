from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.request import RecommendationRequest, PlantScoreRequest
from app.schemas.response import PlantScoreResponse
from app.services.recommendation_service import RecommendationService
from app.services.quantification_service import QuantificationService
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


@router.post("/recommendations-with-impact")
async def get_recommendations_with_quantified_impact(
    request: RecommendationRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Generate plant recommendations with quantified climate impact

    This endpoint extends the standard recommendations endpoint by adding
    quantified climate impact metrics to each recommended plant, including:
    - Temperature reduction (cooling effect)
    - Air quality improvement points
    - CO2 absorption capacity
    - Water processing/cycling
    - Pollinator support level
    - Edible yield (if applicable)
    - Maintenance and water requirements
    - Risk assessment and confidence level
    """
    try:
        # Get standard recommendations
        recommendations = await recommendation_service.generate_recommendations(request)

        # Add quantified impact to each recommendation
        enhanced_recommendations = []

        for rec in recommendations.get("recommendations", []):
            try:
                # Get plant from database
                plant = await recommendation_service.plant_repository.get_plant_object_by_name(rec["plant_name"])
                if not plant:
                    # Skip if plant not found, use original recommendation
                    enhanced_recommendations.append(rec)
                    continue

                # Get suburb data
                suburb = await recommendation_service.climate_repository.get_suburb_by_name(request.suburb)
                if not suburb:
                    # Use default suburb data if not found
                    from app.models.database import Suburb
                    suburb = Suburb(
                        suburb_name=request.suburb,
                        suburb_heat_category="Moderate Heat",
                        avg_heat_celsius=8.0,
                        avg_vegetation_pct=20.0
                    )

                # Quantify impact
                quantified_impact = recommendation_service.quantification_service.quantify_plant_impact(
                    plant=plant,
                    site=request.user_preferences.site,
                    preferences=request.user_preferences.preferences,
                    suburb=suburb,
                    plant_count=1
                )

                # Create enhanced recommendation
                enhanced_rec = rec.copy()
                enhanced_rec["quantified_impact"] = {
                    "temperature_reduction_c": quantified_impact.temperature_reduction_c,
                    "air_quality_points": quantified_impact.air_quality_points,
                    "co2_absorption_g_year": quantified_impact.co2_absorption_g_year,  # Fixed: now in grams
                    "water_processed_l_week": quantified_impact.water_processed_l_week,
                    "pollinator_support": quantified_impact.pollinator_support,
                    "edible_yield": quantified_impact.edible_yield,
                    "maintenance_time": quantified_impact.maintenance_time,
                    "water_requirement": quantified_impact.water_requirement,
                    "risk_badge": quantified_impact.risk_badge,
                    "confidence_level": quantified_impact.confidence_level,
                    "why_this_plant": quantified_impact.why_this_plant,
                    "community_impact_potential": quantified_impact.community_impact_potential
                }

                # Add companion planting data from plant object
                enhanced_rec["beneficial_companions"] = plant.beneficial_companions or ""
                enhanced_rec["harmful_companions"] = plant.harmful_companions or ""
                enhanced_rec["neutral_companions"] = plant.neutral_companions or ""

                enhanced_recommendations.append(enhanced_rec)

            except Exception as e:
                # If quantification fails for a plant, use original recommendation
                print(f"Warning: Failed to quantify impact for {rec['plant_name']}: {str(e)}")
                enhanced_recommendations.append(rec)

        # Update recommendations in response
        recommendations["recommendations"] = enhanced_recommendations

        return recommendations

    except Exception as e:
        import traceback
        print(f"Error in enhanced recommendations endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")