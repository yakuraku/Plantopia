"""
Favorites API endpoints for managing user's favorite plants
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    FavoriteCreate,
    FavoriteResponse,
    FavoriteSyncRequest
)

router = APIRouter()


@router.get("", response_model=List[FavoriteResponse])
async def get_user_favorites(
    email: str = Query(..., description="User email address"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all user's favorite plants

    Args:
        email: User email address
        db: Database session

    Returns:
        List of user's favorite plants with details

    Raises:
        HTTPException 404: If user not found
    """
    user_repo = UserRepository(db)

    # Get user by email
    user = await user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )

    favorites = await user_repo.get_user_favorites(user.id)

    return [
        FavoriteResponse(
            id=fav.id,
            plant_id=fav.plant_id,
            plant_name=fav.plant.plant_name,
            plant_category=fav.plant.plant_category,
            notes=fav.notes,
            priority_level=fav.priority_level,
            created_at=fav.created_at
        )
        for fav in favorites
    ]


@router.post("", response_model=FavoriteResponse)
async def add_favorite(
    favorite_data: FavoriteCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Add a plant to user's favorites

    Args:
        favorite_data: Favorite creation data (includes email, plant_id, notes)
        db: Database session

    Returns:
        Created favorite information

    Raises:
        HTTPException 404: If user not found
        HTTPException 500: If operation fails
    """
    user_repo = UserRepository(db)

    try:
        # Get user by email
        user = await user_repo.get_user_by_email(favorite_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {favorite_data.email} not found"
            )

        favorite = await user_repo.add_favorite(
            user_id=user.id,
            plant_id=favorite_data.plant_id,
            notes=favorite_data.notes
        )

        # Get the favorite with plant data loaded
        favorites = await user_repo.get_user_favorites(user.id)
        created_favorite = next(
            (fav for fav in favorites if fav.id == favorite.id),
            None
        )

        if not created_favorite:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created favorite"
            )

        return FavoriteResponse(
            id=created_favorite.id,
            plant_id=created_favorite.plant_id,
            plant_name=created_favorite.plant.plant_name,
            plant_category=created_favorite.plant.plant_category,
            notes=created_favorite.notes,
            priority_level=created_favorite.priority_level,
            created_at=created_favorite.created_at
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add favorite: {str(e)}"
        )


@router.delete("/{plant_id}")
async def remove_favorite(
    plant_id: int,
    email: str = Query(..., description="User email address"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Remove a plant from user's favorites

    Args:
        plant_id: Plant ID to remove from favorites
        email: User email address
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 404: If user or favorite not found
    """
    user_repo = UserRepository(db)

    # Get user by email
    user = await user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )

    success = await user_repo.remove_favorite(user.id, plant_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )

    return {"success": True, "message": "Favorite removed successfully"}


@router.post("/sync", response_model=List[FavoriteResponse])
async def sync_favorites(
    sync_data: FavoriteSyncRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Sync favorites from localStorage (merge strategy)

    Args:
        sync_data: Sync data (includes email and list of plant IDs)
        db: Database session

    Returns:
        All user's favorites after sync

    Raises:
        HTTPException 404: If user not found
        HTTPException 500: If operation fails
    """
    user_repo = UserRepository(db)

    try:
        # Get user by email
        user = await user_repo.get_user_by_email(sync_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {sync_data.email} not found"
            )

        favorites = await user_repo.sync_favorites(
            user_id=user.id,
            plant_ids=sync_data.favorite_plant_ids
        )

        return [
            FavoriteResponse(
                id=fav.id,
                plant_id=fav.plant_id,
                plant_name=fav.plant.plant_name,
                plant_category=fav.plant.plant_category,
                notes=fav.notes,
                priority_level=fav.priority_level,
                created_at=fav.created_at
            )
            for fav in favorites
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync favorites: {str(e)}"
        )


@router.get("/check/{plant_id}")
async def check_favorite(
    plant_id: int,
    email: str = Query(..., description="User email address"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Check if a plant is in user's favorites

    Args:
        plant_id: Plant ID to check
        email: User email address
        db: Database session

    Returns:
        Whether the plant is favorited

    Raises:
        HTTPException 404: If user not found
    """
    user_repo = UserRepository(db)

    # Get user by email
    user = await user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )

    is_favorite = await user_repo.is_favorite(user.id, plant_id)

    return {"is_favorite": is_favorite}