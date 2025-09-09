import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    # Test direct drive service
    sys.path.append('./api')
    from services.direct_drive_service import DirectDriveImageService
    
    service = DirectDriveImageService()
    
    print("Testing Direct Drive Access...")
    print("=" * 40)
    
    # Test folder accessibility
    print("\n1. Testing folder accessibility:")
    access_results = service.test_folder_access()
    
    print("\n2. Folder URLs for manual testing:")
    sharing_instructions = service.get_sharing_instructions()
    
    for category, info in sharing_instructions.items():
        print(f"\n{category.upper()} FOLDER:")
        print(f"  URL: {info['folder_url']}")
        if not access_results.get(category, False):
            print("  STATUS: Needs sharing setup")
            print("  STEPS:")
            for step in info['steps']:
                print(f"    {step}")
        else:
            print("  STATUS: Accessible")
    
    print("\n3. Sample image structure:")
    for category in ['flower', 'herb', 'vegetable']:
        sample_images = service.get_sample_images(category)
        print(f"\n{category}: {len(sample_images)} sample images")
        for img in sample_images:
            print(f"  - {img['name']}")
    
    print("\n" + "="*50)
    print("NEXT STEPS:")
    print("="*50)
    print("1. Open each folder URL in an incognito browser")
    print("2. If you can see folder contents: folders are shared correctly")
    print("3. If you get permission denied: follow sharing steps above")
    print("4. After sharing, wait 5-10 minutes and test API again")
    print("5. Alternative: Use manual file ID mapping for specific images")
    
except Exception as e:
    print(f"Test failed: {e}")
    print("Make sure direct_drive_service.py was created correctly")