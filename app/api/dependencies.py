"""
FastAPI dependencies for authentication and authorization
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.services.auth_service import AuthService
from app.models.database import User

# OAuth2 scheme for extracting Bearer tokens
oauth2_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Args:
        credentials: HTTP Authorization credentials containing Bearer token
        db: Database session

    Returns:
        Current authenticated User instance

    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_async_db)
) -> Optional[User]:
    """
    Dependency to optionally get current authenticated user from JWT token
    Used for endpoints that work with or without authentication

    Args:
        credentials: Optional HTTP Authorization credentials
        db: Database session

    Returns:
        User instance if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except HTTPException:
        # Authentication failed, but it's optional so return None
        return None


async def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    """
    Dependency to get AuthService instance

    Args:
        db: Database session

    Returns:
        AuthService instance
    """
    return AuthService(db)