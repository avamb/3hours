"""
MINDSETHAPPYBOT - Unit tests for command handlers
Tests the /start command and related functionality
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import time

from src.bot.handlers.commands import (
    cmd_start,
    get_localized_welcome_text,
    get_localized_welcome_back_text,
    send_welcome_image,
)


class TestLocalizedWelcomeText:
    """Tests for get_localized_welcome_text function"""

    def test_russian_text_by_default(self):
        """Test that Russian text is returned by default"""
        result = get_localized_welcome_text("Иван", "ru")
        assert "Привет, Иван!" in result
        assert "позитивного мышления" in result
        assert "👋" in result

    def test_english_text_for_en_language(self):
        """Test that English text is returned for English users"""
        result = get_localized_welcome_text("John", "en")
        assert "Hello, John!" in result
        assert "positive thinking" in result
        assert "👋" in result

    def test_english_text_for_en_us_language(self):
        """Test that English text is returned for en-US users"""
        result = get_localized_welcome_text("John", "en-US")
        assert "Hello, John!" in result

    def test_ukrainian_text_for_uk_language(self):
        """Test that Ukrainian text is returned for Ukrainian users"""
        result = get_localized_welcome_text("Олена", "uk")
        assert "Привіт, Олена!" in result
        assert "позитивного мислення" in result

    def test_russian_text_for_unknown_language(self):
        """Test that Russian is used as fallback for unknown languages"""
        result = get_localized_welcome_text("User", "xx")
        assert "Привет, User!" in result

    def test_russian_text_for_none_language(self):
        """Test that Russian is used when language_code is None"""
        result = get_localized_welcome_text("User", None)
        assert "Привет, User!" in result


class TestLocalizedWelcomeBackText:
    """Tests for get_localized_welcome_back_text function"""

    def test_russian_text_by_default(self):
        """Test that Russian welcome back text is returned by default"""
        result = get_localized_welcome_back_text("Иван", "ru")
        assert "С возвращением, Иван!" in result
        assert "💝" in result

    def test_english_text_for_en_language(self):
        """Test that English welcome back text is returned for English users"""
        result = get_localized_welcome_back_text("John", "en")
        assert "Welcome back, John!" in result

    def test_ukrainian_text_for_uk_language(self):
        """Test that Ukrainian welcome back text is returned"""
        result = get_localized_welcome_back_text("Олена", "uk")
        assert "З поверненням, Олена!" in result


class TestSendWelcomeImage:
    """Tests for send_welcome_image function"""

    @pytest.mark.asyncio
    async def test_send_welcome_image_success_with_url(self):
        """Test that welcome image is sent via URL when local file doesn't exist"""
        mock_message = AsyncMock()

        with patch('src.bot.handlers.commands.WELCOME_IMAGE_PATH') as mock_path:
            mock_path.exists.return_value = False

            result = await send_welcome_image(mock_message)

            # Should return True on success
            assert result is True
            # Should call answer_photo
            mock_message.answer_photo.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_welcome_image_handles_exception(self):
        """Test that send_welcome_image handles exceptions gracefully"""
        mock_message = AsyncMock()
        mock_message.answer_photo.side_effect = Exception("Network error")

        with patch('src.bot.handlers.commands.WELCOME_IMAGE_PATH') as mock_path:
            mock_path.exists.return_value = False

            result = await send_welcome_image(mock_message)

            # Should return False on failure
            assert result is False


class TestCmdStart:
    """Tests for cmd_start command handler"""

    @pytest.fixture
    def mock_telegram_user(self):
        """Create a mock Telegram user"""
        user = MagicMock()
        user.id = 12345
        user.username = "testuser"
        user.first_name = "Test"
        user.language_code = "ru"
        return user

    @pytest.fixture
    def mock_db_user_new(self):
        """Create a mock database user (new, not completed onboarding)"""
        user = MagicMock()
        user.first_name = "Test"
        user.language_code = "ru"
        user.onboarding_completed = False
        user.formal_address = False
        return user

    @pytest.fixture
    def mock_db_user_existing(self):
        """Create a mock database user (existing, completed onboarding)"""
        user = MagicMock()
        user.first_name = "Test"
        user.language_code = "ru"
        user.onboarding_completed = True
        user.formal_address = False
        user.active_hours_start = time(9, 0)
        user.active_hours_end = time(21, 0)
        user.notification_interval_hours = 3
        user.notifications_enabled = True
        return user

    @pytest.mark.asyncio
    async def test_cmd_start_new_user_sends_welcome_image(self, mock_telegram_user, mock_db_user_new):
        """Test that new users receive welcome image"""
        mock_message = AsyncMock()
        mock_message.from_user = mock_telegram_user

        with patch('src.bot.handlers.commands.UserService') as MockUserService:
            mock_service = MockUserService.return_value
            mock_service.get_or_create_user = AsyncMock(return_value=mock_db_user_new)

            with patch('src.bot.handlers.commands.send_welcome_image') as mock_send_image:
                mock_send_image.return_value = True

                await cmd_start(mock_message)

                # Should send welcome image
                mock_send_image.assert_called_once_with(mock_message)
                # Should send welcome text with keyboard
                mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_start_new_user_sends_welcome_text(self, mock_telegram_user, mock_db_user_new):
        """Test that new users receive welcome text with onboarding keyboard"""
        mock_message = AsyncMock()
        mock_message.from_user = mock_telegram_user

        with patch('src.bot.handlers.commands.UserService') as MockUserService:
            mock_service = MockUserService.return_value
            mock_service.get_or_create_user = AsyncMock(return_value=mock_db_user_new)

            with patch('src.bot.handlers.commands.send_welcome_image'):
                await cmd_start(mock_message)

                # Check that welcome message was sent
                call_args = mock_message.answer.call_args
                welcome_text = call_args[0][0]
                assert "Привет, Test!" in welcome_text
                assert "reply_markup" in call_args.kwargs

    @pytest.mark.asyncio
    async def test_cmd_start_existing_user_no_image(self, mock_telegram_user, mock_db_user_existing):
        """Test that existing users don't receive welcome image"""
        mock_message = AsyncMock()
        mock_message.from_user = mock_telegram_user

        with patch('src.bot.handlers.commands.UserService') as MockUserService:
            mock_service = MockUserService.return_value
            mock_service.get_or_create_user = AsyncMock(return_value=mock_db_user_existing)

            with patch('src.bot.handlers.commands.send_welcome_image') as mock_send_image:
                await cmd_start(mock_message)

                # Should NOT send welcome image
                mock_send_image.assert_not_called()
                # Should send welcome back text
                mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_start_existing_user_welcome_back_message(self, mock_telegram_user, mock_db_user_existing):
        """Test that existing users receive welcome back message"""
        mock_message = AsyncMock()
        mock_message.from_user = mock_telegram_user

        with patch('src.bot.handlers.commands.UserService') as MockUserService:
            mock_service = MockUserService.return_value
            mock_service.get_or_create_user = AsyncMock(return_value=mock_db_user_existing)

            await cmd_start(mock_message)

            call_args = mock_message.answer.call_args
            welcome_back_text = call_args[0][0]
            assert "С возвращением, Test!" in welcome_back_text

    @pytest.mark.asyncio
    async def test_cmd_start_user_name_detected(self, mock_telegram_user, mock_db_user_new):
        """Test that user name is detected from Telegram user object"""
        mock_message = AsyncMock()
        mock_message.from_user = mock_telegram_user
        mock_db_user_new.first_name = "ТестИмя"

        with patch('src.bot.handlers.commands.UserService') as MockUserService:
            mock_service = MockUserService.return_value
            mock_service.get_or_create_user = AsyncMock(return_value=mock_db_user_new)

            with patch('src.bot.handlers.commands.send_welcome_image'):
                await cmd_start(mock_message)

                call_args = mock_message.answer.call_args
                welcome_text = call_args[0][0]
                # User name should be in the welcome message
                assert "ТестИмя" in welcome_text

    @pytest.mark.asyncio
    async def test_cmd_start_language_detection_english(self, mock_db_user_new):
        """Test that English language is detected and used"""
        mock_telegram_user = MagicMock()
        mock_telegram_user.id = 12345
        mock_telegram_user.username = "testuser"
        mock_telegram_user.first_name = "John"
        mock_telegram_user.language_code = "en"

        mock_message = AsyncMock()
        mock_message.from_user = mock_telegram_user

        mock_db_user_new.first_name = "John"
        mock_db_user_new.language_code = "en"

        with patch('src.bot.handlers.commands.UserService') as MockUserService:
            mock_service = MockUserService.return_value
            mock_service.get_or_create_user = AsyncMock(return_value=mock_db_user_new)

            with patch('src.bot.handlers.commands.send_welcome_image'):
                await cmd_start(mock_message)

                call_args = mock_message.answer.call_args
                welcome_text = call_args[0][0]
                # Should be in English
                assert "Hello, John!" in welcome_text
