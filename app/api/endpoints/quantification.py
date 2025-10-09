from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.request import PlantQuantificationRequest
from app.schemas.response import PlantQuantificationResponse, QuantifiedImpactResponse, SuitabilityScoreResponse
from app.services.quantification_service import QuantificationService
from app.repositories.database_plant_repository import DatabasePlantRepository
from app.repositories.climate_repository import ClimateRepository
from app.core.database import get_async_db

router = APIRouter(tags=["quantification"])


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


async def get_quantification_service() -> QuantificationService:
    """Get quantification service instance"""
    return QuantificationService()


@router.post("/quantify-plant", response_model=PlantQuantificationResponse)
async def quantify_plant_impact(
    request: PlantQuantificationRequest,
    plant_repository: DatabasePlantRepository = Depends(get_plant_repository),
    climate_repository: ClimateRepository = Depends(get_climate_repository),
    quantification_service: QuantificationService = Depends(get_quantification_service)
):
    """
    Quantify the climate action impact of a specific plant

    This endpoint calculates the environmental impact of a plant including:
    - Temperature reduction (cooling effect)
    - Air quality improvement points
    - CO2 absorption capacity
    - Water processing/cycling
    - Pollinator support level
    - Edible yield (if applicable)
    - Maintenance and water requirements
    - Risk assessment
    - Confidence level
    - Community impact potential
    """
    try:
        # Get plant data
        plant = await plant_repository.get_plant_object_by_name(request.plant_name)
        if not plant:
            raise HTTPException(
                status_code=404,
                detail=f"Plant '{request.plant_name}' not found"
            )

        # Get suburb data for UHI context
        suburb = await climate_repository.get_suburb_by_name(request.suburb)
        if not suburb:
            # Use default suburb data if not found - create a simple object with required attributes
            class DefaultSuburb:
                def __init__(self, name):
                    self.name = name
                    self.suburb_heat_category = "Moderate Heat"
                    self.suburb_heat_intensity = 8.0

            suburb = DefaultSuburb(request.suburb)

        # Extract preferences
        site_prefs = request.user_preferences.site
        user_prefs = request.user_preferences.preferences

        # Quantify plant impact
        quantified_impact = quantification_service.quantify_plant_impact(
            plant=plant,
            site=site_prefs,
            preferences=user_prefs,
            suburb=suburb,
            plant_count=request.plant_count
        )

        # Calculate suitability score
        from app.services.quantification_service import ImpactMetrics

        # Convert quantified impact back to raw metrics for suitability calculation
        raw_metrics = ImpactMetrics(
            cooling_index=75.0,  # Estimated from quantified impact
            air_quality_improvement=quantified_impact.air_quality_points * 100 / 15,
            co2_uptake_kg_year=quantified_impact.co2_absorption_kg_year / request.plant_count,
            water_cycling_l_week=quantified_impact.water_processed_l_week / request.plant_count,
            biodiversity_score=80.0 if quantified_impact.pollinator_support == "High" else
                             60.0 if quantified_impact.pollinator_support == "Medium" else
                             40.0 if quantified_impact.pollinator_support == "Low" else 20.0,
            edible_yield_g_week=50.0 if quantified_impact.edible_yield else None,
            water_need_l_week=float(quantified_impact.water_requirement.split('L/week')[0]),
            maintenance_mins_week=float(quantified_impact.maintenance_time.split('mins/week')[0]),
            risk_level=quantified_impact.risk_badge,
            confidence_score=80.0  # Default confidence
        )

        suitability = quantification_service._calculate_suitability_score(raw_metrics, user_prefs)

        # Determine climate zone
        climate_zone = request.climate_zone or "temperate"

        # Build response
        return PlantQuantificationResponse(
            plant_name=plant.plant_name,
            scientific_name=plant.scientific_name,
            plant_category=plant.plant_category,
            quantified_impact=QuantifiedImpactResponse(
                temperature_reduction_c=quantified_impact.temperature_reduction_c,
                air_quality_points=quantified_impact.air_quality_points,
                co2_absorption_kg_year=quantified_impact.co2_absorption_kg_year,
                water_processed_l_week=quantified_impact.water_processed_l_week,
                pollinator_support=quantified_impact.pollinator_support,
                edible_yield=quantified_impact.edible_yield,
                maintenance_time=quantified_impact.maintenance_time,
                water_requirement=quantified_impact.water_requirement,
                risk_badge=quantified_impact.risk_badge,
                confidence_level=quantified_impact.confidence_level,
                why_this_plant=quantified_impact.why_this_plant,
                community_impact_potential=quantified_impact.community_impact_potential
            ),
            suitability_score=SuitabilityScoreResponse(
                total_score=suitability.total_score,
                breakdown=suitability.breakdown
            ),
            suburb=request.suburb,
            climate_zone=climate_zone,
            plant_count=request.plant_count
        )

    except Exception as e:
        import traceback
        print(f"Error in quantification endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing quantification request: {str(e)}"
        )


@router.post("/batch-quantify", response_model=List[PlantQuantificationResponse])
async def batch_quantify_plants(
    requests: List[PlantQuantificationRequest],
    plant_repository: DatabasePlantRepository = Depends(get_plant_repository),
    climate_repository: ClimateRepository = Depends(get_climate_repository),
    quantification_service: QuantificationService = Depends(get_quantification_service)
):
    """
    Quantify the climate action impact of multiple plants in batch

    This endpoint allows bulk quantification of plants for comparison purposes.
    Useful for analyzing multiple plant options against the same user preferences.
    """
    try:
        if len(requests) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 plants can be quantified in a single batch request"
            )

        results = []

        for request in requests:
            try:
                # Reuse single quantification logic
                result = await quantify_plant_impact(
                    request=request,
                    plant_repository=plant_repository,
                    climate_repository=climate_repository,
                    quantification_service=quantification_service
                )
                results.append(result)

            except HTTPException as e:
                # Skip plants that aren't found but continue with others
                if e.status_code == 404:
                    continue
                else:
                    raise e

        return results

    except Exception as e:
        import traceback
        print(f"Error in batch quantification endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing batch quantification request: {str(e)}"
        )


@router.get("/quantification-info")
async def get_quantification_info():
    """
    Get information about the quantification framework and methodology

    Returns details about how the climate impact metrics are calculated,
    what factors are considered, and confidence levels.
    """
    return {
        "framework_version": "1.0",
        "methodology": "Per-Plant Quantification Framework",
        "description": "Quantifies climate action impact of individual plants based on site context, plant biophysics, and user preferences",
        "metrics": {
            "cooling_effect": {
                "description": "Temperature reduction in nearby area (1-3m radius)",
                "unit": "degrees Celsius",
                "range": "0.1 - 2.0°C",
                "calculation": "Based on LAI, canopy area, transpiration class, and UHI context"
            },
            "air_quality": {
                "description": "Local air quality improvement potential",
                "unit": "AQ points",
                "range": "0 - 15 points",
                "calculation": "Based on leaf surface area, plant roughness, and aromatic properties"
            },
            "co2_absorption": {
                "description": "Annual CO2 uptake capacity",
                "unit": "kg per year",
                "range": "0.5 - 50 kg/year",
                "calculation": "Based on plant type, canopy area, growth speed, and sun exposure"
            },
            "water_cycling": {
                "description": "Weekly water processing through transpiration",
                "unit": "liters per week",
                "range": "1 - 50 L/week",
                "calculation": "Based on transpiration class, canopy area, and sun exposure"
            },
            "pollinator_support": {
                "description": "Support level for pollinators and biodiversity",
                "unit": "categorical",
                "range": "Minimal, Low, Medium, High",
                "calculation": "Based on flower presence, fragrance, bloom period, and native status"
            }
        },
        "factors_considered": [
            "Plant biophysics (LAI, canopy area, transpiration)",
            "Site context (area, sun, wind, containers)",
            "Urban Heat Island (UHI) effect",
            "Seasonal timing and plant maturity",
            "User preferences and maintenance capacity",
            "Risk assessment and safety considerations"
        ],
        "confidence_levels": {
            "high": "85-100% - Complete plant data available",
            "medium": "70-84% - Most plant data available, some estimation",
            "low": "50-69% - Limited plant data, significant estimation required"
        },
        "limitations": [
            "Estimates based on typical conditions and average plant performance",
            "Actual results may vary based on specific site microclimate",
            "Community impact projections are theoretical calculations",
            "Regular calibration with field measurements recommended"
        ]
    }