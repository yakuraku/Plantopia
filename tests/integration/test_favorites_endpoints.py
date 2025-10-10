"""
Integration tests for favorites endpoints
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
def mock_user():
    """Mock authenticated user"""
    user = Mock()
    user.id = 1
    user.email = 'test@example.com'
    user.is_active = True
    return user


@pytest.fixture
def mock_favorite_data():
    """Mock favorite data for testing"""
    return {
        'id': 1,
        'plant_id': 1,
        'plant_name': 'Basil',
        'plant_category': 'herb',
        'notes': 'Love this herb',
        'priority_level': 0,
        'created_at': '2024-01-01T00:00:00'
    }


@pytest.fixture
def mock_plant():
    """Mock plant for testing"""
    plant = Mock()
    plant.id = 1
    plant.plant_name = 'Basil'
    plant.plant_category = 'herb'
    return plant


@pytest.fixture
def mock_favorite():
    """Mock favorite instance"""
    favorite = Mock()
    favorite.id = 1
    favorite.plant_id = 1
    favorite.notes = 'Love this herb'
    favorite.priority_level = 0
    favorite.created_at = '2024-01-01T00:00:00'
    return favorite


@pytest.fixture
def valid_jwt_token():
    """Generate a valid JWT token for testing"""
    payload = {
        'user_id': 1,
        'email': 'test@example.com'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


class TestGetUserFavorites:
    """Tests for getting user's favorite plants"""

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.get_user_favorites')
    def test_get_favorites_success(self, mock_get_favorites, mock_get_user, client, mock_user, mock_favorite, mock_plant, valid_jwt_token):
        """Test successfully getting user's favorites"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_favorite.plant = mock_plant
        mock_get_favorites.return_value = [mock_favorite]

        # Act
        response = client.get(
            "/api/v1/favorites",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["plant_name"] == "Basil"
        assert data[0]["plant_category"] == "herb"

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.get_user_favorites')
    def test_get_favorites_empty(self, mock_get_favorites, mock_get_user, client, mock_user, valid_jwt_token):
        """Test getting favorites when user has none"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_get_favorites.return_value = []

        # Act
        response = client.get(
            "/api/v1/favorites",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0

    def test_get_favorites_unauthenticated(self, client):
        """Test getting favorites without authentication"""
        # Act
        response = client.get("/api/v1/favorites")

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAddFavorite:
    """Tests for adding plants to favorites"""

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.add_favorite')
    @patch('app.repositories.user_repository.UserRepository.get_user_favorites')
    def test_add_favorite_success(self, mock_get_favorites, mock_add_favorite, mock_get_user, client, mock_user, mock_favorite, mock_plant, valid_jwt_token):
        """Test successfully adding a favorite"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_add_favorite.return_value = mock_favorite
        mock_favorite.plant = mock_plant
        mock_get_favorites.return_value = [mock_favorite]

        # Act
        response = client.post(
            "/api/v1/favorites",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"plant_id": 1, "notes": "Great herb for cooking"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["plant_id"] == 1
        assert data["plant_name"] == "Basil"
        mock_add_favorite.assert_called_once_with(1, 1, "Great herb for cooking")

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.add_favorite')
    def test_add_favorite_plant_not_found(self, mock_add_favorite, mock_get_user, client, mock_user, valid_jwt_token):
        """Test adding favorite for non-existent plant"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_add_favorite.side_effect = ValueError("Plant not found")

        # Act
        response = client.post(
            "/api/v1/favorites",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"plant_id": 999}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_favorite_missing_plant_id(self, client, valid_jwt_token):
        """Test adding favorite without plant_id"""
        # Act
        response = client.post(
            "/api/v1/favorites",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"notes": "Missing plant ID"}
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_add_favorite_unauthenticated(self, client):
        """Test adding favorite without authentication"""
        # Act
        response = client.post(
            "/api/v1/favorites",
            json={"plant_id": 1}
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRemoveFavorite:
    """Tests for removing plants from favorites"""

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.remove_favorite')
    def test_remove_favorite_success(self, mock_remove_favorite, mock_get_user, client, mock_user, valid_jwt_token):
        """Test successfully removing a favorite"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_remove_favorite.return_value = True

        # Act
        response = client.delete(
            "/api/v1/favorites/1",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "removed successfully" in data["message"]
        mock_remove_favorite.assert_called_once_with(1, 1)

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.remove_favorite')
    def test_remove_favorite_not_found(self, mock_remove_favorite, mock_get_user, client, mock_user, valid_jwt_token):
        """Test removing favorite that doesn't exist"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_remove_favorite.return_value = False

        # Act
        response = client.delete(
            "/api/v1/favorites/999",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_favorite_unauthenticated(self, client):
        """Test removing favorite without authentication"""
        # Act
        response = client.delete("/api/v1/favorites/1")

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSyncFavorites:
    """Tests for syncing favorites from localStorage"""

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.sync_favorites')
    def test_sync_favorites_success(self, mock_sync_favorites, mock_get_user, client, mock_user, mock_favorite, mock_plant, valid_jwt_token):
        """Test successfully syncing favorites"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_favorite.plant = mock_plant
        mock_sync_favorites.return_value = [mock_favorite]

        # Act
        response = client.post(
            "/api/v1/favorites/sync",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"favorite_plant_ids": [1, 2, 3]}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["plant_name"] == "Basil"
        mock_sync_favorites.assert_called_once_with(1, [1, 2, 3])

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.sync_favorites')
    def test_sync_favorites_empty_list(self, mock_sync_favorites, mock_get_user, client, mock_user, valid_jwt_token):
        """Test syncing with empty favorites list"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_sync_favorites.return_value = []

        # Act
        response = client.post(
            "/api/v1/favorites/sync",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"favorite_plant_ids": []}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0
        mock_sync_favorites.assert_called_once_with(1, [])

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.sync_favorites')
    def test_sync_favorites_error(self, mock_sync_favorites, mock_get_user, client, mock_user, valid_jwt_token):
        """Test sync favorites with database error"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_sync_favorites.side_effect = Exception("Database error")

        # Act
        response = client.post(
            "/api/v1/favorites/sync",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"favorite_plant_ids": [1, 2, 3]}
        )

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_sync_favorites_missing_field(self, client, valid_jwt_token):
        """Test sync favorites with missing favorite_plant_ids field"""
        # Act
        response = client.post(
            "/api/v1/favorites/sync",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={}
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_sync_favorites_unauthenticated(self, client):
        """Test sync favorites without authentication"""
        # Act
        response = client.post(
            "/api/v1/favorites/sync",
            json={"favorite_plant_ids": [1, 2, 3]}
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCheckFavorite:
    """Tests for checking if a plant is favorited"""

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.is_favorite')
    def test_check_favorite_true(self, mock_is_favorite, mock_get_user, client, mock_user, valid_jwt_token):
        """Test checking favorite when plant is favorited"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_is_favorite.return_value = True

        # Act
        response = client.get(
            "/api/v1/favorites/check/1",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_favorite"] is True
        mock_is_favorite.assert_called_once_with(1, 1)

    @patch('app.api.dependencies.get_current_user')
    @patch('app.repositories.user_repository.UserRepository.is_favorite')
    def test_check_favorite_false(self, mock_is_favorite, mock_get_user, client, mock_user, valid_jwt_token):
        """Test checking favorite when plant is not favorited"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_is_favorite.return_value = False

        # Act
        response = client.get(
            "/api/v1/favorites/check/1",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_favorite"] is False

    def test_check_favorite_unauthenticated(self, client):
        """Test checking favorite without authentication"""
        # Act
        response = client.get("/api/v1/favorites/check/1")

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestFavoritesRequireAuth:
    """Tests to ensure all favorites endpoints require authentication"""

    def test_all_favorites_endpoints_require_auth(self, client):
        """Test that all favorites endpoints require authentication"""
        endpoints = [
            ("GET", "/api/v1/favorites"),
            ("POST", "/api/v1/favorites"),
            ("DELETE", "/api/v1/favorites/1"),
            ("POST", "/api/v1/favorites/sync"),
            ("GET", "/api/v1/favorites/check/1")
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)

            assert response.status_code == status.HTTP_403_FORBIDDEN, f"Endpoint {method} {endpoint} should require authentication"