"""
Guide Repository for managing plant guides and user favorites
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.database import UserGuideFavorite
import logging

logger = logging.getLogger(__name__)


class GuideRepository:
    """Repository for plant guides and user guide favorites"""

    # Base path to markdown files
    GUIDES_BASE_PATH = Path("docs/PROCESSED_MARKDOWN_FILES")

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # GUIDE FILE OPERATIONS
    # ========================================================================

    def get_all_guides(self) -> List[Dict[str, Any]]:
        """
        Get all available guide files organized by category

        Returns:
            List of guide dictionaries with category and filename info
        """
        guides = []

        if not self.GUIDES_BASE_PATH.exists():
            logger.warning(f"Guides directory not found: {self.GUIDES_BASE_PATH}")
            return guides

        # Walk through all subdirectories
        for category_path in self.GUIDES_BASE_PATH.iterdir():
            if category_path.is_dir():
                category = category_path.name

                for guide_file in category_path.glob("*.md"):
                    guides.append({
                        "category": category,
                        "guide_name": guide_file.name,
                        "title": guide_file.stem,  # Filename without extension
                        "path": str(guide_file.relative_to(self.GUIDES_BASE_PATH))
                    })

        return guides

    def get_guides_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all guides in a specific category

        Args:
            category: Category name (subdirectory name)

        Returns:
            List of guide dictionaries in that category
        """
        guides = []
        category_path = self.GUIDES_BASE_PATH / category

        if not category_path.exists() or not category_path.is_dir():
            logger.warning(f"Category not found: {category}")
            return guides

        for guide_file in category_path.glob("*.md"):
            guides.append({
                "category": category,
                "guide_name": guide_file.name,
                "title": guide_file.stem,
                "path": str(guide_file.relative_to(self.GUIDES_BASE_PATH))
            })

        return guides

    def get_guide_content(self, category: str, guide_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the full content of a specific guide

        Args:
            category: Category name
            guide_name: Guide filename (with .md extension)

        Returns:
            Dictionary with guide info and content, or None if not found
        """
        guide_path = self.GUIDES_BASE_PATH / category / guide_name

        if not guide_path.exists():
            logger.warning(f"Guide not found: {category}/{guide_name}")
            return None

        try:
            with open(guide_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "category": category,
                "guide_name": guide_name,
                "title": guide_path.stem,
                "content": content,
                "path": str(guide_path.relative_to(self.GUIDES_BASE_PATH))
            }
        except Exception as e:
            logger.error(f"Error reading guide {category}/{guide_name}: {str(e)}")
            return None

    def get_categories(self) -> List[str]:
        """
        Get all available guide categories

        Returns:
            List of category names
        """
        if not self.GUIDES_BASE_PATH.exists():
            return []

        categories = [
            d.name for d in self.GUIDES_BASE_PATH.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        return sorted(categories)

    # ========================================================================
    # USER GUIDE FAVORITES OPERATIONS
    # ========================================================================

    async def add_guide_favorite(
        self,
        user_id: int,
        guide_name: str,
        category: Optional[str] = None,
        notes: Optional[str] = None
    ) -> UserGuideFavorite:
        """
        Add a guide to user's favorites

        Args:
            user_id: User ID
            guide_name: Guide filename
            category: Optional category
            notes: Optional user notes

        Returns:
            Created UserGuideFavorite instance

        Raises:
            ValueError: If favorite already exists
        """
        # Check if already favorited
        stmt = select(UserGuideFavorite).where(
            UserGuideFavorite.user_id == user_id,
            UserGuideFavorite.guide_name == guide_name
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError(f"Guide {guide_name} is already in user's favorites")

        # Create new favorite
        favorite = UserGuideFavorite(
            user_id=user_id,
            guide_name=guide_name,
            category=category,
            notes=notes
        )

        self.db.add(favorite)
        await self.db.commit()
        await self.db.refresh(favorite)

        logger.info(f"Added guide favorite {guide_name} for user {user_id}")
        return favorite

    async def remove_guide_favorite(self, user_id: int, guide_name: str) -> bool:
        """
        Remove a guide from user's favorites

        Args:
            user_id: User ID
            guide_name: Guide filename

        Returns:
            True if removed, False if not found
        """
        stmt = delete(UserGuideFavorite).where(
            UserGuideFavorite.user_id == user_id,
            UserGuideFavorite.guide_name == guide_name
        )
        result = await self.db.execute(stmt)
        await self.db.commit()

        if result.rowcount > 0:
            logger.info(f"Removed guide favorite {guide_name} for user {user_id}")
            return True
        return False

    async def get_user_guide_favorites(self, user_id: int) -> List[UserGuideFavorite]:
        """
        Get all guide favorites for a user

        Args:
            user_id: User ID

        Returns:
            List of UserGuideFavorite instances
        """
        stmt = select(UserGuideFavorite).where(
            UserGuideFavorite.user_id == user_id
        ).order_by(UserGuideFavorite.created_at.desc())

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def is_guide_favorite(self, user_id: int, guide_name: str) -> bool:
        """
        Check if a guide is in user's favorites

        Args:
            user_id: User ID
            guide_name: Guide filename

        Returns:
            True if favorited, False otherwise
        """
        stmt = select(UserGuideFavorite).where(
            UserGuideFavorite.user_id == user_id,
            UserGuideFavorite.guide_name == guide_name
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
