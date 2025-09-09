import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key():
    """Test if API key is valid"""
    api_key = os.getenv('GOOGLE_DRIVE_API_KEY')
    
    if not api_key:
        print("X API key not found in environment variables")
        return False
        
    print(f"Testing API key: {api_key[:20]}...")
    
    # Test with a folder metadata call (this should work)
    folder_id = "1ZcE9R3FMvZa5TRp8HfAHo-K7dAD5IfmL"
    url = f"https://www.googleapis.com/drive/v3/files/{folder_id}"
    params = {
        'key': api_key,
        'fields': 'id,name,permissions'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API key works - can access folder: {data.get('name')}")
            return True
        else:
            print(f"X API key test failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"X API key test error: {e}")
        return False

def test_folder_access():
    """Test folder access permissions"""
    api_key = os.getenv('GOOGLE_DRIVE_API_KEY')
    folder_ids = {
        'flower': os.getenv('GOOGLE_DRIVE_FOLDER_FLOWER'),
        'herb': os.getenv('GOOGLE_DRIVE_FOLDER_HERB'), 
        'vegetable': os.getenv('GOOGLE_DRIVE_FOLDER_VEGETABLE')
    }
    
    print("\nTesting folder access permissions...")
    
    results = {}
    for category, folder_id in folder_ids.items():
        if not folder_id:
            print(f"X {category}: No folder ID configured")
            results[category] = False
            continue
            
        # Test files listing (this is what's failing)
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            'key': api_key,
            'q': f"parents in '{folder_id}'",
            'fields': 'files(id,name)',
            'pageSize': 5
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                file_count = len(data.get('files', []))
                print(f"✓ {category}: Can list files ({file_count} found)")
                results[category] = True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"X {category}: Cannot list files - {response.status_code}: {error_message}")
                results[category] = False
        except Exception as e:
            print(f"X {category}: Error testing folder - {e}")
            results[category] = False
    
    return results

def test_direct_folder_urls():
    """Test if folders are publicly accessible via direct URLs"""
    folder_ids = {
        'flower': os.getenv('GOOGLE_DRIVE_FOLDER_FLOWER'),
        'herb': os.getenv('GOOGLE_DRIVE_FOLDER_HERB'), 
        'vegetable': os.getenv('GOOGLE_DRIVE_FOLDER_VEGETABLE')
    }
    
    print("\nTesting direct folder URL access...")
    
    for category, folder_id in folder_ids.items():
        if folder_id:
            url = f"https://drive.google.com/drive/folders/{folder_id}"
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    print(f"✓ {category}: Folder is publicly accessible")
                    print(f"  URL: {url}")
                else:
                    print(f"X {category}: Folder not publicly accessible (status: {response.status_code})")
            except Exception as e:
                print(f"X {category}: Error accessing folder - {e}")

def print_fix_instructions(api_works, folder_results):
    """Print specific fix instructions based on test results"""
    print("\n" + "="*60)
    print("DIAGNOSIS & FIX INSTRUCTIONS")
    print("="*60)
    
    if not api_works:
        print("\n🔧 FIX 1: API Key Issues")
        print("- Check that your API key is correct in .env file")
        print("- Go to Google Cloud Console > APIs & Services > Credentials") 
        print("- Verify the API key exists and is enabled")
        print("- Make sure Google Drive API is enabled in your project")
        return
    
    if not any(folder_results.values()):
        print("\n🔧 FIX 2: Folder Permission Issues")
        print("The API key works but cannot access folder contents.")
        print("This means folders are not properly shared.")
        print("\nSTEPS TO FIX:")
        print("1. Open Google Drive in your browser")
        print("2. For each folder, right-click and select 'Share'")
        print("3. Click 'Change to anyone with the link'") 
        print("4. Set permission to 'Viewer'")
        print("5. Click 'Copy link' and test in incognito browser")
        print("\nFolder URLs to test:")
        
        folder_ids = {
            'flower': os.getenv('GOOGLE_DRIVE_FOLDER_FLOWER'),
            'herb': os.getenv('GOOGLE_DRIVE_FOLDER_HERB'), 
            'vegetable': os.getenv('GOOGLE_DRIVE_FOLDER_VEGETABLE')
        }
        
        for category, folder_id in folder_ids.items():
            if folder_id:
                print(f"  {category}: https://drive.google.com/drive/folders/{folder_id}")
        
        print("\nAfter sharing, wait 5-10 minutes and run test again.")
    else:
        print("\n✓ All tests passed! Your Google Drive integration should work.")

def main():
    print("Google Drive API Diagnostic Tool")
    print("="*40)
    
    # Test 1: API Key
    api_works = test_api_key()
    
    # Test 2: Folder Access
    folder_results = test_folder_access()
    
    # Test 3: Direct URLs
    test_direct_folder_urls()
    
    # Print fix instructions
    print_fix_instructions(api_works, folder_results)
    
    print(f"\n📋 Summary:")
    print(f"API Key Valid: {'Yes' if api_works else 'No'}")
    for category, works in folder_results.items():
        print(f"{category.title()} Folder Access: {'Yes' if works else 'No'}")

if __name__ == "__main__":
    main()