import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    sys.path.append('./api')
    from services.google_drive_service import GoogleDriveImageService
    
    service = GoogleDriveImageService()
    
    print("QUICK API TEST")
    print("=" * 30)
    
    # Test just flower category with limited results
    print("Testing flower category (limited results)...")
    images = service.get_folder_files('flower')
    
    print(f"Found {len(images)} images")
    
    if len(images) > 0:
        print("\nFirst few images:")
        for i, img in enumerate(images[:3]):
            print(f"  {i+1}. {img['name'][:40]}...")
            print(f"      URL: {img['url'][:50]}...")
        
        print(f"\nSUCCESS! Google Drive API is working!")
        print(f"Ready to deploy to Vercel!")
        
        # Quick test of other categories
        herb_count = len(service.get_folder_files('herb'))
        veg_count = len(service.get_folder_files('vegetable'))
        
        print(f"\nQuick counts:")
        print(f"  Flowers: {len(images)}")  
        print(f"  Herbs: {herb_count}")
        print(f"  Vegetables: {veg_count}")
        
    else:
        print("No images found - check setup")
        
except Exception as e:
    print(f"Error: {e}")