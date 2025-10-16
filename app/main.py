from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import Response

from app.core.config import settings
from app.api.endpoints import api_router
from app.core.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    await init_db()
    print("Database initialized")
    yield
    # Shutdown
    await close_db()
    print("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan
)

# Add GZip compression for responses > 1KB (60-80% size reduction)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses larger than 1KB
    compresslevel=6  # Balance between speed and compression ratio
)

# Smart CORS handling with dynamic origin checking
@app.middleware("http")
async def smart_cors_middleware(request: Request, call_next):
    # Handle preflight OPTIONS requests first
    if request.method == "OPTIONS":
        origin = request.headers.get("origin")

        # Check if origin is in allowed list
        if origin and (origin in settings.BACKEND_CORS_ORIGINS or "*" in settings.BACKEND_CORS_ORIGINS):
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": origin,  # Return specific origin, not wildcard
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                    "Access-Control-Max-Age": "86400",  # Cache preflight for 24 hours
                }
            )
        return Response(status_code=200)

    # Process the actual request
    response = await call_next(request)

    # Only add CORS headers if not already present
    if "access-control-allow-origin" not in response.headers:
        origin = request.headers.get("origin")

        # Dynamic origin checking - return the specific origin that requested, not wildcard
        if origin and (origin in settings.BACKEND_CORS_ORIGINS or "*" in settings.BACKEND_CORS_ORIGINS):
            response.headers["Access-Control-Allow-Origin"] = origin  # Specific origin only
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"

    return response

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint (outside of versioned API)
@app.get("/")
async def root():
    return {"message": settings.PROJECT_NAME, "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)