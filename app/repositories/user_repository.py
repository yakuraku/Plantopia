"""
User repository for managing user data and operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.models.database import User, UserProfile, UserFavorite, Plant, Suburb


class UserRepository:
    """Repository for managing user-related database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID with related data

        Args:
            user_id: User ID

        Returns:
            User instance or None if not found
        """
        query = select(User).options(
            selectinload(User.suburb),
            selectinload(User.profile)
        ).where(User.id == user_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """
        Get user by Google ID

        Args:
            google_id: Google OAuth sub claim

        Returns:
            User instance or None if not found
        """
        query = select(User).options(
            selectinload(User.suburb),
            selectinload(User.profile)
        ).where(User.google_id == google_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address

        Args:
            email: User email

        Returns:
            User instance or None if not found
        """
        query = select(User).options(
            selectinload(User.suburb),
            selectinload(User.profile)
        ).where(func.lower(User.email) == email.lower())

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_user_by_email(self, email: str, user_data: Dict[str, Any]) -> User:
        """
        Get user by email or create if doesn't exist

        Args:
            email: User email (primary identifier)
            user_data: Dictionary containing user information (name, suburb_id, etc)

        Returns:
            User instance (existing or newly created)
        """
        # Try to get existing user
        user = await self.get_user_by_email(email)

        if user:
            # Update last_login timestamp for existing user
            user.last_login = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(user)
            return user

        # Create new user if doesn't exist
        user_data['email'] = email
        user_data['google_id'] = None  # No Google auth
        return await self.create_user(user_data)

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user

        Args:
            user_data: Dictionary containing user information

        Returns:
            Created User instance
        """
        # Determine suburb_id from explicit id or suburb_name (prefer explicit id if provided)
        effective_suburb_id = user_data.pop('suburb_id', None)

        if effective_suburb_id is None and 'suburb_name' in user_data:
            suburb_name = user_data.pop('suburb_name')
            suburb = await self._get_suburb_by_name(suburb_name)
            if suburb:
                effective_suburb_id = suburb.id

        user = User(
            suburb_id=effective_suburb_id,
            **user_data
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> User:
        """
        Update user information

        Args:
            user_id: User ID
            user_data: Dictionary containing updated user information

        Returns:
            Updated User instance

        Raises:
            ValueError: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Handle suburb lookup if suburb_name is provided
        if 'suburb_name' in user_data:
            suburb_name = user_data.pop('suburb_name')
            suburb = await self._get_suburb_by_name(suburb_name)
            user_data['suburb_id'] = suburb.id if suburb else None

        # Update user attributes
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_last_login(self, user_id: int) -> None:
        """
        Update user's last login timestamp

        Args:
            user_id: User ID
        """
        user = await self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            await self.db.commit()

    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """
        Get user profile by user ID

        Args:
            user_id: User ID

        Returns:
            UserProfile instance or None if not found
        """
        query = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_or_update_profile(self, user_id: int, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Create or update user profile

        Args:
            user_id: User ID
            profile_data: Dictionary containing profile information

        Returns:
            Created or updated UserProfile instance
        """
        # Check if profile exists
        existing_profile = await self.get_user_profile(user_id)

        if existing_profile:
            # Update existing profile
            for key, value in profile_data.items():
                if hasattr(existing_profile, key) and value is not None:
                    setattr(existing_profile, key, value)

            existing_profile.updated_at = datetime.utcnow()
            profile = existing_profile
        else:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                **profile_data
            )
            self.db.add(profile)

        await self.db.commit()
        await self.db.refresh(profile)

        return profile

    async def get_user_favorites(self, user_id: int) -> List[UserFavorite]:
        """
        Get all user's favorite plants with plant details

        Args:
            user_id: User ID

        Returns:
            List of UserFavorite instances with plant data loaded
        """
        query = select(UserFavorite).options(
            selectinload(UserFavorite.plant)
        ).where(
            UserFavorite.user_id == user_id
        ).order_by(UserFavorite.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def add_favorite(self, user_id: int, plant_id: int, notes: Optional[str] = None) -> UserFavorite:
        """
        Add a plant to user's favorites (upsert behavior)

        Args:
            user_id: User ID
            plant_id: Plant ID
            notes: Optional notes

        Returns:
            UserFavorite instance
        """
        # Check if favorite already exists
        existing_query = select(UserFavorite).where(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.plant_id == plant_id
            )
        )

        result = await self.db.execute(existing_query)
        existing_favorite = result.scalar_one_or_none()

        if existing_favorite:
            # Update existing favorite
            if notes is not None:
                existing_favorite.notes = notes
            favorite = existing_favorite
        else:
            # Create new favorite
            favorite = UserFavorite(
                user_id=user_id,
                plant_id=plant_id,
                notes=notes
            )
            self.db.add(favorite)

        await self.db.commit()
        await self.db.refresh(favorite)

        return favorite

    async def remove_favorite(self, user_id: int, plant_id: int) -> bool:
        """
        Remove a plant from user's favorites

        Args:
            user_id: User ID
            plant_id: Plant ID

        Returns:
            True if favorite was removed, False if not found
        """
        query = select(UserFavorite).where(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.plant_id == plant_id
            )
        )

        result = await self.db.execute(query)
        favorite = result.scalar_one_or_none()

        if favorite:
            await self.db.delete(favorite)
            await self.db.commit()
            return True

        return False

    async def is_favorite(self, user_id: int, plant_id: int) -> bool:
        """
        Check if a plant is in user's favorites

        Args:
            user_id: User ID
            plant_id: Plant ID

        Returns:
            True if plant is favorited, False otherwise
        """
        query = select(UserFavorite).where(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.plant_id == plant_id
            )
        )

        result = await self.db.execute(query)
        favorite = result.scalar_one_or_none()

        return favorite is not None

    async def sync_favorites(self, user_id: int, plant_ids: List[int]) -> List[UserFavorite]:
        """
        Sync favorites from localStorage (merge strategy - don't remove existing)

        Args:
            user_id: User ID
            plant_ids: List of plant IDs to add as favorites

        Returns:
            List of UserFavorite instances (all user's favorites)
        """
        # Get existing favorites
        existing_favorites = await self.get_user_favorites(user_id)
        existing_plant_ids = {fav.plant_id for fav in existing_favorites}

        # Add new favorites that don't exist yet
        new_plant_ids = [pid for pid in plant_ids if pid not in existing_plant_ids]

        for plant_id in new_plant_ids:
            # Verify plant exists before adding
            plant_query = select(Plant).where(Plant.id == plant_id)
            plant_result = await self.db.execute(plant_query)
            plant = plant_result.scalar_one_or_none()

            if plant:
                favorite = UserFavorite(
                    user_id=user_id,
                    plant_id=plant_id,
                    notes="Synced from localStorage"
                )
                self.db.add(favorite)

        if new_plant_ids:
            await self.db.commit()

        # Return all favorites
        return await self.get_user_favorites(user_id)

    async def _get_suburb_by_name(self, suburb_name: str) -> Optional[Suburb]:
        """
        Helper method to get suburb by name

        Args:
            suburb_name: Suburb name

        Returns:
            Suburb instance or None if not found
        """
        query = select(Suburb).where(
            func.lower(Suburb.name) == suburb_name.lower()
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()