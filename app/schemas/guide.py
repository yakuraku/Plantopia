"""
Pydantic schemas for plant guides and favorites
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# GUIDE SCHEMAS
# ============================================================================

class GuideInfo(BaseModel):
    """Schema for guide information"""
    category: str = Field(..., description="Guide category")
    guide_name: str = Field(..., description="Guide filename")
    title: str = Field(..., description="Guide title (filename without extension)")
    path: str = Field(..., description="Relative path from guides base")


class GuideContent(BaseModel):
    """Schema for guide with full content"""
    category: str = Field(..., description="Guide category")
    guide_name: str = Field(..., description="Guide filename")
    title: str = Field(..., description="Guide title")
    content: str = Field(..., description="Full markdown content")
    path: str = Field(..., description="Relative path from guides base")


class GuideListResponse(BaseModel):
    """Schema for guide list response"""
    guides: List[GuideInfo] = Field(..., description="List of guides")
    total_count: int = Field(..., description="Total number of guides")
    categories: List[str] = Field(..., description="Available categories")
    category_count: int = Field(..., description="Number of categories")


class CategoryGuidesResponse(BaseModel):
    """Schema for guides by category response"""
    category: str = Field(..., description="Category name")
    guides: List[GuideInfo] = Field(..., description="Guides in this category")
    count: int = Field(..., description="Number of guides in category")


class CategoriesResponse(BaseModel):
    """Schema for categories list response"""
    categories: List[str] = Field(..., description="Available categories")
    count: int = Field(..., description="Number of categories")


# ============================================================================
# GUIDE FAVORITES SCHEMAS
# ============================================================================

class GuideFavoriteCreate(BaseModel):
    """Schema for creating a guide favorite"""
    email: str = Field(..., description="User email address")
    guide_name: str = Field(..., description="Guide filename")
    category: Optional[str] = Field(None, description="Guide category (optional)")
    notes: Optional[str] = Field(None, description="User notes about this guide")


class GuideFavoriteResponse(BaseModel):
    """Schema for guide favorite response"""
    id: int = Field(..., description="Favorite ID")
    guide_name: str = Field(..., description="Guide filename")
    category: Optional[str] = Field(None, description="Guide category")
    notes: Optional[str] = Field(None, description="User notes")
    title: Optional[str] = Field(None, description="Guide title (if available)")
    path: Optional[str] = Field(None, description="Guide path (if available)")
    created_at: datetime = Field(..., description="When favorited")

    class Config:
        from_attributes = True


class UserGuideFavoritesResponse(BaseModel):
    """Schema for user's guide favorites list"""
    favorites: List[GuideFavoriteResponse] = Field(..., description="User's favorite guides")
    count: int = Field(..., description="Number of favorites")


class GuideFavoriteRemoveResponse(BaseModel):
    """Schema for guide favorite removal response"""
    success: bool = Field(..., description="Whether removal was successful")
    guide_name: str = Field(..., description="Guide filename that was removed")
    message: str = Field(..., description="Success message")


class GuideFavoriteCheckResponse(BaseModel):
    """Schema for checking if guide is favorited"""
    guide_name: str = Field(..., description="Guide filename")
    is_favorite: bool = Field(..., description="Whether guide is in user's favorites")
