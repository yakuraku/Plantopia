"""
Google OAuth authentication service for user management
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from app.core.config import settings
from app.models.database import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """Service for handling Google OAuth authentication and JWT tokens"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def verify_google_token(self, credential: str) -> Dict[str, str]:
        """
        Verify Google OAuth token and extract user information

        Args:
            credential: JWT token from Google OAuth

        Returns:
            Dictionary containing user information from Google

        Raises:
            HTTPException: If token is invalid or verification fails
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                credential,
                Request(),
                settings.GOOGLE_CLIENT_ID
            )

            # Check if token is from the correct issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token issuer"
                )

            # Extract user information
            user_info = {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', '')
            }

            return user_info

        except ValueError as e:
            # Token verification failed
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
        except Exception as e:
            # Unexpected error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token verification failed: {str(e)}"
            )

    def create_access_token(self, data: Dict[str, any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token

        Args:
            data: Dictionary containing token payload data
            expires_delta: Optional expiration time delta

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    async def get_current_user(self, token: str) -> User:
        """
        Get current user from JWT token

        Args:
            token: JWT access token

        Returns:
            User model instance

        Raises:
            HTTPException: If token is invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            user_id: int = payload.get("user_id")
            email: str = payload.get("email")

            if user_id is None or email is None:
                raise credentials_exception

        except jwt.PyJWTError:
            raise credentials_exception

        # Get user from database
        user = await self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )

        return user

    async def authenticate_with_google(self, credential: str) -> tuple[User, str]:
        """
        Authenticate user with Google OAuth and return user + access token

        Args:
            credential: Google OAuth JWT token

        Returns:
            Tuple of (User instance, JWT access token)

        Raises:
            HTTPException: If authentication fails
        """
        # Verify Google token
        google_user_info = await self.verify_google_token(credential)

        # Check if user exists
        user = await self.user_repository.get_user_by_google_id(google_user_info['google_id'])

        if user is None:
            # Create new user
            user_data = {
                'google_id': google_user_info['google_id'],
                'email': google_user_info['email'],
                'name': google_user_info['name'],
                'avatar_url': google_user_info['picture'],
                'is_active': True
            }
            user = await self.user_repository.create_user(user_data)

            # Create empty profile for new user
            await self.user_repository.create_or_update_profile(user.id, {})
        else:
            # Update existing user's last login and avatar
            await self.user_repository.update_last_login(user.id)
            if google_user_info['picture'] and google_user_info['picture'] != user.avatar_url:
                await self.user_repository.update_user(user.id, {
                    'avatar_url': google_user_info['picture']
                })
                user.avatar_url = google_user_info['picture']

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"user_id": user.id, "email": user.email},
            expires_delta=access_token_expires
        )

        return user, access_token