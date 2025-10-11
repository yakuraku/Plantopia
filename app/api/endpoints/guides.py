"""
Plant Guide API Endpoints
Handles plant guide listing, content retrieval, and user favorites
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.guide import (
    GuideListResponse,
    CategoryGuidesResponse,
    GuideContent,
    CategoriesResponse,
    GuideFavoriteCreate,
    GuideFavoriteResponse,
    UserGuideFavoritesResponse,
    GuideFavoriteRemoveResponse,
    GuideFavoriteCheckResponse
)
from app.services.guide_service import GuideService
from app.core.database import get_async_db

router = APIRouter(tags=["guides"])


# Dependency injection
async def get_guide_service(
    db: AsyncSession = Depends(get_async_db)
) -> GuideService:
    """Get guide service instance"""
    return GuideService(db)


# ============================================================================
# GUIDE LISTING AND RETRIEVAL ENDPOINTS
# ============================================================================

@router.get("", response_model=GuideListResponse)
async def list_all_guides(
    guide_service: GuideService = Depends(get_guide_service)
):
    """
    List all available plant guides across all categories.

    This endpoint:
    - Returns all guides organized by category
    - Provides category list for navigation
    - No authentication required (public guides)
    - Useful for browsing all available guides

    Returns:
        GuideListResponse with all guides and categories
    """
    try:
        result = await guide_service.get_all_guides()
        return GuideListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading guides: {str(e)}")


@router.get("/categories", response_model=CategoriesResponse)
async def list_categories(
    guide_service: GuideService = Depends(get_guide_service)
):
    """
    List all available guide categories.

    This endpoint:
    - Returns list of guide categories
    - Useful for building category navigation
    - No authentication required

    Returns:
        CategoriesResponse with category list
    """
    try:
        result = await guide_service.get_categories()
        return CategoriesResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading categories: {str(e)}")


@router.get("/{category}", response_model=CategoryGuidesResponse)
async def list_guides_by_category(
    category: str,
    guide_service: GuideService = Depends(get_guide_service)
):
    """
    List all guides in a specific category.

    This endpoint:
    - Returns guides filtered by category
    - Useful for category-specific browsing
    - No authentication required

    Args:
        category: Category name (e.g., "Composting", "flowers", "grow_guide")

    Returns:
        CategoryGuidesResponse with guides in that category

    Raises:
        HTTPException 404: If category not found
    """
    try:
        result = await guide_service.get_guides_by_category(category)
        return CategoryGuidesResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading guides: {str(e)}")


@router.get("/{category}/{guide_name}", response_model=GuideContent)
async def get_guide_content(
    category: str,
    guide_name: str,
    guide_service: GuideService = Depends(get_guide_service)
):
    """
    Get the full content of a specific guide.

    This endpoint:
    - Returns complete markdown content
    - Includes guide metadata (title, category, path)
    - No authentication required
    - Useful for displaying guide in reader view

    Args:
        category: Category name
        guide_name: Guide filename (e.g., "Composting for Beginners.md")

    Returns:
        GuideContent with full markdown content

    Raises:
        HTTPException 404: If guide not found
    """
    try:
        result = await guide_service.get_guide_content(category, guide_name)
        return GuideContent(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading guide: {str(e)}")


# ============================================================================
# GUIDE FAVORITES ENDPOINTS
# ============================================================================

@router.post("/favorites", response_model=GuideFavoriteResponse, status_code=201)
async def add_guide_to_favorites(
    favorite_data: GuideFavoriteCreate,
    guide_service: GuideService = Depends(get_guide_service)
):
    """
    Add a guide to user's favorites.

    This endpoint:
    - Adds guide to user's personal favorites list
    - Validates user exists by email
    - Validates guide exists
    - Prevents duplicate favorites

    Args:
        favorite_data: Contains email, guide_name, optional category and notes

    Returns:
        GuideFavoriteResponse with created favorite info

    Raises:
        HTTPException 404: If user or guide not found
        HTTPException 400: If guide already favorited
    """
    try:
        result = await guide_service.add_guide_favorite(
            email=favorite_data.email,
            guide_name=favorite_data.guide_name,
            category=favorite_data.category,
            notes=favorite_data.notes
        )
        return GuideFavoriteResponse(**result)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding favorite: {str(e)}")


@router.delete("/favorites/{guide_name}", response_model=GuideFavoriteRemoveResponse)
async def remove_guide_from_favorites(
    guide_name: str,
    email: str = Query(..., description="User email address"),
    guide_service: GuideService = Depends(get_guide_service)
):
    """
    Remove a guide from user's favorites.

    This endpoint:
    - Removes guide from user's favorites list
    - Validates user exists
    - Returns error if favorite not found

    Args:
        guide_name: Guide filename to remove
        email: User email (query parameter)

    Returns:
        GuideFavoriteRemoveResponse with success confirmation

    Raises:
        HTTPException 404: If user or favorite not found
    """
    try:
        result = await guide_service.remove_guide_favorite(
            email=email,
            guide_name=guide_name
        )
        return GuideFavoriteRemoveResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing favorite: {str(e)}")


@router.get("/favorites/user", response_model=UserGuideFavoritesResponse)
async def get_user_guide_favorites(
    email: str = Query(..., description="User email address"),
    guide_service: GuideService = Depends(get_guide_service)
):
    """
    Get all guide favorites for a user.

    This endpoint:
    - Returns user's complete list of favorite guides
    - Enriches with guide details (title, path)
    - Ordered by most recently favorited
    - Validates user exists

    Args:
        email: User email (query parameter)

    Returns:
        UserGuideFavoritesResponse with user's favorite guides

    Raises:
        HTTPException 404: If user not found
    """
    try:
        result = await guide_service.get_user_guide_favorites(email=email)
        return UserGuideFavoritesResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading favorites: {str(e)}")


@router.get("/favorites/check/{guide_name}", response_model=GuideFavoriteCheckResponse)
async def check_guide_favorite_status(
    guide_name: str,
    email: str = Query(..., description="User email address"),
    guide_service: GuideService = Depends(get_guide_service)
):
    """
    Check if a guide is in user's favorites.

    This endpoint:
    - Checks favorite status for a specific guide
    - Useful for showing favorite icon in UI
    - Validates user exists

    Args:
        guide_name: Guide filename to check
        email: User email (query parameter)

    Returns:
        GuideFavoriteCheckResponse with favorite status

    Raises:
        HTTPException 404: If user not found
    """
    try:
        result = await guide_service.check_guide_favorite(
            email=email,
            guide_name=guide_name
        )
        return GuideFavoriteCheckResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking favorite: {str(e)}")
