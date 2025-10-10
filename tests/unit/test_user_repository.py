"""
Unit tests for the user repository
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from app.repositories.user_repository import UserRepository
from app.models.database import User, UserProfile, UserFavorite, Plant, Suburb


@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def user_repo(mock_db):
    """User repository instance with mocked database"""
    return UserRepository(mock_db)


@pytest.fixture
def mock_user():
    """Mock user instance"""
    user = Mock(spec=User)
    user.id = 1
    user.google_id = "123456789"
    user.email = "test@example.com"
    user.name = "Test User"
    user.is_active = True
    user.suburb = None
    user.profile = None
    return user


@pytest.fixture
def mock_suburb():
    """Mock suburb instance"""
    suburb = Mock(spec=Suburb)
    suburb.id = 1
    suburb.name = "Richmond"
    suburb.postcode = "3121"
    suburb.latitude = -37.8136
    suburb.longitude = 144.9631
    return suburb


@pytest.fixture
def mock_profile():
    """Mock user profile instance"""
    profile = Mock(spec=UserProfile)
    profile.id = 1
    profile.user_id = 1
    profile.experience_level = "beginner"
    profile.garden_type = "balcony"
    profile.has_containers = True
    profile.organic_preference = True
    profile.created_at = datetime.utcnow()
    profile.updated_at = datetime.utcnow()
    return profile


@pytest.fixture
def mock_plant():
    """Mock plant instance"""
    plant = Mock(spec=Plant)
    plant.id = 1
    plant.plant_name = "Basil"
    plant.plant_category = "herb"
    return plant


@pytest.fixture
def mock_favorite():
    """Mock favorite instance"""
    favorite = Mock(spec=UserFavorite)
    favorite.id = 1
    favorite.user_id = 1
    favorite.plant_id = 1
    favorite.notes = "Love this plant"
    favorite.priority_level = 0
    favorite.created_at = datetime.utcnow()
    return favorite


class TestGetUserById:
    """Tests for getting user by ID"""

    async def test_get_user_by_id_found(self, user_repo, mock_db, mock_user):
        """Test getting user by ID when user exists"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        # Act
        result = await user_repo.get_user_by_id(1)

        # Assert
        assert result == mock_user
        mock_db.execute.assert_called_once()

    async def test_get_user_by_id_not_found(self, user_repo, mock_db):
        """Test getting user by ID when user doesn't exist"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Act
        result = await user_repo.get_user_by_id(999)

        # Assert
        assert result is None


class TestGetUserByGoogleId:
    """Tests for getting user by Google ID"""

    async def test_get_user_by_google_id_found(self, user_repo, mock_db, mock_user):
        """Test getting user by Google ID when user exists"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        # Act
        result = await user_repo.get_user_by_google_id("123456789")

        # Assert
        assert result == mock_user

    async def test_get_user_by_google_id_not_found(self, user_repo, mock_db):
        """Test getting user by Google ID when user doesn't exist"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Act
        result = await user_repo.get_user_by_google_id("nonexistent")

        # Assert
        assert result is None


class TestCreateUser:
    """Tests for creating users"""

    async def test_create_user_without_suburb(self, user_repo, mock_db, mock_user):
        """Test creating user without suburb"""
        # Arrange
        user_data = {
            'google_id': '123456789',
            'email': 'test@example.com',
            'name': 'Test User'
        }
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with pytest.mock.patch.object(User, '__new__', return_value=mock_user):
            # Act
            result = await user_repo.create_user(user_data)

            # Assert
            assert result == mock_user
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    async def test_create_user_with_suburb(self, user_repo, mock_db, mock_user, mock_suburb):
        """Test creating user with suburb lookup"""
        # Arrange
        user_data = {
            'google_id': '123456789',
            'email': 'test@example.com',
            'name': 'Test User',
            'suburb_name': 'Richmond'
        }

        # Mock suburb lookup
        mock_suburb_result = AsyncMock()
        mock_suburb_result.scalar_one_or_none.return_value = mock_suburb
        mock_db.execute.return_value = mock_suburb_result

        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with pytest.mock.patch.object(User, '__new__', return_value=mock_user):
            # Act
            result = await user_repo.create_user(user_data)

            # Assert
            assert result == mock_user
            mock_db.execute.assert_called_once()  # Suburb lookup


class TestUpdateUser:
    """Tests for updating users"""

    async def test_update_user_success(self, user_repo, mock_db, mock_user):
        """Test updating user successfully"""
        # Arrange
        update_data = {'name': 'Updated Name'}

        # Mock get_user_by_id
        with pytest.mock.patch.object(user_repo, 'get_user_by_id', return_value=mock_user):
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            # Act
            result = await user_repo.update_user(1, update_data)

            # Assert
            assert result == mock_user
            assert mock_user.name == 'Updated Name'
            mock_db.commit.assert_called_once()

    async def test_update_user_not_found(self, user_repo):
        """Test updating user when user doesn't exist"""
        # Arrange
        with pytest.mock.patch.object(user_repo, 'get_user_by_id', return_value=None):
            # Act & Assert
            with pytest.raises(ValueError, match="User with ID 999 not found"):
                await user_repo.update_user(999, {'name': 'New Name'})


class TestUserProfile:
    """Tests for user profile operations"""

    async def test_get_user_profile_found(self, user_repo, mock_db, mock_profile):
        """Test getting user profile when it exists"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_profile
        mock_db.execute.return_value = mock_result

        # Act
        result = await user_repo.get_user_profile(1)

        # Assert
        assert result == mock_profile

    async def test_create_new_profile(self, user_repo, mock_db, mock_profile):
        """Test creating new user profile"""
        # Arrange
        profile_data = {
            'experience_level': 'beginner',
            'garden_type': 'balcony'
        }

        # Mock no existing profile
        with pytest.mock.patch.object(user_repo, 'get_user_profile', return_value=None):
            mock_db.add = Mock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            with pytest.mock.patch.object(UserProfile, '__new__', return_value=mock_profile):
                # Act
                result = await user_repo.create_or_update_profile(1, profile_data)

                # Assert
                assert result == mock_profile
                mock_db.add.assert_called_once()

    async def test_update_existing_profile(self, user_repo, mock_db, mock_profile):
        """Test updating existing user profile"""
        # Arrange
        profile_data = {'experience_level': 'intermediate'}

        # Mock existing profile
        with pytest.mock.patch.object(user_repo, 'get_user_profile', return_value=mock_profile):
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            # Act
            result = await user_repo.create_or_update_profile(1, profile_data)

            # Assert
            assert result == mock_profile
            assert mock_profile.experience_level == 'intermediate'


class TestUserFavorites:
    """Tests for user favorites operations"""

    async def test_get_user_favorites(self, user_repo, mock_db, mock_favorite, mock_plant):
        """Test getting user's favorites"""
        # Arrange
        mock_favorite.plant = mock_plant
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [mock_favorite]
        mock_db.execute.return_value = mock_result

        # Act
        result = await user_repo.get_user_favorites(1)

        # Assert
        assert len(result) == 1
        assert result[0] == mock_favorite

    async def test_add_favorite_new(self, user_repo, mock_db, mock_favorite):
        """Test adding new favorite"""
        # Arrange
        # Mock no existing favorite
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with pytest.mock.patch.object(UserFavorite, '__new__', return_value=mock_favorite):
            # Act
            result = await user_repo.add_favorite(1, 1, "Great plant")

            # Assert
            assert result == mock_favorite
            mock_db.add.assert_called_once()

    async def test_add_favorite_existing(self, user_repo, mock_db, mock_favorite):
        """Test updating existing favorite"""
        # Arrange
        # Mock existing favorite
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_favorite
        mock_db.execute.return_value = mock_result

        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Act
        result = await user_repo.add_favorite(1, 1, "Updated notes")

        # Assert
        assert result == mock_favorite
        assert mock_favorite.notes == "Updated notes"

    async def test_remove_favorite_success(self, user_repo, mock_db, mock_favorite):
        """Test removing favorite successfully"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_favorite
        mock_db.execute.return_value = mock_result
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        # Act
        result = await user_repo.remove_favorite(1, 1)

        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(mock_favorite)

    async def test_remove_favorite_not_found(self, user_repo, mock_db):
        """Test removing favorite when it doesn't exist"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Act
        result = await user_repo.remove_favorite(1, 1)

        # Assert
        assert result is False

    async def test_is_favorite_true(self, user_repo, mock_db, mock_favorite):
        """Test checking if plant is favorite when it is"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_favorite
        mock_db.execute.return_value = mock_result

        # Act
        result = await user_repo.is_favorite(1, 1)

        # Assert
        assert result is True

    async def test_is_favorite_false(self, user_repo, mock_db):
        """Test checking if plant is favorite when it isn't"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Act
        result = await user_repo.is_favorite(1, 1)

        # Assert
        assert result is False

    async def test_sync_favorites(self, user_repo, mock_db, mock_favorite, mock_plant):
        """Test syncing favorites from localStorage"""
        # Arrange
        plant_ids = [1, 2, 3]

        # Mock existing favorites (plant 1 already exists)
        mock_favorite.plant_id = 1
        existing_favorites = [mock_favorite]

        # Mock plant existence check
        mock_plant_result = AsyncMock()
        mock_plant_result.scalar_one_or_none.return_value = mock_plant
        mock_db.execute.return_value = mock_plant_result

        mock_db.add = Mock()
        mock_db.commit = AsyncMock()

        with pytest.mock.patch.object(user_repo, 'get_user_favorites') as mock_get_favs:
            mock_get_favs.side_effect = [existing_favorites, existing_favorites]  # Before and after

            # Act
            result = await user_repo.sync_favorites(1, plant_ids)

            # Assert
            assert result == existing_favorites
            # Should add 2 new favorites (plants 2 and 3)
            assert mock_db.add.call_count == 2