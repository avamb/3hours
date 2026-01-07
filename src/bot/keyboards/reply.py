"""
MINDSETHAPPYBOT - Reply keyboards
Persistent keyboard with main menu buttons
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Create main menu reply keyboard
    Layout:
    [📖 Мои моменты] [📊 Статистика]
    [⚙️ Настройки] [💬 Поговорить]
    [💡 Предложить идею]
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📖 Мои моменты"),
                KeyboardButton(text="📊 Статистика"),
            ],
            [
                KeyboardButton(text="⚙️ Настройки"),
                KeyboardButton(text="💬 Поговорить"),
            ],
            [
                KeyboardButton(text="💡 Предложить идею"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
    return keyboard
