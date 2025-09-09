import os
import base64
from typing import Optional


def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string with data URI scheme or empty string if error
    """
    try:
        if not image_path or not os.path.exists(image_path):
            return ""
        
        with open(image_path, "rb") as image_file:
            # Read image and encode to base64
            image_data = image_file.read()
            base64_string = base64.b64encode(image_data).decode('utf-8')
            
            # Determine MIME type based on file extension
            file_ext = os.path.splitext(image_path)[1].lower()
            mime_type = get_mime_type(file_ext)
            
            return f"data:{mime_type};base64,{base64_string}"
    except Exception as e:
        print(f"Error converting image {image_path} to base64: {e}")
        return ""


def get_mime_type(file_extension: str) -> str:
    """Get MIME type from file extension.
    
    Args:
        file_extension: File extension (e.g., '.jpg', '.png')
        
    Returns:
        MIME type string
    """
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml'
    }
    return mime_types.get(file_extension.lower(), 'image/jpeg')


def validate_image_path(image_path: str, base_dirs: Optional[list] = None) -> bool:
    """Validate that an image path exists and is in allowed directories.
    
    Args:
        image_path: Path to validate
        base_dirs: List of allowed base directories (optional)
        
    Returns:
        True if path is valid, False otherwise
    """
    if not image_path or not os.path.exists(image_path):
        return False
    
    if base_dirs:
        # Check if path is within allowed directories
        abs_path = os.path.abspath(image_path)
        for base_dir in base_dirs:
            if abs_path.startswith(os.path.abspath(base_dir)):
                return True
        return False
    
    return True