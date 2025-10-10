"""
Unit tests for plant tracking services
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import date, datetime, timedelta

from app.services.plant_growth_service import PlantGrowthService
from app.services.plant_instance_service import PlantInstanceService
from app.services.progress_tracking_service import ProgressTrackingService
from app.models.database import Plant, UserPlantInstance


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def mock_plant():
    """Mock Plant instance"""
    plant = Mock(spec=Plant)
    plant.id = 1
    plant.plant_name = "Basil"
    plant.scientific_name = "Ocimum basilicum"
    plant.plant_category = "herb"
    plant.time_to_maturity_days = 60
    plant.water_requirements = "moderate"
    plant.sunlight_requirements = "full sun"
    plant.soil_type = "well-drained"
    plant.climate_zone = "10-11"
    return plant


@pytest.fixture
def mock_growth_data():
    """Mock growth data dictionary"""
    return {
        "requirements_checklist": [
            {
                "category": "Tools",
                "items": [{"item": "Garden Trowel", "quantity": "1"}]
            }
        ],
        "setup_instructions": [
            {
                "category": "Planting",
                "steps": [{"step": "Prepare soil"}]
            }
        ],
        "growth_stages": [
            {
                "stage_name": "germination",
                "start_day": 0,
                "end_day": 10,
                "description": "Seed sprouting",
                "key_indicators": ["First leaves"]
            },
            {
                "stage_name": "seedling",
                "start_day": 11,
                "end_day": 25,
                "description": "Young plant growth",
                "key_indicators": ["Multiple leaves"]
            }
        ],
        "care_tips": [
            {
                "stage_name": "germination",
                "tips": [
                    {"tip": "Keep soil moist"},
                    {"tip": "Maintain warm temperature"}
                ]
            }
        ],
        "data_source_info": {"model": "gemini-2.0-flash-exp"}
    }


@pytest.fixture
def mock_plant_instance():
    """Mock plant instance"""
    instance = Mock(spec=UserPlantInstance)
    instance.id = 1
    instance.user_id = 1
    instance.plant_id = 1
    instance.plant_nickname = "My Basil"
    instance.start_date = date.today() - timedelta(days=15)
    instance.expected_maturity_date = date.today() + timedelta(days=45)
    instance.current_stage = "germination"
    instance.is_active = True
    instance.user_notes = None
    instance.location_details = "Kitchen window"

    # Add plant relationship
    instance.plant = Mock(spec=Plant)
    instance.plant.plant_name = "Basil"
    instance.plant.time_to_maturity_days = 60

    return instance


# ============================================================================
# PLANT GROWTH SERVICE TESTS
# ============================================================================

class TestPlantGrowthService:
    """Tests for PlantGrowthService"""

    @pytest.fixture
    def plant_growth_service(self, mock_db):
        """PlantGrowthService instance"""
        return PlantGrowthService(mock_db)

    async def test_get_or_generate_growth_data_from_cache(
        self, plant_growth_service, mock_plant, mock_growth_data
    ):
        """Test getting growth data from cache when it exists and is current"""
        # Arrange
        mock_repository = Mock()
        mock_repository.get_by_plant_id = AsyncMock(return_value=Mock(
            requirements_checklist=mock_growth_data["requirements_checklist"],
            setup_instructions=mock_growth_data["setup_instructions"],
            growth_stages=mock_growth_data["growth_stages"],
            care_tips=mock_growth_data["care_tips"],
            data_source_info=mock_growth_data["data_source_info"]
        ))
        mock_repository.is_data_current = AsyncMock(return_value=True)
        plant_growth_service.repository = mock_repository

        with patch.object(plant_growth_service, 'get_plant_by_id', return_value=mock_plant):
            # Act
            result = await plant_growth_service.get_or_generate_growth_data(
                plant_id=1,
                user_data={"experience_level": "beginner"}
            )

            # Assert
            assert result["cached"] is True
            assert "requirements_checklist" in result
            mock_repository.get_by_plant_id.assert_called_once_with(1)

    async def test_get_or_generate_growth_data_generates_new(
        self, plant_growth_service, mock_plant, mock_growth_data
    ):
        """Test generating new growth data when cache is empty"""
        # Arrange
        mock_repository = Mock()
        mock_repository.get_by_plant_id = AsyncMock(return_value=None)
        mock_repository.get_or_create = AsyncMock()
        plant_growth_service.repository = mock_repository

        mock_gemini_service = Mock()
        mock_gemini_service.generate_complete_plant_data = AsyncMock(return_value=mock_growth_data)
        plant_growth_service.gemini_service = mock_gemini_service

        with patch.object(plant_growth_service, 'get_plant_by_id', return_value=mock_plant):
            # Act
            result = await plant_growth_service.get_or_generate_growth_data(
                plant_id=1,
                user_data={"experience_level": "beginner"}
            )

            # Assert
            assert result["cached"] is False
            mock_gemini_service.generate_complete_plant_data.assert_called_once()
            mock_repository.get_or_create.assert_called_once()

    async def test_get_or_generate_growth_data_plant_not_found(self, plant_growth_service):
        """Test getting growth data when plant doesn't exist"""
        # Arrange
        with patch.object(plant_growth_service, 'get_plant_by_id', return_value=None):
            # Act & Assert
            with pytest.raises(ValueError, match="Plant with ID 999 not found"):
                await plant_growth_service.get_or_generate_growth_data(
                    plant_id=999,
                    user_data={}
                )

    async def test_get_requirements_success(self, plant_growth_service, mock_growth_data):
        """Test getting requirements checklist"""
        # Arrange
        mock_repository = Mock()
        mock_repository.get_by_plant_id = AsyncMock(return_value=Mock(
            requirements_checklist=mock_growth_data["requirements_checklist"]
        ))
        plant_growth_service.repository = mock_repository

        # Act
        result = await plant_growth_service.get_requirements(1)

        # Assert
        assert result["plant_id"] == 1
        assert "requirements" in result
        assert len(result["requirements"]) == 1

    async def test_get_requirements_not_found(self, plant_growth_service):
        """Test getting requirements when no growth data exists"""
        # Arrange
        mock_repository = Mock()
        mock_repository.get_by_plant_id = AsyncMock(return_value=None)
        plant_growth_service.repository = mock_repository

        # Act & Assert
        with pytest.raises(ValueError, match="No growth data found"):
            await plant_growth_service.get_requirements(1)

    async def test_get_timeline_success(self, plant_growth_service, mock_growth_data):
        """Test getting growth timeline"""
        # Arrange
        mock_repository = Mock()
        mock_repository.get_by_plant_id = AsyncMock(return_value=Mock(
            growth_stages=mock_growth_data["growth_stages"]
        ))
        plant_growth_service.repository = mock_repository

        # Act
        result = await plant_growth_service.get_timeline(1)

        # Assert
        assert result["plant_id"] == 1
        assert result["total_days"] == 25  # Max end_day from stages
        assert len(result["stages"]) == 2

    async def test_get_care_tips_for_stage(self, plant_growth_service, mock_growth_data):
        """Test getting care tips for specific stage"""
        # Arrange
        mock_repository = Mock()
        mock_repository.get_by_plant_id = AsyncMock(return_value=Mock(
            care_tips=mock_growth_data["care_tips"],
            growth_stages=mock_growth_data["growth_stages"]
        ))
        plant_growth_service.repository = mock_repository

        # Act
        result = await plant_growth_service.get_care_tips_for_stage(1, "germination")

        # Assert
        assert result["stage_name"] == "germination"
        assert len(result["tips"]) == 2
        assert result["tips"][0]["tip"] == "Keep soil moist"


# ============================================================================
# PLANT INSTANCE SERVICE TESTS
# ============================================================================

class TestPlantInstanceService:
    """Tests for PlantInstanceService"""

    @pytest.fixture
    def plant_instance_service(self, mock_db):
        """PlantInstanceService instance"""
        return PlantInstanceService(mock_db)

    async def test_start_tracking_success(
        self, plant_instance_service, mock_plant, mock_plant_instance
    ):
        """Test starting plant tracking successfully"""
        # Arrange
        mock_growth_service = Mock()
        mock_growth_service.get_plant_by_id = AsyncMock(return_value=mock_plant)
        mock_growth_service.get_or_generate_growth_data = AsyncMock()
        plant_instance_service.growth_service = mock_growth_service

        mock_repository = Mock()
        mock_repository.create = AsyncMock(return_value=mock_plant_instance)
        plant_instance_service.repository = mock_repository

        # Act
        result = await plant_instance_service.start_tracking(
            user_id=1,
            plant_id=1,
            plant_nickname="My Basil",
            start_date=date.today(),
            user_data={"experience_level": "beginner"}
        )

        # Assert
        assert result["instance_id"] == 1
        assert result["plant_nickname"] == "My Basil"
        assert "expected_maturity_date" in result
        mock_growth_service.get_or_generate_growth_data.assert_called_once()

    async def test_start_tracking_plant_not_found(self, plant_instance_service):
        """Test starting tracking when plant doesn't exist"""
        # Arrange
        mock_growth_service = Mock()
        mock_growth_service.get_plant_by_id = AsyncMock(return_value=None)
        plant_instance_service.growth_service = mock_growth_service

        # Act & Assert
        with pytest.raises(ValueError, match="Plant with ID 999 not found"):
            await plant_instance_service.start_tracking(
                user_id=1,
                plant_id=999,
                plant_nickname="Test",
                start_date=date.today(),
                user_data={}
            )

    async def test_get_user_plants_with_pagination(self, plant_instance_service, mock_plant_instance):
        """Test getting user plants with pagination"""
        # Arrange
        mock_repository = Mock()
        mock_repository.get_user_instances = AsyncMock(return_value=[mock_plant_instance])
        mock_repository.count_user_instances = AsyncMock(return_value=1)
        mock_repository.calculate_days_elapsed = AsyncMock(return_value=15)
        plant_instance_service.repository = mock_repository

        with patch.object(plant_instance_service, 'calculate_progress_percentage', return_value=25.0):
            # Act
            result = await plant_instance_service.get_user_plants(
                user_id=1,
                page=1,
                limit=20
            )

            # Assert
            assert len(result["plants"]) == 1
            assert result["total_count"] == 1
            assert result["pagination"]["page"] == 1

    async def test_get_instance_details_success(self, plant_instance_service, mock_plant_instance, mock_growth_data):
        """Test getting detailed instance information"""
        # Arrange
        mock_repository = Mock()
        mock_repository.get_by_id = AsyncMock(return_value=mock_plant_instance)
        mock_repository.calculate_days_elapsed = AsyncMock(return_value=15)
        plant_instance_service.repository = mock_repository

        mock_growth_service = Mock()
        mock_growth_service.get_timeline = AsyncMock(return_value={
            "stages": mock_growth_data["growth_stages"]
        })
        mock_growth_service.get_care_tips_for_stage = AsyncMock(return_value={
            "tips": [{"tip": "Keep soil moist"}]
        })
        plant_instance_service.growth_service = mock_growth_service

        with patch.object(plant_instance_service, 'calculate_progress_percentage', return_value=25.0):
            # Act
            result = await plant_instance_service.get_instance_details(1)

            # Assert
            assert result["instance_id"] == 1
            assert "plant_details" in result
            assert "tracking_info" in result
            assert "timeline" in result
            assert len(result["current_tips"]) == 1

    async def test_update_progress_success(self, plant_instance_service, mock_plant_instance):
        """Test updating plant progress"""
        # Arrange
        mock_repository = Mock()
        mock_repository.update = AsyncMock(return_value=mock_plant_instance)
        plant_instance_service.repository = mock_repository

        # Act
        result = await plant_instance_service.update_progress(
            instance_id=1,
            current_stage="seedling",
            user_notes="Growing well!"
        )

        # Assert
        assert result["instance_id"] == 1
        assert "message" in result
        mock_repository.update.assert_called_once()

    async def test_auto_update_stage_changes_stage(
        self, plant_instance_service, mock_plant_instance, mock_growth_data
    ):
        """Test auto-updating stage when it should change"""
        # Arrange
        mock_plant_instance.current_stage = "germination"

        mock_repository = Mock()
        mock_repository.get_by_id = AsyncMock(return_value=mock_plant_instance)
        mock_repository.calculate_days_elapsed = AsyncMock(return_value=20)  # In seedling range
        mock_repository.update_stage = AsyncMock()
        plant_instance_service.repository = mock_repository

        mock_growth_service = Mock()
        mock_growth_service.get_timeline = AsyncMock(return_value={
            "stages": mock_growth_data["growth_stages"]
        })
        plant_instance_service.growth_service = mock_growth_service

        # Act
        result = await plant_instance_service.auto_update_stage(1)

        # Assert
        assert result == "seedling"
        mock_repository.update_stage.assert_called_once_with(1, "seedling")

    async def test_calculate_progress_percentage(self, plant_instance_service, mock_plant_instance):
        """Test calculating progress percentage"""
        # Arrange
        mock_plant_instance.start_date = date.today() - timedelta(days=15)
        mock_plant_instance.expected_maturity_date = date.today() + timedelta(days=45)

        # Act
        result = await plant_instance_service.calculate_progress_percentage(mock_plant_instance)

        # Assert
        assert result == 25.0  # 15 days out of 60 total


# ============================================================================
# PROGRESS TRACKING SERVICE TESTS
# ============================================================================

class TestProgressTrackingService:
    """Tests for ProgressTrackingService"""

    @pytest.fixture
    def progress_tracking_service(self, mock_db):
        """ProgressTrackingService instance"""
        return ProgressTrackingService(mock_db)

    async def test_mark_checklist_item_complete(self, progress_tracking_service):
        """Test marking checklist item as complete"""
        # Arrange
        mock_repository = Mock()
        mock_repository.mark_complete = AsyncMock()
        mock_repository.get_completed_count = AsyncMock(return_value=5)
        mock_repository.get_total_count = AsyncMock(return_value=10)
        mock_repository.get_completion_percentage = AsyncMock(return_value=50.0)
        progress_tracking_service.repository = mock_repository

        # Act
        result = await progress_tracking_service.mark_checklist_item_complete(
            instance_id=1,
            checklist_item_key="tools_garden_trowel",
            is_completed=True,
            user_notes="Purchased!"
        )

        # Assert
        assert result["success"] is True
        assert result["progress_summary"]["completed_items"] == 5
        assert result["progress_summary"]["completion_percentage"] == 50.0
        mock_repository.mark_complete.assert_called_once()

    async def test_get_progress_summary(self, progress_tracking_service):
        """Test getting progress summary"""
        # Arrange
        mock_repository = Mock()
        mock_repository.get_completed_count = AsyncMock(return_value=7)
        mock_repository.get_total_count = AsyncMock(return_value=10)
        mock_repository.get_completion_percentage = AsyncMock(return_value=70.0)
        progress_tracking_service.repository = mock_repository

        # Act
        result = await progress_tracking_service.get_progress_summary(1)

        # Assert
        assert result["instance_id"] == 1
        assert result["completed_items"] == 7
        assert result["total_items"] == 10
        assert result["completion_percentage"] == 70.0

    async def test_initialize_checklist_success(self, progress_tracking_service, mock_growth_data):
        """Test initializing checklist from requirements"""
        # Arrange
        mock_growth_service = Mock()
        mock_growth_service.get_requirements = AsyncMock(return_value={
            "requirements": mock_growth_data["requirements_checklist"]
        })
        progress_tracking_service.growth_service = mock_growth_service

        mock_repository = Mock()
        mock_repository.bulk_create = AsyncMock(return_value=[Mock(), Mock()])
        progress_tracking_service.repository = mock_repository

        # Act
        result = await progress_tracking_service.initialize_checklist(
            instance_id=1,
            plant_id=1
        )

        # Assert
        assert result["success"] is True
        assert result["items_created"] == 2

    async def test_initialize_checklist_no_growth_data(self, progress_tracking_service):
        """Test initializing checklist when no growth data exists"""
        # Arrange
        mock_growth_service = Mock()
        mock_growth_service.get_requirements = AsyncMock(side_effect=ValueError("No data"))
        progress_tracking_service.growth_service = mock_growth_service

        # Act
        result = await progress_tracking_service.initialize_checklist(
            instance_id=1,
            plant_id=1
        )

        # Assert
        assert result["success"] is False
        assert "No growth data available" in result["message"]

    async def test_get_current_stage_tips(self, progress_tracking_service, mock_growth_data):
        """Test getting randomized current stage tips"""
        # Arrange
        mock_growth_service = Mock()
        mock_growth_service.get_care_tips_for_stage = AsyncMock(return_value={
            "tips": mock_growth_data["care_tips"][0]["tips"]
        })
        progress_tracking_service.growth_service = mock_growth_service

        # Act
        result = await progress_tracking_service.get_current_stage_tips(
            instance_id=1,
            plant_id=1,
            current_stage="germination",
            limit=3
        )

        # Assert
        assert len(result) <= 3
        assert all(isinstance(tip, str) for tip in result)

    async def test_get_stage_info(self, progress_tracking_service, mock_growth_data):
        """Test getting stage information"""
        # Arrange
        mock_growth_service = Mock()
        mock_growth_service.get_timeline = AsyncMock(return_value={
            "stages": mock_growth_data["growth_stages"]
        })
        progress_tracking_service.growth_service = mock_growth_service

        # Act
        result = await progress_tracking_service.get_stage_info(
            plant_id=1,
            current_stage="germination",
            days_elapsed=5
        )

        # Assert
        assert result["stage_name"] == "germination"
        assert result["days_in_stage"] == 5
        assert result["estimated_days_remaining"] == 5  # end_day 10 - 5 elapsed

    async def test_delete_all_tracking(self, progress_tracking_service):
        """Test deleting all tracking data for instance"""
        # Arrange
        mock_repository = Mock()
        mock_repository.delete_by_instance = AsyncMock(return_value=10)
        progress_tracking_service.repository = mock_repository

        # Act
        result = await progress_tracking_service.delete_all_tracking(1)

        # Assert
        assert result == 10
        mock_repository.delete_by_instance.assert_called_once_with(1)
