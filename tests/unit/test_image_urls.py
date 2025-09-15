"""
Test script to verify GCS image URL generation
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.services.plant_service import PlantService
from app.core.config import settings


def test_image_url_generation():
    """Test generating GCS image URLs"""

    # Create a plant service instance (no db needed for URL generation)
    plant_service = PlantService(None)

    print(f"GCS Bucket URL: {settings.GCS_BUCKET_URL}")
    print("-" * 50)

    # Test cases matching the actual GCS structure
    test_plants = [
        ("Alyssum- Royal Carpet", "flower", "Lobularia maritima"),
        ("Basil- Cinnamon", "herb", "Ocimum basilicum"),
        ("Basil- Bush", "herb", "unknown"),
        ("Agave- Foxtail", "flower", "Agave attentuata"),
    ]

    for plant_name, category, scientific_name in test_plants:
        print(f"\nPlant: {plant_name}")
        print(f"Category: {category}")
        print(f"Scientific Name: {scientific_name}")

        # Get primary image URL
        primary_url = plant_service.get_primary_image_url(plant_name, category, scientific_name)
        print(f"Primary Image URL: {primary_url}")

        # Get all image URLs
        all_urls = plant_service.generate_gcs_image_urls(plant_name, category, scientific_name)
        print(f"All Image URLs ({len(all_urls)}):")
        for i, url in enumerate(all_urls, 1):
            print(f"  Image {i}: {url}")


async def test_api_endpoints():
    """Test the API endpoints (requires running server)"""
    try:
        import httpx

        base_url = "http://localhost:8000/api/v1"

        async with httpx.AsyncClient() as client:
            # Test getting a plant's image URL (assuming plant ID 1 exists)
            response = await client.get(f"{base_url}/plants/1/image-url")
            if response.status_code == 200:
                print("\nAPI Test - Single Image URL:")
                print(response.json())
            else:
                print(f"Error: {response.status_code} - {response.text}")

            # Test getting all image URLs
            response = await client.get(f"{base_url}/plants/1/all-images")
            if response.status_code == 200:
                print("\nAPI Test - All Image URLs:")
                print(response.json())
            else:
                print(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"\nAPI test failed (is the server running?): {e}")


def main():
    """Main test function"""
    print("=" * 60)
    print("Testing GCS Image URL Generation")
    print("=" * 60)

    # Test URL generation
    test_image_url_generation()

    # Optionally test API endpoints
    print("\n" + "=" * 60)
    print("Testing API Endpoints")
    print("=" * 60)
    print("\nNote: Start the backend server first for API tests")
    user_input = input("Test API endpoints? (y/n): ")

    if user_input.lower() == 'y':
        asyncio.run(test_api_endpoints())

    print("\nTest complete!")


if __name__ == "__main__":
    main()