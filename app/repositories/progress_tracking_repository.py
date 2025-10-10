"""
Progress Tracking Repository for managing user progress tracking operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.database import UserProgressTracking


class ProgressTrackingRepository:
    """Repository for managing progress tracking database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, tracking_id: int) -> Optional[UserProgressTracking]:
        """
        Get progress tracking entry by ID

        Args:
            tracking_id: Progress tracking ID

        Returns:
            UserProgressTracking instance or None if not found
        """
        query = select(UserProgressTracking).where(UserProgressTracking.id == tracking_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_instance(self, instance_id: int) -> List[UserProgressTracking]:
        """
        Get all progress tracking entries for a plant instance

        Args:
            instance_id: Plant instance ID

        Returns:
            List of UserProgressTracking instances
        """
        query = select(UserProgressTracking).where(
            UserProgressTracking.user_plant_instance_id == instance_id
        ).order_by(UserProgressTracking.created_at)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_item_key(
        self,
        instance_id: int,
        checklist_item_key: str
    ) -> Optional[UserProgressTracking]:
        """
        Get progress tracking entry by instance and checklist item key

        Args:
            instance_id: Plant instance ID
            checklist_item_key: Checklist item key

        Returns:
            UserProgressTracking instance or None if not found
        """
        query = select(UserProgressTracking).where(
            and_(
                UserProgressTracking.user_plant_instance_id == instance_id,
                UserProgressTracking.checklist_item_key == checklist_item_key
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, tracking_data: Dict[str, Any]) -> UserProgressTracking:
        """
        Create new progress tracking entry

        Args:
            tracking_data: Dictionary containing tracking information

        Returns:
            Created UserProgressTracking instance
        """
        tracking = UserProgressTracking(**tracking_data)

        self.db.add(tracking)
        await self.db.commit()
        await self.db.refresh(tracking)

        return tracking

    async def update(self, tracking_id: int, tracking_data: Dict[str, Any]) -> UserProgressTracking:
        """
        Update progress tracking entry

        Args:
            tracking_id: Progress tracking ID
            tracking_data: Dictionary containing updated information

        Returns:
            Updated UserProgressTracking instance

        Raises:
            ValueError: If tracking entry not found
        """
        tracking = await self.get_by_id(tracking_id)
        if not tracking:
            raise ValueError(f"Progress tracking with ID {tracking_id} not found")

        # Update fields
        for key, value in tracking_data.items():
            if hasattr(tracking, key):
                setattr(tracking, key, value)

        await self.db.commit()
        await self.db.refresh(tracking)

        return tracking

    async def mark_complete(
        self,
        instance_id: int,
        checklist_item_key: str,
        is_completed: bool = True,
        user_notes: Optional[str] = None
    ) -> UserProgressTracking:
        """
        Mark a checklist item as complete or incomplete (upsert behavior)

        Args:
            instance_id: Plant instance ID
            checklist_item_key: Checklist item key
            is_completed: Completion status
            user_notes: Optional user notes

        Returns:
            UserProgressTracking instance
        """
        # Check if entry already exists
        existing = await self.get_by_item_key(instance_id, checklist_item_key)

        if existing:
            # Update existing entry
            existing.is_completed = is_completed
            if is_completed and not existing.completed_at:
                existing.completed_at = datetime.utcnow()
            elif not is_completed:
                existing.completed_at = None

            if user_notes is not None:
                existing.user_notes = user_notes

            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new entry
            tracking_data = {
                'user_plant_instance_id': instance_id,
                'checklist_item_key': checklist_item_key,
                'is_completed': is_completed,
                'completed_at': datetime.utcnow() if is_completed else None,
                'user_notes': user_notes
            }
            return await self.create(tracking_data)

    async def get_completed_count(self, instance_id: int) -> int:
        """
        Get count of completed items for a plant instance

        Args:
            instance_id: Plant instance ID

        Returns:
            Number of completed items
        """
        query = select(func.count(UserProgressTracking.id)).where(
            and_(
                UserProgressTracking.user_plant_instance_id == instance_id,
                UserProgressTracking.is_completed == True
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_total_count(self, instance_id: int) -> int:
        """
        Get total count of tracking entries for a plant instance

        Args:
            instance_id: Plant instance ID

        Returns:
            Total number of tracking entries
        """
        query = select(func.count(UserProgressTracking.id)).where(
            UserProgressTracking.user_plant_instance_id == instance_id
        )

        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_completion_percentage(self, instance_id: int) -> float:
        """
        Calculate completion percentage for a plant instance

        Args:
            instance_id: Plant instance ID

        Returns:
            Completion percentage (0-100)
        """
        total = await self.get_total_count(instance_id)
        if total == 0:
            return 0.0

        completed = await self.get_completed_count(instance_id)
        return round((completed / total) * 100, 2)

    async def get_incomplete_items(self, instance_id: int) -> List[UserProgressTracking]:
        """
        Get all incomplete tracking entries for a plant instance

        Args:
            instance_id: Plant instance ID

        Returns:
            List of incomplete UserProgressTracking instances
        """
        query = select(UserProgressTracking).where(
            and_(
                UserProgressTracking.user_plant_instance_id == instance_id,
                UserProgressTracking.is_completed == False
            )
        ).order_by(UserProgressTracking.created_at)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_completed_items(self, instance_id: int) -> List[UserProgressTracking]:
        """
        Get all completed tracking entries for a plant instance

        Args:
            instance_id: Plant instance ID

        Returns:
            List of completed UserProgressTracking instances
        """
        query = select(UserProgressTracking).where(
            and_(
                UserProgressTracking.user_plant_instance_id == instance_id,
                UserProgressTracking.is_completed == True
            )
        ).order_by(UserProgressTracking.completed_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_by_instance(self, instance_id: int) -> int:
        """
        Delete all progress tracking entries for a plant instance

        Args:
            instance_id: Plant instance ID

        Returns:
            Number of deleted entries
        """
        tracking_entries = await self.get_by_instance(instance_id)

        count = 0
        for entry in tracking_entries:
            await self.db.delete(entry)
            count += 1

        if count > 0:
            await self.db.commit()

        return count

    async def bulk_create(
        self,
        instance_id: int,
        checklist_item_keys: List[str]
    ) -> List[UserProgressTracking]:
        """
        Bulk create progress tracking entries for checklist items

        Args:
            instance_id: Plant instance ID
            checklist_item_keys: List of checklist item keys

        Returns:
            List of created UserProgressTracking instances
        """
        created_entries = []

        for key in checklist_item_keys:
            # Check if entry already exists
            existing = await self.get_by_item_key(instance_id, key)

            if not existing:
                tracking_data = {
                    'user_plant_instance_id': instance_id,
                    'checklist_item_key': key,
                    'is_completed': False
                }
                tracking = UserProgressTracking(**tracking_data)
                self.db.add(tracking)
                created_entries.append(tracking)

        if created_entries:
            await self.db.commit()
            # Refresh all created entries
            for entry in created_entries:
                await self.db.refresh(entry)

        return created_entries
