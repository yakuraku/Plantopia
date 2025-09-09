#!/usr/bin/env python3
"""
Startup script for Plantopia backend server.
This script ensures proper module imports by setting up the Python path correctly.
"""

import sys
import os

# Add the current directory to Python path so 'app' module can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    # Run the FastAPI application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )