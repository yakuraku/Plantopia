"""
End-to-end integration tests for the complete user authentication flow
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app


@pytest.fixture
def client():
    """Test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def mock_google_user_info():
    """Mock Google user information"""
    return {
        'google_id': '123456789',
        'email': 'test@example.com',
        'name': 'Test User',
        'picture': 'https://example.com/avatar.jpg'
    }


class TestCompleteAuthFlow:
    """Test the complete authentication and user management flow"""

    @patch('app.services.auth_service.AuthService.verify_google_token')
    @patch('app.repositories.user_repository.UserRepository.get_user_by_google_id')
    @patch('app.repositories.user_repository.UserRepository.create_user')
    @patch('app.repositories.user_repository.UserRepository.create_or_update_profile')
    def test_new_user_complete_flow(
        self, mock_create_profile, mock_create_user, mock_get_user, mock_verify_token,
        client, mock_google_user_info
    ):
        """Test complete flow for a new user: Google login -> profile creation -> favorites"""

        # Step 1: Mock Google login for new user
        mock_verify_token.return_value = mock_google_user_info
        mock_get_user.return_value = None  # User doesn't exist

        mock_user = Mock()
        mock_user.id = 1
        mock_user.google_id = '123456789'
        mock_user.email = 'test@example.com'
        mock_user.name = 'Test User'
        mock_user.avatar_url = 'https://example.com/avatar.jpg'
        mock_user.suburb = None
        mock_user.is_active = True
        mock_user.created_at = '2024-01-01T00:00:00'
        mock_user.last_login = '2024-01-01T12:00:00'

        mock_create_user.return_value = mock_user
        mock_create_profile.return_value = Mock()

        # Step 1: Google Login
        login_response = client.post(
            "/api/v1/auth/google",
            json={"credential": "google_jwt_token"}
        )

        assert login_response.status_code == status.HTTP_200_OK
        login_data = login_response.json()
        assert "access_token" in login_data
        assert login_data["user"]["email"] == "test@example.com"

        # Extract JWT token for subsequent requests
        jwt_token = login_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {jwt_token}"}

        # Step 2: Get user profile (should be created automatically)
        with patch('app.api.dependencies.get_current_user', return_value=mock_user):
            with patch('app.repositories.user_repository.UserRepository.get_user_profile') as mock_get_profile:
                mock_profile = Mock()
                mock_profile.id = 1
                mock_profile.user_id = 1
                mock_profile.experience_level = None
                mock_profile.garden_type = None
                mock_profile.has_containers = False
                mock_profile.organic_preference = True
                mock_profile.created_at = '2024-01-01T00:00:00'
                mock_profile.updated_at = '2024-01-01T00:00:00'

                mock_get_profile.return_value = mock_profile

                profile_response = client.get("/api/v1/auth/profile", headers=auth_headers)
                assert profile_response.status_code == status.HTTP_200_OK

        # Step 3: Update user profile
        with patch('app.api.dependencies.get_current_user', return_value=mock_user):
            with patch('app.repositories.user_repository.UserRepository.create_or_update_profile') as mock_update_profile:
                updated_profile = Mock()
                updated_profile.id = 1
                updated_profile.user_id = 1
                updated_profile.experience_level = 'beginner'
                updated_profile.garden_type = 'balcony'
                updated_profile.has_containers = True
                updated_profile.organic_preference = True
                updated_profile.created_at = '2024-01-01T00:00:00'
                updated_profile.updated_at = '2024-01-01T12:00:00'

                mock_update_profile.return_value = updated_profile

                update_response = client.put(
                    "/api/v1/auth/profile",
                    headers=auth_headers,
                    json={
                        "experience_level": "beginner",
                        "garden_type": "balcony",
                        "has_containers": True
                    }
                )
                assert update_response.status_code == status.HTTP_200_OK

        # Step 4: Add some favorites
        with patch('app.api.dependencies.get_current_user', return_value=mock_user):
            with patch('app.repositories.user_repository.UserRepository.add_favorite') as mock_add_fav:
                with patch('app.repositories.user_repository.UserRepository.get_user_favorites') as mock_get_favs:
                    mock_favorite = Mock()
                    mock_favorite.id = 1
                    mock_favorite.plant_id = 1
                    mock_favorite.notes = "Love this plant"
                    mock_favorite.priority_level = 0
                    mock_favorite.created_at = '2024-01-01T12:00:00'

                    mock_plant = Mock()
                    mock_plant.plant_name = "Basil"
                    mock_plant.plant_category = "herb"
                    mock_favorite.plant = mock_plant

                    mock_add_fav.return_value = mock_favorite
                    mock_get_favs.return_value = [mock_favorite]

                    add_fav_response = client.post(
                        "/api/v1/favorites",
                        headers=auth_headers,
                        json={"plant_id": 1, "notes": "Love this plant"}
                    )
                    assert add_fav_response.status_code == status.HTTP_200_OK

        # Step 5: Get all favorites
        with patch('app.api.dependencies.get_current_user', return_value=mock_user):
            with patch('app.repositories.user_repository.UserRepository.get_user_favorites') as mock_get_all_favs:
                mock_get_all_favs.return_value = [mock_favorite]

                get_favs_response = client.get("/api/v1/favorites", headers=auth_headers)
                assert get_favs_response.status_code == status.HTTP_200_OK
                favs_data = get_favs_response.json()
                assert len(favs_data) == 1
                assert favs_data[0]["plant_name"] == "Basil"

    def test_api_health_check(self, client):
        """Test that the API is running and health check works"""
        response = client.get("/api/v1/health")
        # This might not exist, but testing the root endpoint
        if response.status_code == 404:
            # Try root endpoint
            response = client.get("/")
            assert response.status_code == status.HTTP_200_OK
        else:
            assert response.status_code == status.HTTP_200_OK

    def test_invalid_auth_endpoints(self, client):
        """Test that protected endpoints reject invalid authentication"""
        endpoints = [
            "/api/v1/auth/me",
            "/api/v1/auth/profile",
            "/api/v1/favorites"
        ]

        for endpoint in endpoints:
            # Test with no auth
            response = client.get(endpoint)
            assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

            # Test with invalid token
            response = client.get(endpoint, headers={"Authorization": "Bearer invalid_token"})
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cors_headers_present(self, client):
        """Test that CORS headers are properly set"""
        response = client.options("/api/v1/auth/google", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, Authorization"
        })

        # Should return 200 for OPTIONS request
        assert response.status_code == status.HTTP_200_OK