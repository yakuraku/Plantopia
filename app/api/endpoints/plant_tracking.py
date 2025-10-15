"""
Plant Tracking API Endpoints
Handles plant instance tracking, progress monitoring, and AI-generated growth data
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from app.schemas.plant_tracking import (
    StartTrackingRequest,
    StartTrackingResponse,
    UserPlantsResponse,
    PlantInstanceDetailResponse,
    UpdateProgressRequest,
    MessageResponse,
    RequirementsResponse,
    InstructionsResponse,
    TimelineResponse,
    TipsResponse,
    CompleteChecklistItemRequest,
    ChecklistCompleteResponse,
    UpdateNicknameRequest,
    ErrorResponse,
    StartGrowingRequest,
    ChecklistResponse,
    CompleteSetupResponse,
    InstanceStatusResponse
)
from app.services.plant_instance_service import PlantInstanceService
from app.services.progress_tracking_service import ProgressTrackingService
from app.services.plant_growth_service import PlantGrowthService
from app.core.database import get_async_db
from app.schemas.user import UserUpsertRequest
from app.repositories.user_repository import UserRepository

router = APIRouter(tags=["plant-tracking"])


# Dependency injection
async def get_plant_instance_service(
    db: AsyncSession = Depends(get_async_db)
) -> PlantInstanceService:
    """Get plant instance service instance"""
    return PlantInstanceService(db)


async def get_progress_tracking_service(
    db: AsyncSession = Depends(get_async_db)
) -> ProgressTrackingService:
    """Get progress tracking service instance"""
    return ProgressTrackingService(db)


async def get_plant_growth_service(
    db: AsyncSession = Depends(get_async_db)
) -> PlantGrowthService:
    """Get plant growth service instance"""
    return PlantGrowthService(db)


# ============================================================================
# CORE TRACKING ENDPOINTS
# ============================================================================

@router.post("/tracking/start", response_model=StartTrackingResponse, status_code=201)
async def start_plant_tracking(
    request: StartTrackingRequest,
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Start tracking a new plant instance.

    This endpoint:
    - Auto-creates user if email doesn't exist in database
    - Creates a new plant tracking instance for the user
    - Generates AI-powered growth data if not already available
    - Initializes the plant with default growth stage (germination)
    - Calculates expected maturity date based on plant characteristics

    Args:
        request: Start tracking request with user_data (includes email), plant_id, nickname

    Returns:
        StartTrackingResponse with instance details and success message

    Raises:
        HTTPException 404: If plant not found
        HTTPException 500: If tracking creation fails
    """
    try:
        # Extract email from user_data
        user_data_dict = request.user_data.model_dump()
        email = user_data_dict.get('email')

        if not email:
            raise HTTPException(status_code=400, detail="Email is required in user_data")

        result = await plant_instance_service.start_tracking(
            email=email,
            plant_id=request.plant_id,
            plant_nickname=request.plant_nickname,
            start_date=request.start_date or date.today(),
            user_data=user_data_dict,
            location_details=request.location_details
        )

        return StartTrackingResponse(
            instance_id=result["instance_id"],
            plant_nickname=result["plant_nickname"],
            start_date=result["start_date"],
            expected_maturity_date=result["expected_maturity_date"],
            current_stage=result["current_stage"],
            message=result["message"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting plant tracking: {str(e)}")


@router.get("/tracking/user/{email}", response_model=UserPlantsResponse)
async def get_user_plant_instances(
    email: str,
    active_only: bool = Query(True, description="Filter for active plants only"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Get all plant instances for a specific user.

    This endpoint:
    - Returns a paginated list of user's tracked plants
    - Includes progress percentage and days elapsed for each plant
    - Can filter for active plants only or include deactivated ones
    - Shows plant details, nickname, and current growth stage

    Args:
        email: User email to get plants for
        active_only: If True, only return active plants
        page: Page number for pagination
        limit: Number of plants per page

    Returns:
        UserPlantsResponse with plant list and pagination info

    Raises:
        HTTPException 404: If user not found
        HTTPException 500: If data retrieval fails
    """
    try:
        result = await plant_instance_service.get_user_plants(
            email=email,
            active_only=active_only,
            page=page,
            limit=limit
        )

        return UserPlantsResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading user plants: {str(e)}")


@router.get("/tracking/instance/{instance_id}", response_model=PlantInstanceDetailResponse)
async def get_plant_instance_details(
    instance_id: int,
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Get detailed information about a specific plant instance.

    This endpoint:
    - Returns comprehensive instance details including plant info
    - Provides complete growth timeline with stage completion status
    - Shows current care tips for the active growth stage
    - Includes progress tracking and user notes

    Args:
        instance_id: Plant instance ID

    Returns:
        PlantInstanceDetailResponse with full instance details

    Raises:
        HTTPException 404: If instance not found
        HTTPException 500: If data retrieval fails
    """
    try:
        result = await plant_instance_service.get_instance_details(instance_id)
        return PlantInstanceDetailResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading instance details: {str(e)}")


@router.put("/tracking/instance/{instance_id}/progress", response_model=MessageResponse)
async def update_plant_progress(
    instance_id: int,
    request: UpdateProgressRequest,
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Update progress information for a plant instance.

    This endpoint:
    - Allows updating current growth stage
    - Saves user notes about plant observations
    - Updates location details if needed
    - Tracks progress changes over time

    Args:
        instance_id: Plant instance ID
        request: Update request with optional stage, notes, and location

    Returns:
        MessageResponse with success confirmation and updated data

    Raises:
        HTTPException 404: If instance not found
        HTTPException 500: If update fails
    """
    try:
        result = await plant_instance_service.update_progress(
            instance_id=instance_id,
            current_stage=request.current_stage,
            user_notes=request.user_notes,
            location_details=request.location_details,
            align_to_stage_start=bool(request.align_to_stage_start)
        )

        return MessageResponse(
            success=True,
            message=result["message"],
            data={
                "instance_id": result["instance_id"],
                "current_stage": result["current_stage"],
                "user_notes": result["user_notes"],
                "location_details": result["location_details"]
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")


@router.post("/tracking/instance/{instance_id}/start-growing", response_model=MessageResponse)
async def start_growing_instance(
    instance_id: int,
    request: Optional[StartGrowingRequest] = None,
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Mark an instance as officially started growing.

    This endpoint:
    - Sets start_date to provided value or today's date
    - Ensures is_active is True
    - Resets current_stage to first stage if needed (germination)
    - Recalculates expected_maturity_date
    """
    try:
        start_date = (request.start_date if (request and request.start_date) else None)
        result = await plant_instance_service.start_growing(instance_id, start_date)

        return MessageResponse(
            success=True,
            message=result["message"],
            data={
                "instance_id": result["instance_id"],
                "start_date": result["start_date"],
                "expected_maturity_date": result["expected_maturity_date"],
                "current_stage": result["current_stage"],
                "is_active": result["is_active"]
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting growing: {str(e)}")


# ============================================================================
# DATA ACCESS ENDPOINTS (AI-Generated Content)
# ============================================================================

@router.get("/tracking/requirements/{plant_id}", response_model=RequirementsResponse)
async def get_plant_requirements(
    plant_id: int,
    plant_growth_service: PlantGrowthService = Depends(get_plant_growth_service)
):
    """
    Get AI-generated requirements checklist for a plant.

    This endpoint:
    - Returns categorized list of items needed to grow the plant
    - Includes tools, supplies, soil components, and other requirements
    - Data is generated once and cached for performance
    - Personalized based on user context if available

    Args:
        plant_id: Plant ID

    Returns:
        RequirementsResponse with categorized requirements

    Raises:
        HTTPException 404: If plant or growth data not found
        HTTPException 500: If data retrieval fails
    """
    try:
        result = await plant_growth_service.get_requirements(plant_id)
        return RequirementsResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading requirements: {str(e)}")


@router.get("/tracking/instructions/{plant_id}", response_model=InstructionsResponse)
async def get_setup_instructions(
    plant_id: int,
    plant_growth_service: PlantGrowthService = Depends(get_plant_growth_service)
):
    """
    Get AI-generated step-by-step setup instructions for a plant.

    This endpoint:
    - Returns detailed setup instructions organized by category
    - Covers planting, watering, positioning, and initial care
    - Personalized to user's experience level and location
    - Cached for performance after first generation

    Args:
        plant_id: Plant ID

    Returns:
        InstructionsResponse with categorized setup instructions

    Raises:
        HTTPException 404: If plant or growth data not found
        HTTPException 500: If data retrieval fails
    """
    try:
        result = await plant_growth_service.get_instructions(plant_id)
        return InstructionsResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading instructions: {str(e)}")


@router.get("/tracking/timeline/{plant_id}", response_model=TimelineResponse)
async def get_growth_timeline(
    plant_id: int,
    plant_growth_service: PlantGrowthService = Depends(get_plant_growth_service)
):
    """
    Get AI-generated growth timeline and stages for a plant.

    This endpoint:
    - Returns complete growth stages from germination to harvest
    - Includes day ranges, descriptions, and key indicators for each stage
    - Helps users understand what to expect throughout plant's lifecycle
    - Generated based on plant characteristics and growing conditions

    Args:
        plant_id: Plant ID

    Returns:
        TimelineResponse with growth stages and total days to maturity

    Raises:
        HTTPException 404: If plant or growth data not found
        HTTPException 500: If data retrieval fails
    """
    try:
        result = await plant_growth_service.get_timeline(plant_id)
        return TimelineResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading timeline: {str(e)}")


@router.get("/tracking/instance/{instance_id}/tips", response_model=TipsResponse)
async def get_current_stage_tips(
    instance_id: int,
    limit: int = Query(3, ge=1, le=10, description="Maximum number of tips to return"),
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service),
    progress_tracking_service: ProgressTrackingService = Depends(get_progress_tracking_service)
):
    """
    Get randomized care tips for the current growth stage of a plant instance.

    This endpoint:
    - Returns relevant tips for the plant's current growth stage
    - Randomizes tip selection for variety on repeated requests
    - Helps users focus on stage-specific care needs
    - Limited to prevent information overload

    Args:
        instance_id: Plant instance ID
        limit: Maximum number of tips to return (default 3, max 10)

    Returns:
        TipsResponse with list of care tips for current stage

    Raises:
        HTTPException 404: If instance not found
        HTTPException 500: If data retrieval fails
    """
    try:
        # Get instance details
        instance = await plant_instance_service.get_instance_details(instance_id)
        plant_id = instance["plant_details"]["plant_id"]
        current_stage = instance["tracking_info"]["current_stage"]
        days_elapsed = instance["tracking_info"]["days_elapsed"]

        # Get stage-specific tips
        tips = await progress_tracking_service.get_current_stage_tips(
            instance_id=instance_id,
            plant_id=plant_id,
            current_stage=current_stage,
            limit=limit
        )

        return TipsResponse(
            instance_id=instance_id,
            current_stage=current_stage,
            tips=tips
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading tips: {str(e)}")


# ============================================================================
# MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/tracking/checklist/complete", response_model=ChecklistCompleteResponse)
async def complete_checklist_item(
    request: CompleteChecklistItemRequest,
    progress_tracking_service: ProgressTrackingService = Depends(get_progress_tracking_service)
):
    """
    Mark a checklist item as complete or incomplete.

    This endpoint:
    - Toggles completion status for requirements or milestone items
    - Optionally saves user notes about the item
    - Returns updated progress summary with completion percentage
    - Tracks completion timestamp

    Args:
        request: Checklist completion request with instance, item key, and status

    Returns:
        ChecklistCompleteResponse with updated progress summary

    Raises:
        HTTPException 500: If update fails
    """
    try:
        result = await progress_tracking_service.mark_checklist_item_complete(
            instance_id=request.instance_id,
            checklist_item_key=request.checklist_item_key,
            is_completed=request.is_completed,
            user_notes=request.user_notes
        )

        return ChecklistCompleteResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating checklist: {str(e)}")


@router.post("/tracking/instance/{instance_id}/initialize-checklist", response_model=MessageResponse)
async def initialize_instance_checklist(
    instance_id: int,
    progress_tracking_service: ProgressTrackingService = Depends(get_progress_tracking_service),
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Initialize checklist items for a plant instance from requirements data.

    This endpoint:
    - Creates tracking entries for all requirements items
    - Links to AI-generated requirements checklist
    - Only creates items that don't already exist
    - Returns count of items created

    Args:
        instance_id: Plant instance ID

    Returns:
        MessageResponse with initialization result and item count

    Raises:
        HTTPException 404: If instance not found or no growth data available
        HTTPException 500: If initialization fails
    """
    try:
        # Get plant_id from instance
        instance = await plant_instance_service.get_instance_details(instance_id)
        plant_id = instance["plant_details"]["plant_id"]

        # Initialize checklist
        result = await progress_tracking_service.initialize_checklist(
            instance_id=instance_id,
            plant_id=plant_id
        )

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])

        return MessageResponse(
            success=True,
            message=result["message"],
            data={"items_created": result["items_created"]}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing checklist: {str(e)}")


@router.put("/tracking/instance/{instance_id}/nickname", response_model=MessageResponse)
async def update_plant_nickname(
    instance_id: int,
    request: UpdateNicknameRequest,
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Update the nickname for a plant instance.

    This endpoint:
    - Allows users to personalize their plant with a custom name
    - Validates nickname is not empty
    - Returns confirmation with updated nickname

    Args:
        instance_id: Plant instance ID
        request: Update request with new nickname

    Returns:
        MessageResponse with success confirmation

    Raises:
        HTTPException 404: If instance not found
        HTTPException 400: If nickname is empty
        HTTPException 500: If update fails
    """
    try:
        if not request.plant_nickname or not request.plant_nickname.strip():
            raise HTTPException(status_code=400, detail="Plant nickname cannot be empty")

        result = await plant_instance_service.update_nickname(
            instance_id=instance_id,
            new_nickname=request.plant_nickname
        )

        return MessageResponse(
            success=True,
            message=result["message"],
            data={
                "instance_id": result["instance_id"],
                "plant_nickname": result["plant_nickname"]
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating nickname: {str(e)}")


@router.delete("/tracking/instance/{instance_id}", response_model=MessageResponse)
async def delete_plant_instance(
    instance_id: int,
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Delete a plant instance (hard delete).

    This endpoint:
    - Permanently removes the plant instance and its tracking data
    - Instance disappears from all lists and detail endpoints
    - Use with caution

    Args:
        instance_id: Plant instance ID to delete

    Returns:
        MessageResponse with confirmation

    Raises:
        HTTPException 404: If instance not found
        HTTPException 500: If deletion fails
    """
    try:
        result = await plant_instance_service.delete_instance(instance_id)

        return MessageResponse(
            success=True,
            message=result["message"],
            data={
                "instance_id": result["instance_id"],
                "deleted": True
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting instance: {str(e)}")


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.post("/tracking/instance/{instance_id}/auto-update-stage", response_model=MessageResponse)
async def auto_update_growth_stage(
    instance_id: int,
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Automatically update plant growth stage based on days elapsed.

    This endpoint:
    - Calculates days since planting
    - Determines correct stage from growth timeline
    - Updates stage if it has changed
    - Returns new stage or confirmation if no change

    Args:
        instance_id: Plant instance ID

    Returns:
        MessageResponse with stage update result

    Raises:
        HTTPException 404: If instance not found
        HTTPException 500: If update fails
    """
    try:
        new_stage = await plant_instance_service.auto_update_stage(instance_id)

        if new_stage:
            return MessageResponse(
                success=True,
                message=f"Plant stage automatically updated to: {new_stage}",
                data={
                    "instance_id": instance_id,
                    "new_stage": new_stage,
                    "updated": True
                }
            )
        else:
            return MessageResponse(
                success=True,
                message="Plant stage is already up to date",
                data={
                    "instance_id": instance_id,
                    "updated": False
                }
            )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error auto-updating stage: {str(e)}")


# ============================================================================
# PHASE 1 ENDPOINTS - Enhanced Journal Tracking
# ============================================================================

@router.get("/tracking/instance/{instance_id}/checklist", response_model=ChecklistResponse)
async def get_instance_checklist(
    instance_id: int,
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service),
    progress_tracking_service: ProgressTrackingService = Depends(get_progress_tracking_service)
):
    """
    Retrieve the saved checklist state for a plant instance.

    This endpoint:
    - Returns all checklist items with their completion status
    - Includes item details (category, name, quantity, optional flag)
    - Shows completion timestamps and user notes
    - Provides progress summary (total items, completed items, percentage)

    Args:
        instance_id: Plant instance ID

    Returns:
        ChecklistResponse with detailed checklist items and progress summary

    Raises:
        HTTPException 404: If instance not found
        HTTPException 500: If data retrieval fails
    """
    try:
        # Get instance details to retrieve plant_id
        instance = await plant_instance_service.get_instance_details(instance_id)
        plant_id = instance["plant_details"]["plant_id"]

        # Get checklist with full details
        result = await progress_tracking_service.get_checklist_with_details(
            instance_id=instance_id,
            plant_id=plant_id
        )

        return ChecklistResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading checklist: {str(e)}")


@router.post("/tracking/instance/{instance_id}/complete-setup", response_model=CompleteSetupResponse)
async def complete_setup_instructions(
    instance_id: int,
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Mark setup instructions as complete for a plant instance.

    This endpoint:
    - Sets setup_completed flag to True
    - Records the completion timestamp
    - Separate from starting growth (is_active status)
    - Allows tracking setup completion independently

    Args:
        instance_id: Plant instance ID

    Returns:
        CompleteSetupResponse with completion status and timestamp

    Raises:
        HTTPException 404: If instance not found
        HTTPException 500: If update fails
    """
    try:
        result = await plant_instance_service.complete_setup(instance_id)

        return CompleteSetupResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing setup: {str(e)}")


@router.get("/tracking/instance/{instance_id}/status", response_model=InstanceStatusResponse)
async def get_instance_status(
    instance_id: int,
    plant_instance_service: PlantInstanceService = Depends(get_plant_instance_service)
):
    """
    Get comprehensive status summary for a plant instance.

    This endpoint:
    - Returns checklist progress (total, completed, percentage, threshold status)
    - Shows setup completion status and timestamp
    - Provides growing status (active, days elapsed, current stage, progress)
    - Helps determine which step to show in the UI

    Args:
        instance_id: Plant instance ID

    Returns:
        InstanceStatusResponse with complete status across all three steps

    Raises:
        HTTPException 404: If instance not found
        HTTPException 500: If data retrieval fails
    """
    try:
        result = await plant_instance_service.get_instance_status_summary(instance_id)

        return InstanceStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading instance status: {str(e)}")


# ============================================================================
# USER UPSERT ENDPOINT (for frontend to write/update user + profile)
# ============================================================================

@router.post("/tracking/user/upsert")
async def upsert_user_from_tracking(
    user_data: UserUpsertRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create or update user and profile from unified user_data payload.

    Only email is required; other fields are optional. Provided fields will be
    persisted/updated; missing fields keep existing/default values.
    """
    try:
        repo = UserRepository(db)
        payload = {k: v for k, v in user_data.dict().items() if v is not None}
        user = await repo.get_or_create_user_by_email(user_data.email, payload)

        # Fetch latest profile after upsert
        profile = await repo.get_user_profile(user.id)
        profile_dict = None
        if profile:
            profile_dict = {
                "id": profile.id,
                "user_id": profile.user_id,
                "experience_level": profile.experience_level,
                "garden_type": profile.garden_type,
                "climate_goals": profile.climate_goals,
                "available_space_m2": profile.available_space_m2,
                "sun_exposure": profile.sun_exposure,
                "has_containers": profile.has_containers,
                "organic_preference": profile.organic_preference,
                "budget_level": profile.budget_level,
                "notification_preferences": profile.notification_preferences,
                "created_at": profile.created_at,
                "updated_at": profile.updated_at,
            }

        return {
            "success": True,
            "message": "User upserted successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "suburb_id": user.suburb_id,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login": user.last_login,
            },
            "profile": profile_dict,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error upserting user: {str(e)}")
