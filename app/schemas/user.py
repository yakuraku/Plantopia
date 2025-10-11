"""
Pydantic schemas for user management and authentication
"""
from __future__ import annotations
from pydantic import BaseModel, Field
try:
    from pydantic import EmailStr
except ImportError:
    # Fallback for older versions of pydantic
    EmailStr = str
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    google_id: str = Field(..., description="Google OAuth sub claim")
    email: EmailStr = Field(..., description="User email address")
    name: Optional[str] = Field(None, description="User display name")
    avatar_url: Optional[str] = Field(None, description="Google profile picture URL")
    suburb_name: Optional[str] = Field(None, description="Suburb name for location")


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = Field(None, description="User display name")
    suburb_name: Optional[str] = Field(None, description="Suburb name for location")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")


class UserProfileCreate(BaseModel):
    """Schema for creating user profile"""
    experience_level: Optional[str] = Field(None, description="beginner/intermediate/advanced")
    garden_type: Optional[str] = Field(None, description="balcony/backyard/indoor/courtyard/community_garden")
    climate_goals: Optional[str] = Field(None, description="User's sustainability goals")
    available_space_m2: Optional[float] = Field(None, description="Available gardening space in square meters")
    sun_exposure: Optional[str] = Field(None, description="full_sun/part_sun/bright_shade/low_light")
    has_containers: Optional[bool] = Field(None, description="Whether user has containers for gardening")
    organic_preference: Optional[bool] = Field(None, description="Preference for organic gardening")
    budget_level: Optional[str] = Field(None, description="low/medium/high budget level")
    notification_preferences: Optional[Dict[str, Any]] = Field(None, description="Notification preferences")


class UserProfileUpdate(UserProfileCreate):
    """Schema for updating user profile (same as create, all optional)"""
    pass


class SuburbInfo(BaseModel):
    """Suburb information schema"""
    id: int = Field(..., description="Suburb ID")
    name: str = Field(..., description="Suburb name")
    postcode: Optional[str] = Field(None, description="Postcode")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")


class UserResponse(BaseModel):
    """Schema for user response data"""
    id: int = Field(..., description="User ID")
    google_id: str = Field(..., description="Google OAuth sub claim")
    email: str = Field(..., description="User email address")
    name: Optional[str] = Field(None, description="User display name")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    suburb: Optional[SuburbInfo] = Field(None, description="User's suburb information")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Schema for user profile response data"""
    id: int = Field(..., description="Profile ID")
    user_id: int = Field(..., description="User ID")
    experience_level: Optional[str] = Field(None, description="User's gardening experience level")
    garden_type: Optional[str] = Field(None, description="Type of garden space")
    climate_goals: Optional[str] = Field(None, description="User's sustainability goals")
    available_space_m2: Optional[float] = Field(None, description="Available gardening space")
    sun_exposure: Optional[str] = Field(None, description="Available sun exposure")
    has_containers: bool = Field(..., description="Whether user has containers")
    organic_preference: bool = Field(..., description="Preference for organic gardening")
    budget_level: Optional[str] = Field(None, description="Budget level")
    notification_preferences: Optional[Dict[str, Any]] = Field(None, description="Notification preferences")
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Profile last update timestamp")

    class Config:
        from_attributes = True


class UserWithProfileResponse(UserResponse):
    """Schema for user response with profile data"""
    profile: Optional[UserProfileResponse] = Field(None, description="User profile information")


class FavoriteCreate(BaseModel):
    """Schema for creating a favorite plant"""
    email: str = Field(..., description="User email address")
    plant_id: int = Field(..., description="Plant ID to favorite")
    notes: Optional[str] = Field(None, description="User notes about why they favorited this plant")


class FavoriteResponse(BaseModel):
    """Schema for favorite plant response"""
    id: int = Field(..., description="Favorite ID")
    plant_id: int = Field(..., description="Plant ID")
    plant_name: str = Field(..., description="Plant name")
    plant_category: str = Field(..., description="Plant category")
    notes: Optional[str] = Field(None, description="User notes")
    priority_level: int = Field(..., description="Priority level for sorting")
    created_at: datetime = Field(..., description="When favorited")

    class Config:
        from_attributes = True


class FavoriteSyncRequest(BaseModel):
    """Schema for syncing favorites from localStorage"""
    email: str = Field(..., description="User email address")
    favorite_plant_ids: List[int] = Field(..., description="List of plant IDs to sync from localStorage")


class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth authentication request"""
    credential: str = Field(..., description="JWT token from Google OAuth")


class AuthResponse(BaseModel):
    """Schema for authentication response"""
    user: UserResponse = Field(..., description="User information")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Schema for JWT token data"""
    user_id: Optional[int] = Field(None, description="User ID from token")
    email: Optional[str] = Field(None, description="Email from token")