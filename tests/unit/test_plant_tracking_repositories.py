"""
Unit tests for plant tracking repositories
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, date, timedelta

from app.repositories.plant_growth_repository import PlantGrowthRepository
from app.repositories.plant_instance_repository import PlantInstanceRepository
from app.repositories.progress_tracking_repository import ProgressTrackingRepository
from app.models.database import PlantGrowthData, UserPlantInstance, UserProgressTracking, Plant, User


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def plant_growth_repo(mock_db):
    """PlantGrowthRepository instance with mocked database"""
    return PlantGrowthRepository(mock_db)


@pytest.fixture
def plant_instance_repo(mock_db):
    """PlantInstanceRepository instance with mocked database"""
    return PlantInstanceRepository(mock_db)


@pytest.fixture
def progress_tracking_repo(mock_db):
    """ProgressTrackingRepository instance with mocked database"""
    return ProgressTrackingRepository(mock_db)


@pytest.fixture
def mock_plant_growth_data():
    """Mock PlantGrowthData instance"""
    growth_data = Mock(spec=PlantGrowthData)
    growth_data.plant_id = 1
    growth_data.requirements_checklist = [
        {
            "category": "Tools",
            "items": [{"item": "Garden Trowel", "quantity": "1"}]
        }
    ]
    growth_data.setup_instructions = [
        {
            "category": "Planting",
            "steps": [{"step": "Prepare soil", "details": "Mix compost"}]
        }
    ]
    growth_data.growth_stages = [
        {
            "stage_name": "germination",
            "start_day": 0,
            "end_day": 10,
            "description": "Seed sprouting phase",
            "key_indicators": ["First leaves appear"]
        }
    ]
    growth_data.care_tips = [
        {
            "stage_name": "germination",
            "tips": [{"tip": "Keep soil moist"}]
        }
    ]
    growth_data.data_source_info = {"model": "gemini-2.0-flash-exp", "generated_at": "2025-01-01"}
    growth_data.last_updated = datetime.utcnow()
    growth_data.version = "1.0"
    return growth_data


@pytest.fixture
def mock_plant():
    """Mock Plant instance"""
    plant = Mock(spec=Plant)
    plant.id = 1
    plant.plant_name = "Basil"
    plant.scientific_name = "Ocimum basilicum"
    plant.plant_category = "herb"
    plant.time_to_maturity_days = 60
    plant.image_url = "https://example.com/basil.jpg"
    return plant


@pytest.fixture
def mock_user():
    """Mock User instance"""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.name = "Test User"
    return user


@pytest.fixture
def mock_plant_instance():
    """Mock UserPlantInstance instance"""
    instance = Mock(spec=UserPlantInstance)
    instance.id = 1
    instance.user_id = 1
    instance.plant_id = 1
    instance.plant_nickname = "My Basil"
    instance.start_date = date(2025, 1, 1)
    instance.expected_maturity_date = date(2025, 3, 1)
    instance.current_stage = "germination"
    instance.is_active = True
    instance.location_details = "Kitchen window"
    instance.user_notes = None
    instance.created_at = datetime.utcnow()
    instance.updated_at = datetime.utcnow()

    # Add mock relationships
    instance.plant = Mock(spec=Plant)
    instance.plant.plant_name = "Basil"
    instance.plant.image_url = "https://example.com/basil.jpg"
    instance.user = Mock(spec=User)
    instance.progress_tracking = []

    return instance


@pytest.fixture
def mock_progress_tracking():
    """Mock UserProgressTracking instance"""
    tracking = Mock(spec=UserProgressTracking)
    tracking.id = 1
    tracking.user_plant_instance_id = 1
    tracking.checklist_item_key = "tools_garden_trowel"
    tracking.is_completed = False
    tracking.completed_at = None
    tracking.user_notes = None
    tracking.created_at = datetime.utcnow()
    return tracking


# ============================================================================
# PLANT GROWTH REPOSITORY TESTS
# ============================================================================

class TestPlantGrowthRepository:
    """Tests for PlantGrowthRepository"""

    async def test_get_by_plant_id_found(self, plant_growth_repo, mock_db, mock_plant_growth_data):
        """Test getting growth data by plant ID when it exists"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_plant_growth_data
        mock_db.execute.return_value = mock_result

        # Act
        result = await plant_growth_repo.get_by_plant_id(1)

        # Assert
        assert result == mock_plant_growth_data
        mock_db.execute.assert_called_once()

    async def test_get_by_plant_id_not_found(self, plant_growth_repo, mock_db):
        """Test getting growth data by plant ID when it doesn't exist"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Act
        result = await plant_growth_repo.get_by_plant_id(999)

        # Assert
        assert result is None

    async def test_create_growth_data(self, plant_growth_repo, mock_db, mock_plant_growth_data):
        """Test creating new growth data"""
        # Arrange
        growth_data_dict = {
            'plant_id': 1,
            'requirements_checklist': [],
            'setup_instructions': [],
            'growth_stages': [],
            'care_tips': [],
            'data_source_info': {}
        }

        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with pytest.mock.patch.object(PlantGrowthData, '__new__', return_value=mock_plant_growth_data):
            # Act
            result = await plant_growth_repo.create(growth_data_dict)

            # Assert
            assert result == mock_plant_growth_data
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    async def test_update_growth_data(self, plant_growth_repo, mock_db, mock_plant_growth_data):
        """Test updating existing growth data"""
        # Arrange
        update_dict = {'version': '2.0'}

        with pytest.mock.patch.object(plant_growth_repo, 'get_by_plant_id', return_value=mock_plant_growth_data):
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            # Act
            result = await plant_growth_repo.update(1, update_dict)

            # Assert
            assert result == mock_plant_growth_data
            assert mock_plant_growth_data.version == '2.0'
            mock_db.commit.assert_called_once()

    async def test_update_growth_data_not_found(self, plant_growth_repo):
        """Test updating growth data when it doesn't exist"""
        # Arrange
        with pytest.mock.patch.object(plant_growth_repo, 'get_by_plant_id', return_value=None):
            # Act & Assert
            with pytest.raises(ValueError, match="PlantGrowthData for plant_id 999 not found"):
                await plant_growth_repo.update(999, {'version': '2.0'})

    async def test_is_data_current_yes(self, plant_growth_repo, mock_db, mock_plant_growth_data):
        """Test checking if data is current when it is"""
        # Arrange
        mock_plant_growth_data.last_updated = datetime.utcnow() - timedelta(days=15)

        with pytest.mock.patch.object(plant_growth_repo, 'get_by_plant_id', return_value=mock_plant_growth_data):
            # Act
            result = await plant_growth_repo.is_data_current(1, max_age_days=30)

            # Assert
            assert result is True

    async def test_is_data_current_no(self, plant_growth_repo, mock_db, mock_plant_growth_data):
        """Test checking if data is current when it's stale"""
        # Arrange
        mock_plant_growth_data.last_updated = datetime.utcnow() - timedelta(days=45)

        with pytest.mock.patch.object(plant_growth_repo, 'get_by_plant_id', return_value=mock_plant_growth_data):
            # Act
            result = await plant_growth_repo.is_data_current(1, max_age_days=30)

            # Assert
            assert result is False

    async def test_is_data_current_no_data(self, plant_growth_repo):
        """Test checking if data is current when no data exists"""
        # Arrange
        with pytest.mock.patch.object(plant_growth_repo, 'get_by_plant_id', return_value=None):
            # Act
            result = await plant_growth_repo.is_data_current(1)

            # Assert
            assert result is False

    async def test_delete_growth_data_success(self, plant_growth_repo, mock_db, mock_plant_growth_data):
        """Test deleting growth data successfully"""
        # Arrange
        with pytest.mock.patch.object(plant_growth_repo, 'get_by_plant_id', return_value=mock_plant_growth_data):
            mock_db.delete = AsyncMock()
            mock_db.commit = AsyncMock()

            # Act
            result = await plant_growth_repo.delete(1)

            # Assert
            assert result is True
            mock_db.delete.assert_called_once_with(mock_plant_growth_data)

    async def test_delete_growth_data_not_found(self, plant_growth_repo):
        """Test deleting growth data when it doesn't exist"""
        # Arrange
        with pytest.mock.patch.object(plant_growth_repo, 'get_by_plant_id', return_value=None):
            # Act
            result = await plant_growth_repo.delete(999)

            # Assert
            assert result is False


# ============================================================================
# PLANT INSTANCE REPOSITORY TESTS
# ============================================================================

class TestPlantInstanceRepository:
    """Tests for PlantInstanceRepository"""

    async def test_get_by_id_found(self, plant_instance_repo, mock_db, mock_plant_instance):
        """Test getting instance by ID when it exists"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_plant_instance
        mock_db.execute.return_value = mock_result

        # Act
        result = await plant_instance_repo.get_by_id(1)

        # Assert
        assert result == mock_plant_instance
        mock_db.execute.assert_called_once()

    async def test_get_by_id_not_found(self, plant_instance_repo, mock_db):
        """Test getting instance by ID when it doesn't exist"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Act
        result = await plant_instance_repo.get_by_id(999)

        # Assert
        assert result is None

    async def test_get_user_instances_active_only(self, plant_instance_repo, mock_db, mock_plant_instance):
        """Test getting user instances with active_only=True"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [mock_plant_instance]
        mock_db.execute.return_value = mock_result

        # Act
        result = await plant_instance_repo.get_user_instances(1, active_only=True)

        # Assert
        assert len(result) == 1
        assert result[0] == mock_plant_instance

    async def test_get_user_instances_with_pagination(self, plant_instance_repo, mock_db, mock_plant_instance):
        """Test getting user instances with pagination"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [mock_plant_instance]
        mock_db.execute.return_value = mock_result

        # Act
        result = await plant_instance_repo.get_user_instances(1, limit=10, offset=0)

        # Assert
        assert len(result) == 1

    async def test_count_user_instances(self, plant_instance_repo, mock_db):
        """Test counting user instances"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one.return_value = 5
        mock_db.execute.return_value = mock_result

        # Act
        result = await plant_instance_repo.count_user_instances(1)

        # Assert
        assert result == 5

    async def test_create_instance(self, plant_instance_repo, mock_db, mock_plant_instance):
        """Test creating new plant instance"""
        # Arrange
        instance_data = {
            'user_id': 1,
            'plant_id': 1,
            'plant_nickname': 'My Basil',
            'start_date': date(2025, 1, 1),
            'expected_maturity_date': date(2025, 3, 1),
            'current_stage': 'germination'
        }

        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with pytest.mock.patch.object(UserPlantInstance, '__new__', return_value=mock_plant_instance):
            # Act
            result = await plant_instance_repo.create(instance_data)

            # Assert
            assert result == mock_plant_instance
            mock_db.add.assert_called_once()

    async def test_update_instance_success(self, plant_instance_repo, mock_db, mock_plant_instance):
        """Test updating instance successfully"""
        # Arrange
        update_data = {'current_stage': 'seedling'}

        with pytest.mock.patch.object(plant_instance_repo, 'get_by_id', return_value=mock_plant_instance):
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            # Act
            result = await plant_instance_repo.update(1, update_data)

            # Assert
            assert result == mock_plant_instance
            assert mock_plant_instance.current_stage == 'seedling'

    async def test_update_instance_not_found(self, plant_instance_repo):
        """Test updating instance when it doesn't exist"""
        # Arrange
        with pytest.mock.patch.object(plant_instance_repo, 'get_by_id', return_value=None):
            # Act & Assert
            with pytest.raises(ValueError, match="Plant instance with ID 999 not found"):
                await plant_instance_repo.update(999, {'current_stage': 'seedling'})

    async def test_deactivate_instance(self, plant_instance_repo, mock_plant_instance):
        """Test deactivating instance (soft delete)"""
        # Arrange
        with pytest.mock.patch.object(plant_instance_repo, 'update', return_value=mock_plant_instance) as mock_update:
            # Act
            result = await plant_instance_repo.deactivate(1)

            # Assert
            assert result == mock_plant_instance
            mock_update.assert_called_once_with(1, {'is_active': False})

    async def test_delete_instance_success(self, plant_instance_repo, mock_db, mock_plant_instance):
        """Test deleting instance (hard delete)"""
        # Arrange
        with pytest.mock.patch.object(plant_instance_repo, 'get_by_id', return_value=mock_plant_instance):
            mock_db.delete = AsyncMock()
            mock_db.commit = AsyncMock()

            # Act
            result = await plant_instance_repo.delete(1)

            # Assert
            assert result is True
            mock_db.delete.assert_called_once_with(mock_plant_instance)

    async def test_update_stage(self, plant_instance_repo, mock_plant_instance):
        """Test updating instance stage"""
        # Arrange
        with pytest.mock.patch.object(plant_instance_repo, 'update', return_value=mock_plant_instance) as mock_update:
            # Act
            result = await plant_instance_repo.update_stage(1, 'flowering')

            # Assert
            mock_update.assert_called_once_with(1, {'current_stage': 'flowering'})

    async def test_calculate_days_elapsed(self, plant_instance_repo, mock_plant_instance):
        """Test calculating days elapsed since planting"""
        # Arrange
        mock_plant_instance.start_date = date.today() - timedelta(days=15)

        with pytest.mock.patch.object(plant_instance_repo, 'get_by_id', return_value=mock_plant_instance):
            # Act
            result = await plant_instance_repo.calculate_days_elapsed(1)

            # Assert
            assert result == 15

    async def test_calculate_days_elapsed_not_found(self, plant_instance_repo):
        """Test calculating days elapsed when instance doesn't exist"""
        # Arrange
        with pytest.mock.patch.object(plant_instance_repo, 'get_by_id', return_value=None):
            # Act & Assert
            with pytest.raises(ValueError, match="Plant instance with ID 999 not found"):
                await plant_instance_repo.calculate_days_elapsed(999)

    async def test_get_maturing_soon(self, plant_instance_repo, mock_db, mock_plant_instance):
        """Test getting instances maturing soon"""
        # Arrange
        mock_plant_instance.expected_maturity_date = date.today() + timedelta(days=3)
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [mock_plant_instance]
        mock_db.execute.return_value = mock_result

        # Act
        result = await plant_instance_repo.get_maturing_soon(1, days_threshold=7)

        # Assert
        assert len(result) == 1
        assert result[0] == mock_plant_instance


# ============================================================================
# PROGRESS TRACKING REPOSITORY TESTS
# ============================================================================

class TestProgressTrackingRepository:
    """Tests for ProgressTrackingRepository"""

    async def test_get_by_id_found(self, progress_tracking_repo, mock_db, mock_progress_tracking):
        """Test getting tracking entry by ID when it exists"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_progress_tracking
        mock_db.execute.return_value = mock_result

        # Act
        result = await progress_tracking_repo.get_by_id(1)

        # Assert
        assert result == mock_progress_tracking

    async def test_get_by_instance(self, progress_tracking_repo, mock_db, mock_progress_tracking):
        """Test getting all tracking entries for an instance"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [mock_progress_tracking]
        mock_db.execute.return_value = mock_result

        # Act
        result = await progress_tracking_repo.get_by_instance(1)

        # Assert
        assert len(result) == 1
        assert result[0] == mock_progress_tracking

    async def test_get_by_item_key_found(self, progress_tracking_repo, mock_db, mock_progress_tracking):
        """Test getting tracking entry by item key when it exists"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_progress_tracking
        mock_db.execute.return_value = mock_result

        # Act
        result = await progress_tracking_repo.get_by_item_key(1, "tools_garden_trowel")

        # Assert
        assert result == mock_progress_tracking

    async def test_mark_complete_new_entry(self, progress_tracking_repo, mock_db, mock_progress_tracking):
        """Test marking item complete when entry doesn't exist (creates new)"""
        # Arrange
        with pytest.mock.patch.object(progress_tracking_repo, 'get_by_item_key', return_value=None):
            with pytest.mock.patch.object(progress_tracking_repo, 'create', return_value=mock_progress_tracking) as mock_create:
                # Act
                result = await progress_tracking_repo.mark_complete(1, "tools_garden_trowel", True)

                # Assert
                assert result == mock_progress_tracking
                mock_create.assert_called_once()

    async def test_mark_complete_existing_entry(self, progress_tracking_repo, mock_db, mock_progress_tracking):
        """Test marking item complete when entry already exists (updates)"""
        # Arrange
        with pytest.mock.patch.object(progress_tracking_repo, 'get_by_item_key', return_value=mock_progress_tracking):
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            # Act
            result = await progress_tracking_repo.mark_complete(1, "tools_garden_trowel", True, "Done!")

            # Assert
            assert result == mock_progress_tracking
            assert mock_progress_tracking.is_completed is True
            assert mock_progress_tracking.user_notes == "Done!"

    async def test_get_completed_count(self, progress_tracking_repo, mock_db):
        """Test getting count of completed items"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one.return_value = 3
        mock_db.execute.return_value = mock_result

        # Act
        result = await progress_tracking_repo.get_completed_count(1)

        # Assert
        assert result == 3

    async def test_get_total_count(self, progress_tracking_repo, mock_db):
        """Test getting total count of tracking entries"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one.return_value = 10
        mock_db.execute.return_value = mock_result

        # Act
        result = await progress_tracking_repo.get_total_count(1)

        # Assert
        assert result == 10

    async def test_get_completion_percentage(self, progress_tracking_repo):
        """Test calculating completion percentage"""
        # Arrange
        with pytest.mock.patch.object(progress_tracking_repo, 'get_total_count', return_value=10):
            with pytest.mock.patch.object(progress_tracking_repo, 'get_completed_count', return_value=7):
                # Act
                result = await progress_tracking_repo.get_completion_percentage(1)

                # Assert
                assert result == 70.0

    async def test_get_completion_percentage_zero_total(self, progress_tracking_repo):
        """Test completion percentage when no items exist"""
        # Arrange
        with pytest.mock.patch.object(progress_tracking_repo, 'get_total_count', return_value=0):
            # Act
            result = await progress_tracking_repo.get_completion_percentage(1)

            # Assert
            assert result == 0.0

    async def test_get_incomplete_items(self, progress_tracking_repo, mock_db, mock_progress_tracking):
        """Test getting incomplete items"""
        # Arrange
        mock_progress_tracking.is_completed = False
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [mock_progress_tracking]
        mock_db.execute.return_value = mock_result

        # Act
        result = await progress_tracking_repo.get_incomplete_items(1)

        # Assert
        assert len(result) == 1
        assert result[0].is_completed is False

    async def test_get_completed_items(self, progress_tracking_repo, mock_db, mock_progress_tracking):
        """Test getting completed items"""
        # Arrange
        mock_progress_tracking.is_completed = True
        mock_progress_tracking.completed_at = datetime.utcnow()
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [mock_progress_tracking]
        mock_db.execute.return_value = mock_result

        # Act
        result = await progress_tracking_repo.get_completed_items(1)

        # Assert
        assert len(result) == 1
        assert result[0].is_completed is True

    async def test_bulk_create(self, progress_tracking_repo, mock_db, mock_progress_tracking):
        """Test bulk creating tracking entries"""
        # Arrange
        item_keys = ["tools_trowel", "tools_watering_can", "supplies_potting_soil"]

        with pytest.mock.patch.object(progress_tracking_repo, 'get_by_item_key', return_value=None):
            mock_db.add = Mock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            with pytest.mock.patch.object(UserProgressTracking, '__new__', return_value=mock_progress_tracking):
                # Act
                result = await progress_tracking_repo.bulk_create(1, item_keys)

                # Assert
                assert len(result) == 3
                assert mock_db.add.call_count == 3

    async def test_delete_by_instance(self, progress_tracking_repo, mock_db, mock_progress_tracking):
        """Test deleting all tracking entries for an instance"""
        # Arrange
        with pytest.mock.patch.object(progress_tracking_repo, 'get_by_instance', return_value=[mock_progress_tracking]):
            mock_db.delete = AsyncMock()
            mock_db.commit = AsyncMock()

            # Act
            result = await progress_tracking_repo.delete_by_instance(1)

            # Assert
            assert result == 1
            mock_db.delete.assert_called_once_with(mock_progress_tracking)
