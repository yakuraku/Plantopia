import os
import requests
from typing import Dict, List, Optional, Tuple
import json
from urllib.parse import quote

class GoogleDriveImageService:
    """Secure Google Drive image service with API key from environment"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_DRIVE_API_KEY')
        self.folder_ids = {
            'flower': os.getenv('GOOGLE_DRIVE_FOLDER_FLOWER'),
            'herb': os.getenv('GOOGLE_DRIVE_FOLDER_HERB'), 
            'vegetable': os.getenv('GOOGLE_DRIVE_FOLDER_VEGETABLE')
        }
        
        if not self.api_key:
            print("⚠️  WARNING: GOOGLE_DRIVE_API_KEY not found in environment variables")
        
        # Validate folder IDs
        for category, folder_id in self.folder_ids.items():
            if not folder_id:
                print(f"⚠️  WARNING: Missing folder ID for {category}")
    
    def get_folder_files(self, category: str) -> List[Dict]:
        """
        Get list of image files in a specific category folder
        
        Args:
            category: Plant category (flower, herb, vegetable)
            
        Returns:
            List of file dictionaries with id, name, and URL
        """
        if not self.api_key:
            return []
            
        folder_id = self.folder_ids.get(category.lower())
        if not folder_id:
            print(f"No folder ID found for category: {category}")
            return []
        
        # Google Drive API endpoint to list files in folder
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            'key': self.api_key,
            'q': f"'{folder_id}' in parents",
            'fields': 'files(id,name,mimeType,size)',
            'pageSize': 20  # Limit for faster testing
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            files = data.get('files', [])
            
            # Transform to our format - handle both direct images and nested folders
            image_files = []
            for file in files:
                mime_type = file.get('mimeType', '')
                
                if 'image/' in mime_type:
                    # Direct image file
                    image_files.append({
                        'id': file['id'],
                        'name': file['name'],
                        'url': f"https://drive.google.com/uc?export=view&id={file['id']}",
                        'size': file.get('size', 0),
                        'category': category,
                        'type': 'image'
                    })
                elif mime_type == 'application/vnd.google-apps.folder':
                    # Subfolder - need to look inside for images
                    subfolder_images = self._get_images_from_subfolder(file['id'], category)
                    image_files.extend(subfolder_images)
            
            print(f"Found {len(image_files)} images in {category} folder")
            return image_files
            
        except requests.RequestException as e:
            print(f"Error fetching files from Google Drive: {e}")
            return []
    
    def _get_images_from_subfolder(self, subfolder_id: str, category: str) -> List[Dict]:
        """Get images from a subfolder"""
        if not self.api_key:
            return []
            
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            'key': self.api_key,
            'q': f"'{subfolder_id}' in parents and mimeType contains 'image/'",
            'fields': 'files(id,name,mimeType,size)',
            'pageSize': 3  # Limit per subfolder for faster testing
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            files = data.get('files', [])
            
            subfolder_images = []
            for file in files:
                subfolder_images.append({
                    'id': file['id'],
                    'name': file['name'],
                    'url': f"https://drive.google.com/uc?export=view&id={file['id']}",
                    'size': file.get('size', 0),
                    'category': category,
                    'type': 'image',
                    'subfolder_id': subfolder_id
                })
            
            return subfolder_images
            
        except requests.RequestException as e:
            print(f"Error fetching images from subfolder {subfolder_id}: {e}")
            return []
    
    def get_image_by_name(self, category: str, image_name: str) -> Optional[str]:
        """
        Get specific image URL by name and category
        
        Args:
            category: Plant category
            image_name: Exact filename to search for
            
        Returns:
            Google Drive URL for the specific image, or None if not found
        """
        files = self.get_folder_files(category)
        
        for file in files:
            if file['name'].lower() == image_name.lower():
                return file['url']
        
        # Try partial name matching if exact match fails
        for file in files:
            if image_name.lower() in file['name'].lower():
                return file['url']
                
        print(f"Image not found: {image_name} in category {category}")
        return None
    
    def get_all_images(self) -> Dict[str, List[Dict]]:
        """Get all images organized by category"""
        all_images = {}
        
        for category in self.folder_ids.keys():
            if self.folder_ids[category]:  # Only if folder ID exists
                all_images[category] = self.get_folder_files(category)
        
        return all_images
    
    def test_connection(self) -> bool:
        """Test if Google Drive API is working"""
        if not self.api_key:
            print("❌ No API key found")
            return False
            
        try:
            # Test with one folder
            test_category = 'flower'
            files = self.get_folder_files(test_category)
            print(f"✅ Google Drive API test successful - found {len(files)} files")
            return True
        except Exception as e:
            print(f"❌ Google Drive API test failed: {e}")
            return False

# Create global instance
drive_service = GoogleDriveImageService()