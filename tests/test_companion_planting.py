"""
Test script to verify companion planting data is included in recommendations API response.
"""
import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.recommendation_service import RecommendationService
from app.repositories.database_plant_repository import DatabasePlantRepository
from app.repositories.climate_repository import ClimateRepository
from app.schemas.request import (
    RecommendationRequest, UserRequest, SitePreferences,
    UserPreferences, PracticalPreferences, EnvironmentPreferences
)
from app.core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession


async def test_companion_planting_data():
    """Test that companion planting data is included in recommendations."""
    print("=" * 80)
    print("TESTING COMPANION PLANTING DATA IN RECOMMENDATIONS")
    print("=" * 80)

    # Get database session
    async for db in get_async_db():
        try:
            # Initialize repositories and service
            plant_repository = DatabasePlantRepository(db)
            climate_repository = ClimateRepository(db)
            recommendation_service = RecommendationService(plant_repository, climate_repository)

            # Create a test recommendation request
            request = RecommendationRequest(
                suburb="Richmond",
                climate_zone="temperate",
                n=5,
                user_preferences=UserRequest(
                    user_id="test_user",
                    site=SitePreferences(
                        location_type="backyard",
                        area_m2=10.0,
                        sun_exposure="full_sun",
                        wind_exposure="moderate",
                        containers=False
                    ),
                    preferences=UserPreferences(
                        goal="mixed",
                        edible_types=["herbs", "leafy"],
                        ornamental_types=["flowers"],
                        colors=["purple", "white"],
                        fragrant=True,
                        maintainability="low",
                        watering="medium",
                        time_to_results="quick"
                    ),
                    practical=PracticalPreferences(
                        budget="medium",
                        has_basic_tools=True,
                        organic_only=False
                    ),
                    environment=EnvironmentPreferences(
                        climate_zone="temperate",
                        temperature_c=18.0,
                        humidity_pct=70
                    )
                )
            )

            print("\nGenerating recommendations...")
            print(f"Suburb: {request.suburb}")
            print(f"Climate Zone: {request.climate_zone}")
            print(f"Number of recommendations: {request.n}")
            print()

            # Generate recommendations
            recommendations = await recommendation_service.generate_recommendations(request)

            print(f"\n✅ Successfully generated {len(recommendations.get('recommendations', []))} recommendations")
            print("-" * 80)

            # Check each recommendation for companion planting data
            all_have_companion_data = True
            for i, rec in enumerate(recommendations.get("recommendations", []), 1):
                plant_name = rec.get("plant_name", "Unknown")
                scientific_name = rec.get("scientific_name", "Unknown")

                # Check for companion planting fields
                has_beneficial = "beneficial_companions" in rec
                has_harmful = "harmful_companions" in rec
                has_neutral = "neutral_companions" in rec

                beneficial = rec.get("beneficial_companions", "")
                harmful = rec.get("harmful_companions", "")
                neutral = rec.get("neutral_companions", "")

                print(f"\n{i}. {plant_name} ({scientific_name})")
                print(f"   Plant ID: {rec.get('id', 'N/A')}")
                print(f"   Score: {rec.get('score', 0)}")

                if has_beneficial and has_harmful and has_neutral:
                    print(f"   ✅ Companion planting data fields present")
                    print(f"      Beneficial: {beneficial if beneficial else 'None'}")
                    print(f"      Harmful: {harmful if harmful else 'None'}")
                    print(f"      Neutral: {neutral if neutral else 'None'}")
                else:
                    print(f"   ❌ Missing companion planting data fields!")
                    all_have_companion_data = False
                    if not has_beneficial:
                        print(f"      Missing: beneficial_companions")
                    if not has_harmful:
                        print(f"      Missing: harmful_companions")
                    if not has_neutral:
                        print(f"      Missing: neutral_companions")

            print("\n" + "=" * 80)
            if all_have_companion_data:
                print("✅ TEST PASSED: All recommendations include companion planting data!")
            else:
                print("❌ TEST FAILED: Some recommendations missing companion planting data")
            print("=" * 80)

            return all_have_companion_data

        except Exception as e:
            print(f"\n❌ Error during test: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            break  # Exit the async generator


if __name__ == "__main__":
    result = asyncio.run(test_companion_planting_data())
    sys.exit(0 if result else 1)
