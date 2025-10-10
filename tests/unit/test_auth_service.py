"""
Unit tests for the authentication service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.core.config import settings
from app.models.database import User


@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_db):
    """Auth service instance with mocked database"""
    return AuthService(mock_db)


@pytest.fixture
def mock_user():
    """Mock user instance"""
    user = Mock(spec=User)
    user.id = 1
    user.google_id = "123456789"
    user.email = "test@example.com"
    user.name = "Test User"
    user.is_active = True
    user.avatar_url = "https://example.com/avatar.jpg"
    return user


class TestVerifyGoogleToken:
    """Tests for Google token verification"""

    @patch('app.services.auth_service.id_token.verify_oauth2_token')
    async def test_verify_valid_google_token(self, mock_verify, auth_service):
        """Test verification of a valid Google token"""
        # Arrange
        mock_verify.return_value = {
            'iss': 'accounts.google.com',
            'sub': '123456789',
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg'
        }

        # Act
        result = await auth_service.verify_google_token("valid_token")

        # Assert
        assert result['google_id'] == '123456789'
        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'
        assert result['picture'] == 'https://example.com/avatar.jpg'
        mock_verify.assert_called_once()

    @patch('app.services.auth_service.id_token.verify_oauth2_token')
    async def test_verify_invalid_issuer(self, mock_verify, auth_service):
        """Test verification fails with invalid issuer"""
        # Arrange
        mock_verify.return_value = {
            'iss': 'malicious.com',
            'sub': '123456789',
            'email': 'test@example.com'
        }

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.verify_google_token("invalid_token")

        assert exc_info.value.status_code == 401
        assert "Invalid token issuer" in str(exc_info.value.detail)

    @patch('app.services.auth_service.id_token.verify_oauth2_token')
    async def test_verify_token_value_error(self, mock_verify, auth_service):
        """Test verification handles ValueError from Google API"""
        # Arrange
        mock_verify.side_effect = ValueError("Token verification failed")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.verify_google_token("invalid_token")

        assert exc_info.value.status_code == 401
        assert "Invalid Google token" in str(exc_info.value.detail)

    @patch('app.services.auth_service.id_token.verify_oauth2_token')
    async def test_verify_token_unexpected_error(self, mock_verify, auth_service):
        """Test verification handles unexpected errors"""
        # Arrange
        mock_verify.side_effect = Exception("Unexpected error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.verify_google_token("invalid_token")

        assert exc_info.value.status_code == 500
        assert "Token verification failed" in str(exc_info.value.detail)


class TestCreateAccessToken:
    """Tests for JWT access token creation"""

    def test_create_access_token_default_expiry(self, auth_service):
        """Test creating access token with default expiry"""
        # Arrange
        data = {"user_id": 1, "email": "test@example.com"}

        # Act
        token = auth_service.create_access_token(data)

        # Assert
        assert isinstance(token, str)

        # Decode and verify token
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["user_id"] == 1
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded

    def test_create_access_token_custom_expiry(self, auth_service):
        """Test creating access token with custom expiry"""
        # Arrange
        data = {"user_id": 1, "email": "test@example.com"}
        expires_delta = timedelta(minutes=30)

        # Act
        token = auth_service.create_access_token(data, expires_delta)

        # Assert
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Check expiry is approximately 30 minutes from now
        exp_time = datetime.fromtimestamp(decoded["exp"])
        expected_time = datetime.utcnow() + expires_delta
        assert abs((exp_time - expected_time).total_seconds()) < 60  # Within 1 minute


class TestGetCurrentUser:
    """Tests for getting current user from JWT token"""

    @patch('app.repositories.user_repository.UserRepository.get_user_by_id')
    async def test_get_current_user_valid_token(self, mock_get_user, auth_service, mock_user):
        """Test getting current user with valid token"""
        # Arrange
        data = {"user_id": 1, "email": "test@example.com"}
        token = auth_service.create_access_token(data)
        mock_get_user.return_value = mock_user

        # Act
        result = await auth_service.get_current_user(token)

        # Assert
        assert result == mock_user
        mock_get_user.assert_called_once_with(1)

    async def test_get_current_user_invalid_token(self, auth_service):
        """Test getting current user with invalid token"""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.get_current_user("invalid_token")

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)

    @patch('app.repositories.user_repository.UserRepository.get_user_by_id')
    async def test_get_current_user_not_found(self, mock_get_user, auth_service):
        """Test getting current user when user not found in database"""
        # Arrange
        data = {"user_id": 999, "email": "test@example.com"}
        token = auth_service.create_access_token(data)
        mock_get_user.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.get_current_user(token)

        assert exc_info.value.status_code == 401

    @patch('app.repositories.user_repository.UserRepository.get_user_by_id')
    async def test_get_current_user_inactive(self, mock_get_user, auth_service, mock_user):
        """Test getting current user when user is inactive"""
        # Arrange
        mock_user.is_active = False
        data = {"user_id": 1, "email": "test@example.com"}
        token = auth_service.create_access_token(data)
        mock_get_user.return_value = mock_user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.get_current_user(token)

        assert exc_info.value.status_code == 401
        assert "Inactive user" in str(exc_info.value.detail)

    async def test_get_current_user_missing_user_id(self, auth_service):
        """Test getting current user with token missing user_id"""
        # Arrange
        data = {"email": "test@example.com"}  # Missing user_id
        token = auth_service.create_access_token(data)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.get_current_user(token)

        assert exc_info.value.status_code == 401


class TestAuthenticateWithGoogle:
    """Tests for full Google authentication flow"""

    @patch('app.services.auth_service.AuthService.verify_google_token')
    @patch('app.repositories.user_repository.UserRepository.get_user_by_google_id')
    @patch('app.repositories.user_repository.UserRepository.create_user')
    @patch('app.repositories.user_repository.UserRepository.create_or_update_profile')
    async def test_authenticate_new_user(
        self, mock_create_profile, mock_create_user, mock_get_user,
        mock_verify_token, auth_service, mock_user
    ):
        """Test authentication creates new user"""
        # Arrange
        google_info = {
            'google_id': '123456789',
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg'
        }
        mock_verify_token.return_value = google_info
        mock_get_user.return_value = None  # User doesn't exist
        mock_create_user.return_value = mock_user
        mock_create_profile.return_value = Mock()

        # Act
        user, token = await auth_service.authenticate_with_google("google_token")

        # Assert
        assert user == mock_user
        assert isinstance(token, str)
        mock_create_user.assert_called_once()
        mock_create_profile.assert_called_once_with(mock_user.id, {})

    @patch('app.services.auth_service.AuthService.verify_google_token')
    @patch('app.repositories.user_repository.UserRepository.get_user_by_google_id')
    @patch('app.repositories.user_repository.UserRepository.update_last_login')
    @patch('app.repositories.user_repository.UserRepository.update_user')
    async def test_authenticate_existing_user(
        self, mock_update_user, mock_update_login, mock_get_user,
        mock_verify_token, auth_service, mock_user
    ):
        """Test authentication with existing user"""
        # Arrange
        google_info = {
            'google_id': '123456789',
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': 'https://example.com/new_avatar.jpg'
        }
        mock_user.avatar_url = 'https://example.com/old_avatar.jpg'
        mock_verify_token.return_value = google_info
        mock_get_user.return_value = mock_user
        mock_update_login.return_value = None
        mock_update_user.return_value = mock_user

        # Act
        user, token = await auth_service.authenticate_with_google("google_token")

        # Assert
        assert user == mock_user
        assert isinstance(token, str)
        mock_update_login.assert_called_once_with(mock_user.id)
        mock_update_user.assert_called_once()  # Avatar updated

    @patch('app.services.auth_service.AuthService.verify_google_token')
    async def test_authenticate_google_token_invalid(self, mock_verify_token, auth_service):
        """Test authentication with invalid Google token"""
        # Arrange
        mock_verify_token.side_effect = HTTPException(status_code=401, detail="Invalid token")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_with_google("invalid_token")

        assert exc_info.value.status_code == 401