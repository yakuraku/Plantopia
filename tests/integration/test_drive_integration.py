import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the api directory to Python path  
api_path = os.path.join(os.path.dirname(__file__), 'api')
sys.path.append(api_path)

try:
    from services.google_drive_service import GoogleDriveImageService
    
    print("Testing Google Drive Integration...")
    
    # Create service instance
    service = GoogleDriveImageService()
    
    # Test connection
    if service.test_connection():
        print("✓ Google Drive API connection successful")
        
        # Test each category
        for category in ['flower', 'herb', 'vegetable']:
            print(f"\nTesting {category} category:")
            images = service.get_folder_files(category)
            
            if images:
                print(f"  Found {len(images)} images")
                # Show first few images
                for img in images[:3]:
                    print(f"  - {img['name']}: {img['url'][:50]}...")
            else:
                print(f"  No images found (check upload status)")
        
        # Test get_all_images method
        print(f"\nTesting get_all_images method:")
        all_images = service.get_all_images()
        total_images = sum(len(images) for images in all_images.values())
        print(f"  Total images across all categories: {total_images}")
        
        # Test specific image search
        print(f"\nTesting specific image search:")
        flower_image = service.get_image_by_name('flower', 'rose')
        if flower_image:
            print(f"  Found rose image: {flower_image[:50]}...")
        else:
            print("  No rose image found (will use first available)")
            
    else:
        print("X Google Drive API connection failed")
        print("Check your API key and folder IDs")
        
except ImportError as e:
    print(f"X Import error: {e}")
    print("Make sure the google_drive_service.py file was created correctly")
    print("Also ensure python-dotenv and requests are installed:")
    print("  pip install python-dotenv requests")
except Exception as e:
    print(f"X Test failed: {e}")

print("\nNext: If test passed, you're ready for deployment!")
print("If test failed, check your .env file and API key")