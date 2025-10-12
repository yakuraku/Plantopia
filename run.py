#!/usr/bin/env python3
"""
Startup script for Plantopia backend server.
This script ensures proper module imports by setting up the Python path correctly.
"""

import sys
import os
import argparse

# Add the current directory to Python path so 'app' module can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Plantopia Backend Server")
    parser.add_argument(
        "--env",
        type=str,
        default=os.getenv("ENVIRONMENT", "production"),
        choices=["development", "production"],
        help="Environment mode (default: production)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (overrides environment setting)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload (overrides environment setting)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    import uvicorn
    from app.main import app

    args = parse_args()

    # Set environment variable
    os.environ["ENVIRONMENT"] = args.env

    # Determine reload setting
    # Priority: --no-reload > --reload > environment (development=True, production=False)
    if args.no_reload:
        reload = False
    elif args.reload:
        reload = True
    else:
        reload = (args.env == "development")

    # Get configuration
    host = args.host
    port = args.port

    print("\n" + "=" * 60)
    print("🌱 Plantopia Backend Server")
    print("=" * 60)
    print(f"🌍 Environment: {args.env}")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {'Enabled' if reload else 'Disabled'}")
    print("=" * 60 + "\n")

    # Run the FastAPI application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )