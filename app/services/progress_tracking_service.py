"""
Progress Tracking Service for managing checklist and milestone tracking
"""
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.progress_tracking_repository import ProgressTrackingRepository
from app.services.plant_growth_service import PlantGrowthService


logger = logging.getLogger(__name__)


class ProgressTrackingService:
    """Service for managing progress tracking and checklists"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ProgressTrackingRepository(db)
        self.growth_service = PlantGrowthService(db)

    async def mark_checklist_item_complete(
        self,
        instance_id: int,
        checklist_item_key: str,
        is_completed: bool = True,
        user_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark a checklist item as complete or incomplete

        Args:
            instance_id: Plant instance ID
            checklist_item_key: Unique key for the checklist item
            is_completed: Completion status
            user_notes: Optional user notes

        Returns:
            Dictionary with completion status and progress summary
        """
        # Mark item
        await self.repository.mark_complete(
            instance_id,
            checklist_item_key,
            is_completed,
            user_notes
        )

        # Get progress summary
        completed = await self.repository.get_completed_count(instance_id)
        total = await self.repository.get_total_count(instance_id)
        percentage = await self.repository.get_completion_percentage(instance_id)

        logger.info(
            f"Marked checklist item '{checklist_item_key}' as "
            f"{'complete' if is_completed else 'incomplete'} for instance {instance_id}"
        )

        return {
            "success": True,
            "message": f"Checklist item marked as {'complete' if is_completed else 'incomplete'}",
            "progress_summary": {
                "completed_items": completed,
                "total_items": total,
                "completion_percentage": percentage
            }
        }

    async def get_progress_summary(self, instance_id: int) -> Dict[str, Any]:
        """
        Get progress summary for a plant instance

        Args:
            instance_id: Plant instance ID

        Returns:
            Dictionary with progress statistics
        """
        completed = await self.repository.get_completed_count(instance_id)
        total = await self.repository.get_total_count(instance_id)
        percentage = await self.repository.get_completion_percentage(instance_id)

        return {
            "instance_id": instance_id,
            "completed_items": completed,
            "total_items": total,
            "completion_percentage": percentage
        }

    async def get_incomplete_items(self, instance_id: int) -> List[Dict[str, Any]]:
        """
        Get all incomplete checklist items

        Args:
            instance_id: Plant instance ID

        Returns:
            List of incomplete items
        """
        items = await self.repository.get_incomplete_items(instance_id)

        return [
            {
                "item_key": item.checklist_item_key,
                "is_completed": item.is_completed,
                "user_notes": item.user_notes,
                "created_at": item.created_at
            }
            for item in items
        ]

    async def get_completed_items(self, instance_id: int) -> List[Dict[str, Any]]:
        """
        Get all completed checklist items

        Args:
            instance_id: Plant instance ID

        Returns:
            List of completed items
        """
        items = await self.repository.get_completed_items(instance_id)

        return [
            {
                "item_key": item.checklist_item_key,
                "is_completed": item.is_completed,
                "completed_at": item.completed_at,
                "user_notes": item.user_notes,
                "created_at": item.created_at
            }
            for item in items
        ]

    async def initialize_checklist(
        self,
        instance_id: int,
        plant_id: int
    ) -> Dict[str, Any]:
        """
        Initialize checklist items from requirements data

        Args:
            instance_id: Plant instance ID
            plant_id: Plant ID

        Returns:
            Dictionary with initialization results
        """
        # Get requirements data
        try:
            requirements_data = await self.growth_service.get_requirements(plant_id)
        except ValueError:
            # No growth data available yet
            return {
                "success": False,
                "message": "No growth data available. Generate data first.",
                "items_created": 0
            }

        # Build checklist item keys from requirements
        item_keys = []
        requirements = requirements_data.get("requirements", [])

        for category in requirements:
            category_name = category.get("category", "")
            items = category.get("items", [])

            for item in items:
                item_name = item.get("item", "")
                # Create unique key: category_itemname
                key = f"{category_name.lower().replace(' ', '_')}_{item_name.lower().replace(' ', '_')}"
                item_keys.append(key)

        # Bulk create tracking entries
        created_entries = await self.repository.bulk_create(instance_id, item_keys)

        logger.info(f"Initialized {len(created_entries)} checklist items for instance {instance_id}")

        return {
            "success": True,
            "message": f"Initialized {len(created_entries)} checklist items",
            "items_created": len(created_entries)
        }

    async def get_current_stage_tips(
        self,
        instance_id: int,
        plant_id: int,
        current_stage: str,
        limit: int = 3
    ) -> List[str]:
        """
        Get random tips for the current growth stage

        Args:
            instance_id: Plant instance ID
            plant_id: Plant ID
            current_stage: Current growth stage
            limit: Maximum number of tips to return

        Returns:
            List of tip strings
        """
        import random

        tips_data = await self.growth_service.get_care_tips_for_stage(plant_id, current_stage)
        all_tips = tips_data.get("tips", [])

        if not all_tips:
            return []

        # Extract tip text and shuffle
        tip_texts = [tip.get("tip") for tip in all_tips if tip.get("tip")]
        random.shuffle(tip_texts)

        # Return limited number
        return tip_texts[:limit]

    async def get_stage_info(
        self,
        plant_id: int,
        current_stage: str,
        days_elapsed: int
    ) -> Dict[str, Any]:
        """
        Get information about the current growth stage

        Args:
            plant_id: Plant ID
            current_stage: Current stage name
            days_elapsed: Days since planting

        Returns:
            Dictionary with stage information
        """
        timeline_data = await self.growth_service.get_timeline(plant_id)
        stages = timeline_data.get("stages", [])

        # Find current stage
        stage_info = None
        for stage in stages:
            if stage.get("stage_name") == current_stage:
                stage_info = stage
                break

        if not stage_info:
            return {
                "stage_name": current_stage,
                "description": "No description available",
                "days_in_stage": 0,
                "estimated_days_remaining": 0
            }

        # Calculate days in stage and remaining
        start_day = stage_info.get("start_day", 0)
        end_day = stage_info.get("end_day", 0)

        days_in_stage = max(0, days_elapsed - start_day)
        estimated_days_remaining = max(0, end_day - days_elapsed)

        return {
            "stage_name": current_stage,
            "description": stage_info.get("description", ""),
            "days_in_stage": days_in_stage,
            "estimated_days_remaining": estimated_days_remaining
        }

    async def get_all_tracking_data(self, instance_id: int) -> List[Dict[str, Any]]:
        """
        Get all tracking data for an instance

        Args:
            instance_id: Plant instance ID

        Returns:
            List of all tracking entries
        """
        entries = await self.repository.get_by_instance(instance_id)

        return [
            {
                "id": entry.id,
                "item_key": entry.checklist_item_key,
                "is_completed": entry.is_completed,
                "completed_at": entry.completed_at,
                "user_notes": entry.user_notes,
                "created_at": entry.created_at
            }
            for entry in entries
        ]

    async def get_checklist_with_details(
        self,
        instance_id: int,
        plant_id: int
    ) -> Dict[str, Any]:
        """
        Get checklist items with full details from requirements data

        Args:
            instance_id: Plant instance ID
            plant_id: Plant ID

        Returns:
            Dictionary with detailed checklist items and progress summary
        """
        # Get requirements data to get item details
        try:
            requirements_data = await self.growth_service.get_requirements(plant_id)
        except ValueError:
            return {
                "instance_id": instance_id,
                "checklist_items": [],
                "progress_summary": {
                    "total_items": 0,
                    "completed_items": 0,
                    "completion_percentage": 0.0
                }
            }

        # Get tracking data for this instance
        tracking_entries = await self.repository.get_by_instance(instance_id)

        # Build a map of item_key -> tracking entry
        tracking_map = {entry.checklist_item_key: entry for entry in tracking_entries}

        # Build detailed checklist items
        checklist_items = []
        requirements = requirements_data.get("requirements", [])

        for category in requirements:
            category_name = category.get("category", "")
            items = category.get("items", [])

            for item in items:
                item_name = item.get("item", "")
                quantity = item.get("quantity", "")
                optional = item.get("optional", False)
                notes = item.get("notes")

                # Create unique key matching initialization logic
                key = f"{category_name.lower().replace(' ', '_')}_{item_name.lower().replace(' ', '_')}"

                # Check if this item has tracking data
                tracking_entry = tracking_map.get(key)

                checklist_items.append({
                    "item_key": key,
                    "category": category_name,
                    "item_name": item_name,
                    "quantity": quantity,
                    "optional": optional,
                    "is_completed": tracking_entry.is_completed if tracking_entry else False,
                    "completed_at": tracking_entry.completed_at if tracking_entry else None,
                    "user_notes": tracking_entry.user_notes if tracking_entry else None
                })

        # Calculate progress summary
        total_items = len(checklist_items)
        completed_items = sum(1 for item in checklist_items if item["is_completed"])
        completion_percentage = (completed_items / total_items * 100) if total_items > 0 else 0.0

        return {
            "instance_id": instance_id,
            "checklist_items": checklist_items,
            "progress_summary": {
                "total_items": total_items,
                "completed_items": completed_items,
                "completion_percentage": round(completion_percentage, 2)
            }
        }

    async def delete_all_tracking(self, instance_id: int) -> int:
        """
        Delete all progress tracking for an instance

        Args:
            instance_id: Plant instance ID

        Returns:
            Number of deleted entries
        """
        count = await self.repository.delete_by_instance(instance_id)

        logger.info(f"Deleted {count} tracking entries for instance {instance_id}")

        return count
