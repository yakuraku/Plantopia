"""
Integration tests for plant tracking API endpoints
"""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
from datetime import date, datetime

from app.main import app


@pytest.fixture
def client():
    """Test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def mock_plant_data():
    """Mock plant data"""
    return {
        'id': 1,
        'plant_name': 'Basil',
        'scientific_name': 'Ocimum basilicum',
        'plant_category': 'herb',
        'time_to_maturity_days': 60
    }


@pytest.fixture
def mock_instance_data():
    """Mock plant instance data"""
    return {
        'instance_id': 1,
        'plant_nickname': 'My Basil',
        'start_date': date.today().isoformat(),
        'expected_maturity_date': date.today().isoformat(),
        'current_stage': 'germination',
        'message': 'Plant tracking started successfully'
    }


@pytest.fixture
def mock_growth_data():
    """Mock AI-generated growth data"""
    return {
        'requirements_checklist': [
            {
                'category': 'Tools',
                'items': [{'item': 'Garden Trowel', 'quantity': '1'}]
            }
        ],
        'setup_instructions': [
            {
                'category': 'Planting',
                'steps': [{'step': 'Prepare soil', 'details': 'Mix compost'}]
            }
        ],
        'growth_stages': [
            {
                'stage_name': 'germination',
                'start_day': 0,
                'end_day': 10,
                'description': 'Seed sprouting',
                'key_indicators': ['First leaves appear']
            }
        ],
        'care_tips': [
            {
                'stage_name': 'germination',
                'tips': [{'tip': 'Keep soil moist'}]
            }
        ]
    }


# ============================================================================
# CORE TRACKING ENDPOINTS
# ============================================================================

class TestStartPlantTracking:
    """Tests for POST /tracking/start endpoint"""

    @patch('app.services.plant_instance_service.PlantInstanceService.start_tracking')
    def test_start_tracking_success(self, mock_start, client, mock_instance_data):
        """Test successfully starting plant tracking"""
        # Arrange
        mock_start.return_value = mock_instance_data

        request_data = {
            'user_id': 1,
            'plant_id': 1,
            'plant_nickname': 'My Basil',
            'user_data': {
                'experience_level': 'beginner',
                'location': 'Melbourne, VIC',
                'climate_zone': '10'
            }
        }

        # Act
        response = client.post('/api/v1/tracking/start', json=request_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['plant_nickname'] == 'My Basil'
        assert data['current_stage'] == 'germination'

    @patch('app.services.plant_instance_service.PlantInstanceService.start_tracking')
    def test_start_tracking_plant_not_found(self, mock_start, client):
        """Test starting tracking when plant doesn't exist"""
        # Arrange
        mock_start.side_effect = ValueError("Plant with ID 999 not found")

        request_data = {
            'user_id': 1,
            'plant_id': 999,
            'plant_nickname': 'Test',
            'user_data': {'experience_level': 'beginner'}
        }

        # Act
        response = client.post('/api/v1/tracking/start', json=request_data)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_start_tracking_missing_fields(self, client):
        """Test starting tracking with missing required fields"""
        # Act
        response = client.post('/api/v1/tracking/start', json={})

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetUserPlantInstances:
    """Tests for GET /tracking/user/{user_id} endpoint"""

    @patch('app.services.plant_instance_service.PlantInstanceService.get_user_plants')
    def test_get_user_plants_success(self, mock_get_plants, client):
        """Test successfully getting user's plant instances"""
        # Arrange
        mock_get_plants.return_value = {
            'plants': [
                {
                    'instance_id': 1,
                    'plant_id': 1,
                    'plant_name': 'Basil',
                    'plant_nickname': 'My Basil',
                    'current_stage': 'germination',
                    'days_elapsed': 5,
                    'progress_percentage': 8.33
                }
            ],
            'total_count': 1,
            'active_count': 1,
            'pagination': {
                'page': 1,
                'limit': 20,
                'total_pages': 1
            }
        }

        # Act
        response = client.get('/api/v1/tracking/user/1')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['plants']) == 1
        assert data['plants'][0]['plant_nickname'] == 'My Basil'
        assert data['pagination']['page'] == 1

    @patch('app.services.plant_instance_service.PlantInstanceService.get_user_plants')
    def test_get_user_plants_with_pagination(self, mock_get_plants, client):
        """Test getting user plants with custom pagination"""
        # Arrange
        mock_get_plants.return_value = {
            'plants': [],
            'total_count': 0,
            'active_count': 0,
            'pagination': {'page': 2, 'limit': 10, 'total_pages': 0}
        }

        # Act
        response = client.get('/api/v1/tracking/user/1?page=2&limit=10')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['pagination']['page'] == 2
        assert data['pagination']['limit'] == 10


class TestGetPlantInstanceDetails:
    """Tests for GET /tracking/instance/{instance_id} endpoint"""

    @patch('app.services.plant_instance_service.PlantInstanceService.get_instance_details')
    def test_get_instance_details_success(self, mock_get_details, client):
        """Test successfully getting plant instance details"""
        # Arrange
        mock_get_details.return_value = {
            'instance_id': 1,
            'plant_details': {
                'plant_id': 1,
                'plant_name': 'Basil',
                'scientific_name': 'Ocimum basilicum',
                'plant_category': 'herb'
            },
            'tracking_info': {
                'plant_nickname': 'My Basil',
                'start_date': date.today().isoformat(),
                'current_stage': 'germination',
                'days_elapsed': 5,
                'progress_percentage': 8.33,
                'is_active': True
            },
            'timeline': {
                'stages': [
                    {
                        'stage_name': 'germination',
                        'start_day': 0,
                        'end_day': 10,
                        'is_current': True,
                        'is_completed': False
                    }
                ]
            },
            'current_tips': ['Keep soil moist']
        }

        # Act
        response = client.get('/api/v1/tracking/instance/1')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['instance_id'] == 1
        assert data['plant_details']['plant_name'] == 'Basil'
        assert len(data['timeline']['stages']) == 1
        assert len(data['current_tips']) == 1

    @patch('app.services.plant_instance_service.PlantInstanceService.get_instance_details')
    def test_get_instance_details_not_found(self, mock_get_details, client):
        """Test getting instance details when instance doesn't exist"""
        # Arrange
        mock_get_details.side_effect = ValueError("Plant instance with ID 999 not found")

        # Act
        response = client.get('/api/v1/tracking/instance/999')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdatePlantProgress:
    """Tests for PUT /tracking/instance/{instance_id}/progress endpoint"""

    @patch('app.services.plant_instance_service.PlantInstanceService.update_progress')
    def test_update_progress_success(self, mock_update, client):
        """Test successfully updating plant progress"""
        # Arrange
        mock_update.return_value = {
            'instance_id': 1,
            'current_stage': 'seedling',
            'user_notes': 'First leaves appeared!',
            'location_details': None,
            'message': 'Progress updated successfully'
        }

        request_data = {
            'current_stage': 'seedling',
            'user_notes': 'First leaves appeared!'
        }

        # Act
        response = client.put('/api/v1/tracking/instance/1/progress', json=request_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['message'] == 'Progress updated successfully'
        assert data['data']['current_stage'] == 'seedling'


# ============================================================================
# DATA ACCESS ENDPOINTS (AI-GENERATED CONTENT)
# ============================================================================

class TestGetPlantRequirements:
    """Tests for GET /tracking/requirements/{plant_id} endpoint"""

    @patch('app.services.plant_growth_service.PlantGrowthService.get_requirements')
    def test_get_requirements_success(self, mock_get_reqs, client, mock_growth_data):
        """Test successfully getting requirements checklist"""
        # Arrange
        mock_get_reqs.return_value = {
            'plant_id': 1,
            'requirements': mock_growth_data['requirements_checklist']
        }

        # Act
        response = client.get('/api/v1/tracking/requirements/1')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['plant_id'] == 1
        assert len(data['requirements']) == 1
        assert data['requirements'][0]['category'] == 'Tools'

    @patch('app.services.plant_growth_service.PlantGrowthService.get_requirements')
    def test_get_requirements_no_data(self, mock_get_reqs, client):
        """Test getting requirements when no growth data exists"""
        # Arrange
        mock_get_reqs.side_effect = ValueError("No growth data found")

        # Act
        response = client.get('/api/v1/tracking/requirements/999')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetSetupInstructions:
    """Tests for GET /tracking/instructions/{plant_id} endpoint"""

    @patch('app.services.plant_growth_service.PlantGrowthService.get_instructions')
    def test_get_instructions_success(self, mock_get_inst, client, mock_growth_data):
        """Test successfully getting setup instructions"""
        # Arrange
        mock_get_inst.return_value = {
            'plant_id': 1,
            'instructions': mock_growth_data['setup_instructions']
        }

        # Act
        response = client.get('/api/v1/tracking/instructions/1')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['plant_id'] == 1
        assert len(data['instructions']) == 1


class TestGetGrowthTimeline:
    """Tests for GET /tracking/timeline/{plant_id} endpoint"""

    @patch('app.services.plant_growth_service.PlantGrowthService.get_timeline')
    def test_get_timeline_success(self, mock_get_timeline, client, mock_growth_data):
        """Test successfully getting growth timeline"""
        # Arrange
        mock_get_timeline.return_value = {
            'plant_id': 1,
            'total_days': 60,
            'stages': mock_growth_data['growth_stages']
        }

        # Act
        response = client.get('/api/v1/tracking/timeline/1')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['plant_id'] == 1
        assert data['total_days'] == 60
        assert len(data['stages']) == 1


class TestGetCurrentStageTips:
    """Tests for GET /tracking/instance/{instance_id}/tips endpoint"""

    @patch('app.services.plant_instance_service.PlantInstanceService.get_instance_details')
    @patch('app.services.progress_tracking_service.ProgressTrackingService.get_current_stage_tips')
    def test_get_tips_success(self, mock_get_tips, mock_get_details, client):
        """Test successfully getting current stage tips"""
        # Arrange
        mock_get_details.return_value = {
            'plant_details': {'plant_id': 1},
            'tracking_info': {'current_stage': 'germination', 'days_elapsed': 5}
        }
        mock_get_tips.return_value = ['Keep soil moist', 'Maintain warm temperature']

        # Act
        response = client.get('/api/v1/tracking/instance/1/tips')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['current_stage'] == 'germination'
        assert len(data['tips']) == 2

    @patch('app.services.plant_instance_service.PlantInstanceService.get_instance_details')
    @patch('app.services.progress_tracking_service.ProgressTrackingService.get_current_stage_tips')
    def test_get_tips_with_limit(self, mock_get_tips, mock_get_details, client):
        """Test getting tips with custom limit"""
        # Arrange
        mock_get_details.return_value = {
            'plant_details': {'plant_id': 1},
            'tracking_info': {'current_stage': 'germination', 'days_elapsed': 5}
        }
        mock_get_tips.return_value = ['Tip 1']

        # Act
        response = client.get('/api/v1/tracking/instance/1/tips?limit=1')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['tips']) == 1


# ============================================================================
# MANAGEMENT ENDPOINTS
# ============================================================================

class TestCompleteChecklistItem:
    """Tests for POST /tracking/checklist/complete endpoint"""

    @patch('app.services.progress_tracking_service.ProgressTrackingService.mark_checklist_item_complete')
    def test_complete_checklist_item_success(self, mock_mark_complete, client):
        """Test successfully marking checklist item as complete"""
        # Arrange
        mock_mark_complete.return_value = {
            'success': True,
            'message': 'Checklist item marked as complete',
            'progress_summary': {
                'completed_items': 5,
                'total_items': 10,
                'completion_percentage': 50.0
            }
        }

        request_data = {
            'instance_id': 1,
            'checklist_item_key': 'tools_garden_trowel',
            'is_completed': True,
            'user_notes': 'Purchased today'
        }

        # Act
        response = client.post('/api/v1/tracking/checklist/complete', json=request_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['success'] is True
        assert data['progress_summary']['completion_percentage'] == 50.0


class TestInitializeChecklist:
    """Tests for POST /tracking/instance/{instance_id}/initialize-checklist endpoint"""

    @patch('app.services.plant_instance_service.PlantInstanceService.get_instance_details')
    @patch('app.services.progress_tracking_service.ProgressTrackingService.initialize_checklist')
    def test_initialize_checklist_success(self, mock_init, mock_get_details, client):
        """Test successfully initializing checklist"""
        # Arrange
        mock_get_details.return_value = {
            'plant_details': {'plant_id': 1}
        }
        mock_init.return_value = {
            'success': True,
            'message': 'Initialized 10 checklist items',
            'items_created': 10
        }

        # Act
        response = client.post('/api/v1/tracking/instance/1/initialize-checklist')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['message'] == 'Initialized 10 checklist items'
        assert data['data']['items_created'] == 10


class TestUpdatePlantNickname:
    """Tests for PUT /tracking/instance/{instance_id}/nickname endpoint"""

    @patch('app.services.plant_instance_service.PlantInstanceService.update_nickname')
    def test_update_nickname_success(self, mock_update, client):
        """Test successfully updating plant nickname"""
        # Arrange
        mock_update.return_value = {
            'instance_id': 1,
            'plant_nickname': 'Super Basil',
            'message': 'Nickname updated successfully'
        }

        request_data = {'plant_nickname': 'Super Basil'}

        # Act
        response = client.put('/api/v1/tracking/instance/1/nickname', json=request_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['data']['plant_nickname'] == 'Super Basil'

    def test_update_nickname_empty(self, client):
        """Test updating nickname with empty string"""
        # Arrange
        request_data = {'plant_nickname': ''}

        # Act
        response = client.put('/api/v1/tracking/instance/1/nickname', json=request_data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDeactivatePlantInstance:
    """Tests for DELETE /tracking/instance/{instance_id} endpoint"""

    @patch('app.services.plant_instance_service.PlantInstanceService.deactivate_instance')
    def test_deactivate_instance_success(self, mock_deactivate, client):
        """Test successfully deactivating plant instance"""
        # Arrange
        mock_deactivate.return_value = {
            'instance_id': 1,
            'is_active': False,
            'message': 'Plant instance deactivated successfully'
        }

        # Act
        response = client.delete('/api/v1/tracking/instance/1')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['message'] == 'Plant instance deactivated successfully'
        assert data['data']['is_active'] is False

    @patch('app.services.plant_instance_service.PlantInstanceService.deactivate_instance')
    def test_deactivate_instance_not_found(self, mock_deactivate, client):
        """Test deactivating instance that doesn't exist"""
        # Arrange
        mock_deactivate.side_effect = ValueError("Plant instance with ID 999 not found")

        # Act
        response = client.delete('/api/v1/tracking/instance/999')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

class TestAutoUpdateStage:
    """Tests for POST /tracking/instance/{instance_id}/auto-update-stage endpoint"""

    @patch('app.services.plant_instance_service.PlantInstanceService.auto_update_stage')
    def test_auto_update_stage_changed(self, mock_auto_update, client):
        """Test auto-update when stage changes"""
        # Arrange
        mock_auto_update.return_value = "seedling"

        # Act
        response = client.post('/api/v1/tracking/instance/1/auto-update-stage')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['data']['new_stage'] == 'seedling'
        assert data['data']['updated'] is True

    @patch('app.services.plant_instance_service.PlantInstanceService.auto_update_stage')
    def test_auto_update_stage_no_change(self, mock_auto_update, client):
        """Test auto-update when stage doesn't change"""
        # Arrange
        mock_auto_update.return_value = None

        # Act
        response = client.post('/api/v1/tracking/instance/1/auto-update-stage')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['data']['updated'] is False
