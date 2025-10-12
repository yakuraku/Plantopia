"""
Plant Instance Service for managing user plant tracking instances
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.plant_instance_repository import PlantInstanceRepository
from app.repositories.progress_tracking_repository import ProgressTrackingRepository
from app.repositories.user_repository import UserRepository
from app.services.plant_growth_service import PlantGrowthService
from sqlalchemy import select
from app.models.database import Plant


logger = logging.getLogger(__name__)


class PlantInstanceService:
    """Service for managing user plant tracking instances"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PlantInstanceRepository(db)
        self.progress_repository = ProgressTrackingRepository(db)
        self.user_repository = UserRepository(db)
        self.growth_service = PlantGrowthService(db)

    async def start_tracking(
        self,
        email: str,
        plant_id: int,
        plant_nickname: str,
        start_date: date,
        user_data: Dict[str, Any],
        location_details: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start tracking a new plant instance

        Args:
            email: User email (auto-creates user if doesn't exist)
            plant_id: Plant ID
            plant_nickname: User's custom nickname
            start_date: Start date
            user_data: User context for AI generation (includes email, name, suburb_id, etc)
            location_details: Optional location info

        Returns:
            Dictionary with created instance info

        Raises:
            ValueError: If plant not found
        """
        # Get or create user by email
        user = await self.user_repository.get_or_create_user_by_email(email, user_data)

        # Get plant details
        plant = await self.growth_service.get_plant_by_id(plant_id)
        if not plant:
            raise ValueError(f"Plant with ID {plant_id} not found")

        # Ensure growth data exists (generate if needed)
        await self.growth_service.get_or_generate_growth_data(plant_id, user_data)

        # Calculate expected maturity date
        maturity_days = plant.time_to_maturity_days or 90  # Default to 90 days
        expected_maturity_date = start_date + timedelta(days=maturity_days)

        # Create instance
        instance_data = {
            "user_id": user.id,
            "plant_id": plant_id,
            "plant_nickname": plant_nickname,
            "start_date": start_date,
            "expected_maturity_date": expected_maturity_date,
            "current_stage": "germination",  # Default first stage
            "is_active": False,
            "location_details": location_details
        }

        instance = await self.repository.create(instance_data)

        logger.info(f"Created plant instance {instance.id} for user {email} (ID: {user.id}), plant {plant_id}")

        return {
            "instance_id": instance.id,
            "plant_nickname": instance.plant_nickname,
            "start_date": instance.start_date,
            "expected_maturity_date": instance.expected_maturity_date,
            "current_stage": instance.current_stage,
            "message": "Plant tracking started successfully"
        }

    async def get_user_plants(
        self,
        email: str,
        active_only: bool = True,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get all plant instances for a user

        Args:
            email: User email
            active_only: Filter for active plants only
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Dictionary with plant instances and pagination info

        Raises:
            ValueError: If user not found
        """
        # Get user by email
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        offset = (page - 1) * limit

        # Get instances
        instances = await self.repository.get_user_instances(
            user.id,
            active_only=active_only,
            limit=limit,
            offset=offset
        )

        # Get total counts
        total_count = await self.repository.count_user_instances(user.id, active_only=False)
        active_count = await self.repository.count_user_instances(user.id, active_only=True)

        # Build response with summary data
        plants_summary = []
        for instance in instances:
            # Calculate days_elapsed directly from instance data (avoid extra DB query)
            days_elapsed = (date.today() - instance.start_date).days
            progress_pct = await self.calculate_progress_percentage(instance)

            plants_summary.append({
                "instance_id": instance.id,
                "plant_id": instance.plant_id,
                "plant_name": instance.plant.plant_name if instance.plant else "Unknown",
                "plant_nickname": instance.plant_nickname,
                "start_date": instance.start_date,
                "expected_maturity_date": instance.expected_maturity_date,
                "current_stage": instance.current_stage,
                "days_elapsed": days_elapsed,
                "progress_percentage": progress_pct,
                "location_details": instance.location_details,
                "image_url": instance.plant.image_url if instance.plant else None
            })

        total_pages = (total_count + limit - 1) // limit  # Ceiling division

        return {
            "plants": plants_summary,
            "total_count": total_count,
            "active_count": active_count,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_pages": total_pages
            }
        }

    async def get_instance_details(self, instance_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a plant instance

        Args:
            instance_id: Plant instance ID

        Returns:
            Dictionary with comprehensive instance details

        Raises:
            ValueError: If instance not found
        """
        instance = await self.repository.get_by_id(instance_id)
        if not instance:
            raise ValueError(f"Plant instance with ID {instance_id} not found")

        # Get growth data
        growth_data = await self.growth_service.get_timeline(instance.plant_id)

        # Calculate progress
        days_elapsed = await self.repository.calculate_days_elapsed(instance_id)
        progress_pct = await self.calculate_progress_percentage(instance)

        # Build timeline with completion status and calendar dates
        timeline_stages = []
        for stage in growth_data.get("stages", []):
            is_completed = days_elapsed > stage["end_day"]
            is_current = (
                days_elapsed >= stage["start_day"] and
                days_elapsed <= stage["end_day"]
            )

            # Calculate actual calendar dates from start_date
            actual_start_date = instance.start_date + timedelta(days=stage["start_day"])
            actual_end_date = instance.start_date + timedelta(days=stage["end_day"])

            timeline_stages.append({
                "stage_name": stage["stage_name"],
                "start_day": stage["start_day"],
                "end_day": stage["end_day"],
                "actual_start_date": actual_start_date,
                "actual_end_date": actual_end_date,
                "description": stage["description"],
                "is_completed": is_completed,
                "is_current": is_current,
                "key_indicators": stage.get("key_indicators", [])
            })

        # Get current stage tips
        tips_data = await self.growth_service.get_care_tips_for_stage(
            instance.plant_id,
            instance.current_stage
        )
        current_tips = [tip.get("tip") for tip in tips_data.get("tips", [])]

        return {
            "instance_id": instance.id,
            "plant_details": {
                "plant_id": instance.plant_id,
                "plant_name": instance.plant.plant_name if instance.plant else "Unknown",
                "scientific_name": instance.plant.scientific_name if instance.plant else None,
                "plant_category": instance.plant.plant_category if instance.plant else None
            },
            "tracking_info": {
                "plant_nickname": instance.plant_nickname,
                "start_date": instance.start_date,
                "expected_maturity_date": instance.expected_maturity_date,
                "current_stage": instance.current_stage,
                "days_elapsed": days_elapsed,
                "progress_percentage": progress_pct,
                "is_active": instance.is_active,
                "user_notes": instance.user_notes,
                "location_details": instance.location_details
            },
            "timeline": {
                "stages": timeline_stages
            },
            "current_tips": current_tips
        }

    async def update_progress(
        self,
        instance_id: int,
        current_stage: Optional[str] = None,
        user_notes: Optional[str] = None,
        location_details: Optional[str] = None,
        align_to_stage_start: bool = False
    ) -> Dict[str, Any]:
        """
        Update plant instance progress

        Args:
            instance_id: Plant instance ID
            current_stage: New growth stage
            user_notes: User notes
            location_details: Location details

        Returns:
            Updated instance information
        """
        update_data: Dict[str, Any] = {}

        # If caller wants to align start_date to the beginning of the chosen stage,
        # compute the stage's start_day and back-calculate a new start_date so that
        # days_elapsed equals start_day. Also recompute expected_maturity_date.
        if current_stage is not None:
            update_data["current_stage"] = current_stage

            if align_to_stage_start:
                instance = await self.repository.get_by_id(instance_id)
                if not instance:
                    raise ValueError(f"Plant instance with ID {instance_id} not found")

                # Get timeline for this plant and find the selected stage
                timeline = await self.growth_service.get_timeline(instance.plant_id)
                stages: List[Dict[str, Any]] = timeline.get("stages", [])

                stage_start_day: Optional[int] = None
                for stage in stages:
                    if stage.get("stage_name") == current_stage:
                        stage_start_day = stage.get("start_day")
                        break

                if stage_start_day is None:
                    # If stage name not found, proceed without alignment
                    pass
                else:
                    # Move start_date backward so that today - start_date == stage_start_day
                    new_start_date = date.today() - timedelta(days=int(stage_start_day))

                    # Recalculate expected_maturity_date from plant maturity days
                    plant_timeline = await self.growth_service.get_timeline(instance.plant_id)
                    total_days = plant_timeline.get("total_days")
                    if isinstance(total_days, int) and total_days > 0:
                        new_expected_maturity = new_start_date + timedelta(days=total_days)
                    else:
                        # Fallback to previous expected_maturity delta if available
                        previous_total = (instance.expected_maturity_date - instance.start_date).days
                        days_to_use = previous_total if previous_total > 0 else 90
                        new_expected_maturity = new_start_date + timedelta(days=days_to_use)

                    update_data.update({
                        "start_date": new_start_date,
                        "expected_maturity_date": new_expected_maturity,
                        "is_active": True,
                    })
        if user_notes is not None:
            update_data["user_notes"] = user_notes
        if location_details is not None:
            update_data["location_details"] = location_details

        instance = await self.repository.update(instance_id, update_data)

        logger.info(f"Updated plant instance {instance_id}")

        return {
            "instance_id": instance.id,
            "current_stage": instance.current_stage,
            "user_notes": instance.user_notes,
            "location_details": instance.location_details,
            "message": "Progress updated successfully"
        }

    async def start_growing(self, instance_id: int, new_start_date: Optional[date]) -> Dict[str, Any]:
        """
        Mark an existing instance as officially started growing (or restart).

        - Sets start_date to the provided date
        - Ensures is_active = True
        - Resets current_stage to 'germination'
        - Recalculates expected_maturity_date based on plant time_to_maturity_days
        """
        instance = await self.repository.get_by_id(instance_id)
        if not instance:
            raise ValueError(f"Plant instance with ID {instance_id} not found")

        update_payload: Dict[str, Any] = {}

        # If a start date is explicitly provided, set it and recompute maturity + reset stage
        if new_start_date is not None:
            plant_query = select(Plant).where(Plant.id == instance.plant_id)
            result = await self.db.execute(plant_query)
            plant: Optional[Plant] = result.scalar_one_or_none()

            maturity_days = (plant.time_to_maturity_days if plant and plant.time_to_maturity_days else 90)
            expected_maturity_date = new_start_date + timedelta(days=maturity_days)

            update_payload.update({
                "start_date": new_start_date,
                "expected_maturity_date": expected_maturity_date,
                "current_stage": "germination"
            })
            # Instance becomes active only when a start_date is explicitly set now
            update_payload["is_active"] = True

        updated = await self.repository.update(instance_id, update_payload)

        return {
            "instance_id": updated.id,
            "start_date": updated.start_date,
            "expected_maturity_date": updated.expected_maturity_date,
            "current_stage": updated.current_stage,
            "is_active": updated.is_active,
            "message": "Instance activated and started" if new_start_date is not None else "Instance activated"
        }

    async def update_nickname(self, instance_id: int, new_nickname: str) -> Dict[str, Any]:
        """Update plant nickname"""
        instance = await self.repository.update(instance_id, {"plant_nickname": new_nickname})

        return {
            "instance_id": instance.id,
            "plant_nickname": instance.plant_nickname,
            "message": "Nickname updated successfully"
        }

    async def deactivate_instance(self, instance_id: int) -> Dict[str, Any]:
        """Deactivate (soft delete) a plant instance"""
        instance = await self.repository.deactivate(instance_id)

        logger.info(f"Deactivated plant instance {instance_id}")

        return {
            "instance_id": instance.id,
            "is_active": instance.is_active,
            "message": "Plant instance deactivated successfully"
        }

    async def delete_instance(self, instance_id: int) -> Dict[str, Any]:
        """Hard delete a plant instance and its tracking data."""
        # Best-effort cleanup for tracking entries (also covered by FK cascade)
        try:
            await self.progress_repository.delete_by_instance(instance_id)
        except Exception:
            # Even if cleanup fails, proceed with deletion; FK cascade should handle
            pass

        deleted = await self.repository.delete(instance_id)
        if not deleted:
            raise ValueError(f"Plant instance with ID {instance_id} not found")

        logger.info(f"Hard deleted plant instance {instance_id}")

        return {
            "instance_id": instance_id,
            "deleted": True,
            "message": "Plant instance deleted successfully"
        }

    async def calculate_progress_percentage(self, instance) -> float:
        """
        Calculate overall progress percentage based on days elapsed

        Args:
            instance: UserPlantInstance model

        Returns:
            Progress percentage (0-100)
        """
        days_elapsed = (date.today() - instance.start_date).days
        total_days = (instance.expected_maturity_date - instance.start_date).days

        if total_days <= 0:
            return 100.0

        progress = (days_elapsed / total_days) * 100
        return min(round(progress, 2), 100.0)  # Cap at 100%

    async def auto_update_stage(self, instance_id: int) -> Optional[str]:
        """
        Automatically update stage based on days elapsed

        Args:
            instance_id: Plant instance ID

        Returns:
            New stage name if updated, None otherwise
        """
        instance = await self.repository.get_by_id(instance_id)
        if not instance:
            return None

        days_elapsed = await self.repository.calculate_days_elapsed(instance_id)

        # Get timeline
        growth_data = await self.growth_service.get_timeline(instance.plant_id)

        # Find appropriate stage
        new_stage = None
        for stage in growth_data.get("stages", []):
            if days_elapsed >= stage["start_day"] and days_elapsed <= stage["end_day"]:
                new_stage = stage["stage_name"]
                break

        # Update if stage changed
        if new_stage and new_stage != instance.current_stage:
            await self.repository.update_stage(instance_id, new_stage)
            logger.info(f"Auto-updated instance {instance_id} to stage: {new_stage}")
            return new_stage

        return None
