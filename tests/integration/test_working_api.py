import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    sys.path.append('./api')
    from services.google_drive_service import GoogleDriveImageService
    
    service = GoogleDriveImageService()
    
    print("TESTING GOOGLE DRIVE API - SIMPLE VERSION")
    print("=" * 50)
    
    # Test each category
    total_images = 0
    for category in ['flower', 'herb', 'vegetable']:
        print(f"\nTesting {category} category:")
        try:
            images = service.get_folder_files(category)
            image_count = len(images)
            total_images += image_count
            
            print(f"  Found: {image_count} images")
            
            if image_count > 0:
                # Show first few images
                for i, img in enumerate(images[:3]):
                    print(f"    {i+1}. {img['name'][:50]}...")
                    print(f"       URL: {img['url'][:60]}...")
                    
                if image_count > 3:
                    print(f"    ... and {image_count - 3} more images")
                    
                # Test image search
                first_image_name = images[0]['name'].split('.')[0]  # Remove extension
                found_image = service.get_image_by_name(category, first_image_name)
                if found_image:
                    print(f"  Image search works: Found match for '{first_image_name[:30]}...'")
            else:
                print(f"  No images found in {category}")
                
        except Exception as e:
            print(f"  Error testing {category}: {str(e)[:100]}")
    
    print(f"\n" + "="*50)
    print(f"SUMMARY:")
    print(f"Total images found across all categories: {total_images}")
    
    if total_images > 0:
        print("STATUS: SUCCESS! Google Drive API is working!")
        print("\nReady for:")
        print("1. Deploy to Vercel")
        print("2. Set environment variables in Vercel dashboard") 
        print("3. Test production deployment")
        
        # Test all images method
        print("\nTesting get_all_images method:")
        all_images = service.get_all_images()
        for category, images in all_images.items():
            print(f"  {category}: {len(images)} images")
            
    else:
        print("STATUS: No images found - check folder structure")
        
except Exception as e:
    print(f"Test failed: {e}")
    print("Check that the google_drive_service.py file was updated correctly")