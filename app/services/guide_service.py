"""
Guide Service for managing plant guides and user favorites
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.guide_repository import GuideRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class GuideService:
    """Service for plant guides and user guide favorites"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = GuideRepository(db)
        self.user_repository = UserRepository(db)

    # ========================================================================
    # GUIDE LISTING AND RETRIEVAL
    # ========================================================================

    async def get_all_guides(self) -> Dict[str, Any]:
        """
        Get all available plant guides organized by category

        Returns:
            Dictionary with guides list and category info
        """
        guides = self.repository.get_all_guides()
        categories = self.repository.get_categories()

        return {
            "guides": guides,
            "total_count": len(guides),
            "categories": categories,
            "category_count": len(categories)
        }

    async def get_guides_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get all guides in a specific category

        Args:
            category: Category name

        Returns:
            Dictionary with guides in that category

        Raises:
            ValueError: If category not found
        """
        guides = self.repository.get_guides_by_category(category)

        if not guides:
            # Check if category exists
            available_categories = self.repository.get_categories()
            if category not in available_categories:
                raise ValueError(f"Category '{category}' not found")

        return {
            "category": category,
            "guides": guides,
            "count": len(guides)
        }

    async def get_guide_content(self, category: str, guide_name: str) -> Dict[str, Any]:
        """
        Get the full content of a specific guide

        Args:
            category: Category name
            guide_name: Guide filename

        Returns:
            Dictionary with guide content

        Raises:
            ValueError: If guide not found
        """
        guide = self.repository.get_guide_content(category, guide_name)

        if not guide:
            raise ValueError(f"Guide '{guide_name}' not found in category '{category}'")

        return guide

    async def get_categories(self) -> Dict[str, Any]:
        """
        Get all available guide categories

        Returns:
            Dictionary with category list
        """
        categories = self.repository.get_categories()

        return {
            "categories": categories,
            "count": len(categories)
        }

    # ========================================================================
    # USER GUIDE FAVORITES
    # ========================================================================

    async def add_guide_favorite(
        self,
        email: str,
        guide_name: str,
        category: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a guide to user's favorites

        Args:
            email: User email
            guide_name: Guide filename
            category: Optional category
            notes: Optional user notes

        Returns:
            Dictionary with favorite info

        Raises:
            ValueError: If user not found or guide already favorited
        """
        # Get user by email
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        # Verify guide exists
        if category:
            guide = self.repository.get_guide_content(category, guide_name)
            if not guide:
                raise ValueError(f"Guide '{guide_name}' not found in category '{category}'")
        else:
            # If no category provided, search all guides
            all_guides = self.repository.get_all_guides()
            guide_exists = any(g["guide_name"] == guide_name for g in all_guides)
            if not guide_exists:
                raise ValueError(f"Guide '{guide_name}' not found")

        # Add to favorites
        favorite = await self.repository.add_guide_favorite(
            user_id=user.id,
            guide_name=guide_name,
            category=category,
            notes=notes
        )

        logger.info(f"User {email} added guide {guide_name} to favorites")

        return {
            "id": favorite.id,
            "guide_name": favorite.guide_name,
            "category": favorite.category,
            "notes": favorite.notes,
            "created_at": favorite.created_at,
            "message": "Guide added to favorites successfully"
        }

    async def remove_guide_favorite(self, email: str, guide_name: str) -> Dict[str, Any]:
        """
        Remove a guide from user's favorites

        Args:
            email: User email
            guide_name: Guide filename

        Returns:
            Dictionary with success info

        Raises:
            ValueError: If user not found or favorite not found
        """
        # Get user by email
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        # Remove from favorites
        success = await self.repository.remove_guide_favorite(
            user_id=user.id,
            guide_name=guide_name
        )

        if not success:
            raise ValueError(f"Guide '{guide_name}' not found in user's favorites")

        logger.info(f"User {email} removed guide {guide_name} from favorites")

        return {
            "success": True,
            "guide_name": guide_name,
            "message": "Guide removed from favorites successfully"
        }

    async def get_user_guide_favorites(self, email: str) -> Dict[str, Any]:
        """
        Get all guide favorites for a user

        Args:
            email: User email

        Returns:
            Dictionary with user's favorite guides

        Raises:
            ValueError: If user not found
        """
        # Get user by email
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        # Get favorites
        favorites = await self.repository.get_user_guide_favorites(user.id)

        # Enrich with guide content info
        favorites_list = []
        for fav in favorites:
            fav_dict = {
                "id": fav.id,
                "guide_name": fav.guide_name,
                "category": fav.category,
                "notes": fav.notes,
                "created_at": fav.created_at
            }

            # Try to get guide details
            if fav.category:
                guide = self.repository.get_guide_content(fav.category, fav.guide_name)
                if guide:
                    fav_dict["title"] = guide["title"]
                    fav_dict["path"] = guide["path"]

            favorites_list.append(fav_dict)

        return {
            "favorites": favorites_list,
            "count": len(favorites_list)
        }

    async def check_guide_favorite(self, email: str, guide_name: str) -> Dict[str, Any]:
        """
        Check if a guide is in user's favorites

        Args:
            email: User email
            guide_name: Guide filename

        Returns:
            Dictionary with favorite status

        Raises:
            ValueError: If user not found
        """
        # Get user by email
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        # Check if favorited
        is_favorite = await self.repository.is_guide_favorite(user.id, guide_name)

        return {
            "guide_name": guide_name,
            "is_favorite": is_favorite
        }
