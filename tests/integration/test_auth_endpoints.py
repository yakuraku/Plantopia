"""
Integration tests for authentication endpoints
"""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
import jwt

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    """Test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def mock_user_data():
    """Mock user data for testing"""
    return {
        'id': 1,
        'google_id': '123456789',
        'email': 'test@example.com',
        'name': 'Test User',
        'avatar_url': 'https://example.com/avatar.jpg',
        'suburb': None,
        'is_active': True,
        'created_at': '2024-01-01T00:00:00',
        'last_login': '2024-01-01T12:00:00'
    }


@pytest.fixture
def mock_profile_data():
    """Mock profile data for testing"""
    return {
        'id': 1,
        'user_id': 1,
        'experience_level': 'beginner',
        'garden_type': 'balcony',
        'climate_goals': 'Reduce carbon footprint',
        'available_space_m2': 10.5,
        'sun_exposure': 'part_sun',
        'has_containers': True,
        'organic_preference': True,
        'budget_level': 'medium',
        'notification_preferences': {'email': True, 'push': False},
        'created_at': '2024-01-01T00:00:00',
        'updated_at': '2024-01-01T00:00:00'
    }


@pytest.fixture
def valid_jwt_token():
    """Generate a valid JWT token for testing"""
    payload = {
        'user_id': 1,
        'email': 'test@example.com'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


class TestGoogleLogin:
    """Tests for Google OAuth login endpoint"""

    @patch('app.services.auth_service.AuthService.authenticate_with_google')
    def test_google_login_success_new_user(self, mock_auth, client, mock_user_data):
        """Test successful Google login for new user"""
        # Arrange
        mock_user = Mock()
        for key, value in mock_user_data.items():
            setattr(mock_user, key, value)

        mock_auth.return_value = (mock_user, "jwt_token_here")

        # Act
        response = client.post(
            "/api/v1/auth/google",
            json={"credential": "google_jwt_token"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_token"] == "jwt_token_here"
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["google_id"] == "123456789"

    @patch('app.services.auth_service.AuthService.authenticate_with_google')
    def test_google_login_success_existing_user(self, mock_auth, client, mock_user_data):
        """Test successful Google login for existing user"""
        # Arrange
        mock_user = Mock()
        for key, value in mock_user_data.items():
            setattr(mock_user, key, value)

        mock_auth.return_value = (mock_user, "jwt_token_here")

        # Act
        response = client.post(
            "/api/v1/auth/google",
            json={"credential": "google_jwt_token"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_token"] == "jwt_token_here"
        assert data["user"]["email"] == "test@example.com"

    @patch('app.services.auth_service.AuthService.authenticate_with_google')
    def test_google_login_invalid_token(self, mock_auth, client):
        """Test Google login with invalid token"""
        # Arrange
        from fastapi import HTTPException
        mock_auth.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )

        # Act
        response = client.post(
            "/api/v1/auth/google",
            json={"credential": "invalid_token"}
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_google_login_missing_credential(self, client):
        """Test Google login with missing credential"""
        # Act
        response = client.post("/api/v1/auth/google", json={})

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_google_login_malformed_request(self, client):
        """Test Google login with malformed request"""
        # Act
        response = client.post("/api/v1/auth/google", json="invalid")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetCurrentUser:
    """Tests for getting current user information"""

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.get_user_profile')
    def test_get_me_success(self, mock_get_profile, mock_get_user, client, mock_user_data, mock_profile_data, valid_jwt_token):
        """Test successfully getting current user info"""
        # Arrange
        mock_user = Mock()
        for key, value in mock_user_data.items():
            setattr(mock_user, key, value)

        mock_profile = Mock()
        for key, value in mock_profile_data.items():
            setattr(mock_profile, key, value)

        mock_get_user.return_value = mock_user
        mock_get_profile.return_value = mock_profile

        # Act
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["profile"]["experience_level"] == "beginner"

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.get_user_profile')
    def test_get_me_no_profile(self, mock_get_profile, mock_get_user, client, mock_user_data, valid_jwt_token):
        """Test getting current user info with no profile"""
        # Arrange
        mock_user = Mock()
        for key, value in mock_user_data.items():
            setattr(mock_user, key, value)

        mock_get_user.return_value = mock_user
        mock_get_profile.return_value = None

        # Act
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["profile"] is None

    def test_get_me_unauthenticated(self, client):
        """Test getting current user info without authentication"""
        # Act
        response = client.get("/api/v1/auth/me")

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_me_invalid_token(self, client):
        """Test getting current user info with invalid token"""
        # Act
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateCurrentUser:
    """Tests for updating current user information"""

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.update_user')
    def test_update_user_success(self, mock_update_user, mock_get_user, client, mock_user_data, valid_jwt_token):
        """Test successfully updating user"""
        # Arrange
        mock_user = Mock()
        for key, value in mock_user_data.items():
            setattr(mock_user, key, value)

        updated_user = Mock()
        updated_data = mock_user_data.copy()
        updated_data['name'] = 'Updated Name'
        for key, value in updated_data.items():
            setattr(updated_user, key, value)

        mock_get_user.return_value = mock_user
        mock_update_user.return_value = updated_user

        # Act
        response = client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"name": "Updated Name"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"

    @patch('app.api.dependencies.get_current_user')
    def test_update_user_no_changes(self, mock_get_user, client, mock_user_data, valid_jwt_token):
        """Test updating user with no actual changes"""
        # Arrange
        mock_user = Mock()
        for key, value in mock_user_data.items():
            setattr(mock_user, key, value)

        mock_get_user.return_value = mock_user

        # Act
        response = client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK


class TestUserProfile:
    """Tests for user profile endpoints"""

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.get_user_profile')
    def test_get_profile_exists(self, mock_get_profile, mock_get_user, client, mock_user_data, mock_profile_data, valid_jwt_token):
        """Test getting existing user profile"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user

        mock_profile = Mock()
        for key, value in mock_profile_data.items():
            setattr(mock_profile, key, value)
        mock_get_profile.return_value = mock_profile

        # Act
        response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["experience_level"] == "beginner"
        assert data["garden_type"] == "balcony"

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.get_user_profile')
    @patch('app.repositories.user_repository.UserRepository.create_or_update_profile')
    def test_get_profile_create_if_missing(self, mock_create_profile, mock_get_profile, mock_get_user, client, mock_profile_data, valid_jwt_token):
        """Test getting profile creates one if missing"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user

        mock_get_profile.return_value = None

        mock_profile = Mock()
        for key, value in mock_profile_data.items():
            setattr(mock_profile, key, value)
        mock_create_profile.return_value = mock_profile

        # Act
        response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_create_profile.assert_called_once_with(1, {})

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.create_or_update_profile')
    def test_update_profile_success(self, mock_update_profile, mock_get_user, client, mock_profile_data, valid_jwt_token):
        """Test successfully updating user profile"""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user

        mock_profile = Mock()
        for key, value in mock_profile_data.items():
            setattr(mock_profile, key, value)
        mock_update_profile.return_value = mock_profile

        # Act
        response = client.put(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"experience_level": "intermediate", "garden_type": "backyard"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["experience_level"] == "beginner"  # From mock data


class TestLogout:
    """Tests for logout endpoint"""

    def test_logout_success(self, client):
        """Test successful logout"""
        # Act
        response = client.post("/api/v1/auth/logout")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully logged out"