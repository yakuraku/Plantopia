"""
Plant Instance Repository for managing user plant instance operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from app.models.database import UserPlantInstance, Plant, User


class PlantInstanceRepository:
    """Repository for managing user plant instance database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, instance_id: int) -> Optional[UserPlantInstance]:
        """
        Get plant instance by ID with related data

        Args:
            instance_id: Plant instance ID

        Returns:
            UserPlantInstance instance or None if not found
        """
        query = select(UserPlantInstance).options(
            selectinload(UserPlantInstance.plant),
            selectinload(UserPlantInstance.user),
            selectinload(UserPlantInstance.progress_tracking)
        ).where(UserPlantInstance.id == instance_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_instances(
        self,
        user_id: int,
        active_only: bool = True,
        limit: int = 20,
        offset: int = 0
    ) -> List[UserPlantInstance]:
        """
        Get all plant instances for a user

        Args:
            user_id: User ID
            active_only: If True, only return active instances
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of UserPlantInstance instances
        """
        query = select(UserPlantInstance).options(
            selectinload(UserPlantInstance.plant),
            selectinload(UserPlantInstance.progress_tracking)
        ).where(UserPlantInstance.user_id == user_id)

        if active_only:
            query = query.where(UserPlantInstance.is_active == True)

        query = query.order_by(desc(UserPlantInstance.created_at)).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_user_instances(self, user_id: int, active_only: bool = True) -> int:
        """
        Count total plant instances for a user

        Args:
            user_id: User ID
            active_only: If True, only count active instances

        Returns:
            Total count
        """
        query = select(func.count(UserPlantInstance.id)).where(
            UserPlantInstance.user_id == user_id
        )

        if active_only:
            query = query.where(UserPlantInstance.is_active == True)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def create(self, instance_data: Dict[str, Any]) -> UserPlantInstance:
        """
        Create new plant instance

        Args:
            instance_data: Dictionary containing instance information

        Returns:
            Created UserPlantInstance instance
        """
        instance = UserPlantInstance(**instance_data)

        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)

        return instance

    async def update(self, instance_id: int, instance_data: Dict[str, Any]) -> UserPlantInstance:
        """
        Update plant instance

        Args:
            instance_id: Plant instance ID
            instance_data: Dictionary containing updated information

        Returns:
            Updated UserPlantInstance instance

        Raises:
            ValueError: If instance not found
        """
        instance = await self.get_by_id(instance_id)
        if not instance:
            raise ValueError(f"Plant instance with ID {instance_id} not found")

        # Update fields
        for key, value in instance_data.items():
            if hasattr(instance, key) and value is not None:
                setattr(instance, key, value)

        instance.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(instance)

        return instance

    async def deactivate(self, instance_id: int) -> UserPlantInstance:
        """
        Deactivate a plant instance (soft delete)

        Args:
            instance_id: Plant instance ID

        Returns:
            Updated UserPlantInstance instance

        Raises:
            ValueError: If instance not found
        """
        return await self.update(instance_id, {'is_active': False})

    async def delete(self, instance_id: int) -> bool:
        """
        Delete a plant instance (hard delete)

        Args:
            instance_id: Plant instance ID

        Returns:
            True if deleted, False if not found
        """
        instance = await self.get_by_id(instance_id)

        if instance:
            await self.db.delete(instance)
            await self.db.commit()
            return True

        return False

    async def update_stage(self, instance_id: int, new_stage: str) -> UserPlantInstance:
        """
        Update the current growth stage of a plant instance

        Args:
            instance_id: Plant instance ID
            new_stage: New stage name

        Returns:
            Updated UserPlantInstance instance
        """
        return await self.update(instance_id, {'current_stage': new_stage})

    async def get_instances_by_stage(
        self,
        user_id: int,
        stage: str,
        active_only: bool = True
    ) -> List[UserPlantInstance]:
        """
        Get all plant instances for a user in a specific stage

        Args:
            user_id: User ID
            stage: Growth stage name
            active_only: If True, only return active instances

        Returns:
            List of UserPlantInstance instances
        """
        query = select(UserPlantInstance).options(
            selectinload(UserPlantInstance.plant)
        ).where(
            and_(
                UserPlantInstance.user_id == user_id,
                UserPlantInstance.current_stage == stage
            )
        )

        if active_only:
            query = query.where(UserPlantInstance.is_active == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_instances_by_plant(
        self,
        user_id: int,
        plant_id: int,
        active_only: bool = True
    ) -> List[UserPlantInstance]:
        """
        Get all instances of a specific plant for a user

        Args:
            user_id: User ID
            plant_id: Plant ID
            active_only: If True, only return active instances

        Returns:
            List of UserPlantInstance instances
        """
        query = select(UserPlantInstance).where(
            and_(
                UserPlantInstance.user_id == user_id,
                UserPlantInstance.plant_id == plant_id
            )
        )

        if active_only:
            query = query.where(UserPlantInstance.is_active == True)

        query = query.order_by(desc(UserPlantInstance.created_at))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def calculate_days_elapsed(self, instance_id: int) -> int:
        """
        Calculate days elapsed since start date

        Args:
            instance_id: Plant instance ID

        Returns:
            Number of days elapsed

        Raises:
            ValueError: If instance not found
        """
        instance = await self.get_by_id(instance_id)
        if not instance:
            raise ValueError(f"Plant instance with ID {instance_id} not found")

        today = date.today()
        days_elapsed = (today - instance.start_date).days

        return max(0, days_elapsed)  # Ensure non-negative

    async def get_maturing_soon(
        self,
        user_id: int,
        days_threshold: int = 7
    ) -> List[UserPlantInstance]:
        """
        Get plant instances that will mature within the specified days

        Args:
            user_id: User ID
            days_threshold: Number of days to look ahead

        Returns:
            List of UserPlantInstance instances
        """
        target_date = date.today() + timedelta(days=days_threshold)

        query = select(UserPlantInstance).options(
            selectinload(UserPlantInstance.plant)
        ).where(
            and_(
                UserPlantInstance.user_id == user_id,
                UserPlantInstance.is_active == True,
                UserPlantInstance.expected_maturity_date <= target_date,
                UserPlantInstance.expected_maturity_date >= date.today()
            )
        ).order_by(UserPlantInstance.expected_maturity_date)

        result = await self.db.execute(query)
        return list(result.scalars().all())


# Import timedelta for maturing_soon method
from datetime import timedelta
