"""
MINDSETHAPPYBOT - Reply keyboards
Persistent keyboard with main menu buttons
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.utils.localization import get_menu_text


def get_main_menu_keyboard(language_code: str = "ru") -> ReplyKeyboardMarkup:
    """
    Create main menu reply keyboard
    Layout:
    [📖 Мои моменты] [📊 Статистика]
    [⚙️ Настройки] [💬 Поговорить]
    [💡 Предложить идею]

    Args:
        language_code: User's language code for button localization
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_menu_text("menu_moments", language_code)),
                KeyboardButton(text=get_menu_text("menu_stats", language_code)),
            ],
            [
                KeyboardButton(text=get_menu_text("menu_settings", language_code)),
                KeyboardButton(text=get_menu_text("menu_talk", language_code)),
            ],
            [
                KeyboardButton(text=get_menu_text("menu_feedback", language_code)),
                KeyboardButton(text=get_menu_text("menu_pause", language_code)),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
    return keyboard
