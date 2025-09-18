from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import json
import os
from pathlib import Path
from typing import Optional

router = APIRouter(tags=["uhi"])

# Base path for UHI data files - relative to project root
# Get the project root directory (where app/ folder is located)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # Go up from endpoints/uhi.py to project root
UHI_DATA_PATH = PROJECT_ROOT / "app" / "static" / "uhi"

# Essential endpoints for basic heatmap
@router.get("/boundaries")
async def get_suburb_boundaries(simplified: bool = True):
    """Get GeoJSON boundaries URL for map polygons - Essential for heatmap

    Args:
        simplified: If True, returns simplified (~726KB) version for faster loading.
                   If False, returns full detail (8.8MB) version.
    """
    base_url = "https://storage.googleapis.com/plantopia-images-1757656642/data/"

    if simplified:
        return {
            "url": f"{base_url}melbourne_suburbs_simplified.geojson",
            "size": "726KB",
            "description": "Simplified boundaries for fast loading"
        }
    else:
        return {
            "url": f"{base_url}melbourne_suburb_boundaries_with_heat.geojson",
            "size": "8.8MB",
            "description": "Full detail boundaries"
        }

@router.get("/data")
async def get_uhi_data():
    """Get heat intensity data to color the polygons - Essential for heatmap"""
    file_path = UHI_DATA_PATH / "melbourne_heat_data.json"

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"UHI data not found at {file_path.absolute()}"
        )

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Clean the data - replace infinity values with large numbers that JSON can handle
        # The original data has max values as 999 which might be causing issues
        import math

        def clean_json_data(obj):
            """Recursively clean JSON data to remove inf/nan values"""
            if isinstance(obj, dict):
                return {k: clean_json_data(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_json_data(item) for item in obj]
            elif isinstance(obj, float):
                if math.isinf(obj) or math.isnan(obj):
                    return None  # or return 0, or some default value
                return obj
            return obj

        # Clean the data
        cleaned_data = clean_json_data(data)

        # Alternative fix: Just return the data using JSONResponse which handles special values
        from fastapi.responses import JSONResponse
        import json as json_module

        # Use json.dumps with allow_nan=False to catch issues
        json_str = json_module.dumps(cleaned_data, allow_nan=False)
        return JSONResponse(content=json_module.loads(json_str))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

# Nice-to-have endpoints
@router.get("/suburb/{suburb_id}")
async def get_suburb_heat_data(suburb_id: str):
    """Get heat data for specific suburb when user clicks"""
    file_path = UHI_DATA_PATH / "melbourne_heat_data.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="UHI data not found")

    with open(file_path, 'r') as f:
        data = json.load(f)

    # Find suburb in data
    for suburb in data.get('suburbs', []):
        if suburb['id'] == suburb_id:
            return {
                "suburb": suburb,
                "heat_categories": data['heat_categories']
            }

    raise HTTPException(status_code=404, detail=f"Suburb {suburb_id} not found")

@router.get("/metadata")
async def get_metadata():
    """Get dataset metadata and heat categories for legend display"""
    file_path = UHI_DATA_PATH / "melbourne_heat_data.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="UHI data not found")

    with open(file_path, 'r') as f:
        data = json.load(f)

    return {
        "metadata": data.get('metadata', {}),
        "statistics": data.get('statistics', {}),
        "heat_categories": data.get('heat_categories', {})
    }

# Optional endpoints for additional features
@router.get("/suburbs/search")
async def search_suburbs(q: str, limit: int = 10):
    """Search suburbs by name for search bar feature"""
    file_path = UHI_DATA_PATH / "melbourne_heat_data.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="UHI data not found")

    with open(file_path, 'r') as f:
        data = json.load(f)

    query = q.lower()
    suburbs = data.get('suburbs', [])

    # Filter suburbs matching query
    matching = [s for s in suburbs if query in s['name'].lower()]

    # Sort by name relevance (exact match first)
    matching.sort(key=lambda x: (not x['name'].lower().startswith(query), x['name']))

    # Apply limit
    matching = matching[:limit]

    return {
        "suburbs": matching,
        "total": len(matching),
        "query": q
    }

@router.get("/suburbs/by-heat")
async def get_suburbs_by_heat(
    category: Optional[str] = None,
    limit: int = 10
):
    """Get suburbs sorted by heat intensity for 'Top 10 Hottest' list"""
    file_path = UHI_DATA_PATH / "melbourne_heat_data.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="UHI data not found")

    with open(file_path, 'r') as f:
        data = json.load(f)

    suburbs = data.get('suburbs', [])

    # Filter by category if specified
    if category:
        suburbs = [s for s in suburbs if s['heat']['category'].lower() == category.lower()]

    # Sort by heat intensity
    suburbs.sort(key=lambda x: x['heat']['intensity'], reverse=True)

    # Apply limit
    suburbs = suburbs[:limit]

    return {
        "suburbs": suburbs,
        "total": len(suburbs),
        "filter": {"category": category} if category else None
    }

@router.get("/summary")
async def get_heat_summary():
    """Get heat category summary statistics for dashboard"""
    file_path = UHI_DATA_PATH / "heat_category_summary.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Summary data not found")

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        headers={"Cache-Control": "public, max-age=86400"}
    )

@router.get("/chart-data")
async def get_chart_data():
    """Get chart data CSV for additional visualizations"""
    file_path = UHI_DATA_PATH / "melbourne_heat_chart_data.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Chart data not found")

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        headers={"Cache-Control": "public, max-age=86400"}
    )