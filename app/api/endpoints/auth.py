"""
Authentication API endpoints for user management and Google OAuth
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.api.dependencies import get_current_user, get_auth_service
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    GoogleAuthRequest,
    AuthResponse,
    UserResponse,
    UserUpdate,
    UserProfileResponse,
    UserProfileUpdate,
    UserWithProfileResponse,
    UserUpsertRequest
)
from app.models.database import User

router = APIRouter()


@router.post("/google", response_model=AuthResponse)
async def google_login(
    auth_request: GoogleAuthRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user with Google OAuth

    Args:
        auth_request: Google OAuth credential

    Returns:
        Authentication response with user data and JWT token
    """
    try:
        user, access_token = await auth_service.authenticate_with_google(auth_request.credential)

        # Convert user to response format
        user_response = UserResponse(
            id=user.id,
            google_id=user.google_id,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            suburb=None if not user.suburb else {
                "id": user.suburb.id,
                "name": user.suburb.name,
                "postcode": user.suburb.postcode,
                "latitude": user.suburb.latitude,
                "longitude": user.suburb.longitude
            },
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )

        return AuthResponse(
            user=user_response,
            access_token=access_token,
            token_type="bearer"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/users/upsert")
async def upsert_user(
    user_data: UserUpsertRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create or update user and profile from unified user_data payload.

    Request body (user_data):
    {
      "email": "string",
      "name": "string",
      "suburb_id": 0,
      "experience_level": "beginner",
      "garden_type": "backyard",
      "available_space": 10,
      "climate_goal": "general gardening"
    }
    """
    try:
        repo = UserRepository(db)
        email = user_data.email
        if not email:
            raise HTTPException(status_code=400, detail="email is required")

        # Convert model to dict with only provided (non-None) fields
        payload = {k: v for k, v in user_data.dict().items() if v is not None}
        user = await repo.get_or_create_user_by_email(email, payload)

        return {
            "success": True,
            "message": "User upserted successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "suburb_id": user.suburb_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error upserting user: {str(e)}")


@router.get("/me", response_model=UserWithProfileResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current authenticated user's information with profile

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        User information with profile data
    """
    user_repo = UserRepository(db)

    # Get user profile
    profile = await user_repo.get_user_profile(current_user.id)

    # Convert to response format
    user_response = UserResponse(
        id=current_user.id,
        google_id=current_user.google_id,
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        suburb=None if not current_user.suburb else {
            "id": current_user.suburb.id,
            "name": current_user.suburb.name,
            "postcode": current_user.suburb.postcode,
            "latitude": current_user.suburb.latitude,
            "longitude": current_user.suburb.longitude
        },
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

    profile_response = None
    if profile:
        profile_response = UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            experience_level=profile.experience_level,
            garden_type=profile.garden_type,
            climate_goals=profile.climate_goals,
            available_space_m2=profile.available_space_m2,
            sun_exposure=profile.sun_exposure,
            has_containers=profile.has_containers,
            organic_preference=profile.organic_preference,
            budget_level=profile.budget_level,
            notification_preferences=profile.notification_preferences,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )

    return UserWithProfileResponse(
        **user_response.dict(),
        profile=profile_response
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update current authenticated user's information

    Args:
        user_update: User update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user information
    """
    user_repo = UserRepository(db)

    # Prepare update data (only include non-None values)
    update_data = {}
    if user_update.name is not None:
        update_data['name'] = user_update.name
    if user_update.avatar_url is not None:
        update_data['avatar_url'] = user_update.avatar_url
    if user_update.suburb_name is not None:
        update_data['suburb_name'] = user_update.suburb_name

    if update_data:
        updated_user = await user_repo.update_user(current_user.id, update_data)
    else:
        updated_user = current_user

    # Convert to response format
    return UserResponse(
        id=updated_user.id,
        google_id=updated_user.google_id,
        email=updated_user.email,
        name=updated_user.name,
        avatar_url=updated_user.avatar_url,
        suburb=None if not updated_user.suburb else {
            "id": updated_user.suburb.id,
            "name": updated_user.suburb.name,
            "postcode": updated_user.suburb.postcode,
            "latitude": updated_user.suburb.latitude,
            "longitude": updated_user.suburb.longitude
        },
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        last_login=updated_user.last_login
    )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current user's profile

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        User profile information
    """
    user_repo = UserRepository(db)
    profile = await user_repo.get_user_profile(current_user.id)

    if not profile:
        # Create empty profile if it doesn't exist
        profile = await user_repo.create_or_update_profile(current_user.id, {})

    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        experience_level=profile.experience_level,
        garden_type=profile.garden_type,
        climate_goals=profile.climate_goals,
        available_space_m2=profile.available_space_m2,
        sun_exposure=profile.sun_exposure,
        has_containers=profile.has_containers,
        organic_preference=profile.organic_preference,
        budget_level=profile.budget_level,
        notification_preferences=profile.notification_preferences,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create or update current user's profile

    Args:
        profile_update: Profile update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user profile information
    """
    user_repo = UserRepository(db)

    # Prepare update data (only include non-None values)
    update_data = {}
    for field, value in profile_update.dict().items():
        if value is not None:
            update_data[field] = value

    profile = await user_repo.create_or_update_profile(current_user.id, update_data)

    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        experience_level=profile.experience_level,
        garden_type=profile.garden_type,
        climate_goals=profile.climate_goals,
        available_space_m2=profile.available_space_m2,
        sun_exposure=profile.sun_exposure,
        has_containers=profile.has_containers,
        organic_preference=profile.organic_preference,
        budget_level=profile.budget_level,
        notification_preferences=profile.notification_preferences,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token removal)

    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}