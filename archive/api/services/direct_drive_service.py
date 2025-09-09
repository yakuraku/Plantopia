import os
import requests
from typing import Dict, List, Optional

class DirectDriveImageService:
    """Direct Google Drive access using public folder sharing (backup method)"""
    
    def __init__(self):
        self.folder_ids = {
            'flower': os.getenv('GOOGLE_DRIVE_FOLDER_FLOWER'),
            'herb': os.getenv('GOOGLE_DRIVE_FOLDER_HERB'), 
            'vegetable': os.getenv('GOOGLE_DRIVE_FOLDER_VEGETABLE')
        }
    
    def get_direct_folder_url(self, category: str) -> str:
        """Get direct Google Drive folder URL for embedding"""
        folder_id = self.folder_ids.get(category.lower())
        if not folder_id:
            return None
            
        # Direct folder embed URL (shows folder contents)
        return f"https://drive.google.com/embeddedfolderview?id={folder_id}#grid"
    
    def get_folder_view_url(self, category: str) -> str:
        """Get folder view URL for manual access"""
        folder_id = self.folder_ids.get(category.lower())
        if not folder_id:
            return None
            
        return f"https://drive.google.com/drive/folders/{folder_id}"
    
    def get_sample_images(self, category: str) -> List[Dict]:
        """Return sample image structure for testing"""
        folder_id = self.folder_ids.get(category.lower())
        if not folder_id:
            return []
            
        # Return sample structure - in production, you would manually map file IDs
        return [
            {
                'id': 'SAMPLE_FILE_ID_1',
                'name': f'sample_{category}_1.jpg',
                'url': f"https://drive.google.com/uc?export=view&id=SAMPLE_FILE_ID_1",
                'category': category,
                'note': 'Replace with actual file ID'
            },
            {
                'id': 'SAMPLE_FILE_ID_2', 
                'name': f'sample_{category}_2.jpg',
                'url': f"https://drive.google.com/uc?export=view&id=SAMPLE_FILE_ID_2",
                'category': category,
                'note': 'Replace with actual file ID'
            }
        ]
    
    def test_folder_access(self) -> Dict[str, bool]:
        """Test if folders are publicly accessible"""
        results = {}
        
        for category, folder_id in self.folder_ids.items():
            if folder_id:
                # Test folder access
                url = f"https://drive.google.com/drive/folders/{folder_id}"
                try:
                    response = requests.head(url, timeout=10)
                    results[category] = response.status_code == 200
                    print(f"{category}: {'Accessible' if results[category] else 'Not accessible'}")
                except Exception as e:
                    print(f"{category}: Error - {e}")
                    results[category] = False
            else:
                results[category] = False
                
        return results
    
    def get_sharing_instructions(self) -> Dict[str, str]:
        """Get instructions for sharing each folder"""
        instructions = {}
        
        for category, folder_id in self.folder_ids.items():
            if folder_id:
                instructions[category] = {
                    'folder_url': f"https://drive.google.com/drive/folders/{folder_id}",
                    'steps': [
                        "1. Open the folder URL above",
                        "2. Right-click in the folder and select 'Share'",
                        "3. Click 'Change to anyone with the link'",
                        "4. Set permission to 'Viewer'", 
                        "5. Click 'Done' and wait 5-10 minutes"
                    ]
                }
        
        return instructions

# Create global instance for testing
direct_drive_service = DirectDriveImageService()