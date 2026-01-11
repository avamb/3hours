"""
MINDSETHAPPYBOT - Inline keyboards
Inline buttons for various bot interactions
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.utils.localization import get_onboarding_text


def get_onboarding_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for address form selection during onboarding.

    Args:
        language_code: User's Telegram language code for button localization
    """
    informal_text = get_onboarding_text("address_informal_button", language_code)
    formal_text = get_onboarding_text("address_formal_button", language_code)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=informal_text, callback_data="address_informal"),
                InlineKeyboardButton(text=formal_text, callback_data="address_formal"),
            ],
        ]
    )
    return keyboard


def get_main_menu_inline() -> InlineKeyboardMarkup:
    """Create inline main menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Мои моменты", callback_data="menu_moments"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="menu_stats"),
            ],
            [
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings"),
                InlineKeyboardButton(text="💬 Поговорить", callback_data="menu_talk"),
            ],
        ]
    )
    return keyboard


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Create settings menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🕐 Активные часы", callback_data="settings_hours"),
            ],
            [
                InlineKeyboardButton(text="⏰ Интервал", callback_data="settings_interval"),
            ],
            [
                InlineKeyboardButton(text="🌍 Часовой пояс", callback_data="settings_timezone"),
            ],
            [
                InlineKeyboardButton(text="👤 Социальный профиль", callback_data="settings_social"),
            ],
            [
                InlineKeyboardButton(text="🗣 Форма обращения", callback_data="settings_address"),
            ],
            [
                InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings_notifications"),
            ],
            [
                InlineKeyboardButton(text="🔄 Сбросить настройки", callback_data="settings_reset"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"),
            ],
        ]
    )
    return keyboard


def get_social_profile_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for social profile settings"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Добавить соцсеть", callback_data="social_add"),
            ],
            [
                InlineKeyboardButton(text="📝 Редактировать био", callback_data="social_bio"),
            ],
            [
                InlineKeyboardButton(text="🔍 Определить интересы", callback_data="social_parse"),
            ],
            [
                InlineKeyboardButton(text="🗑 Удалить ссылку", callback_data="social_remove"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_back"),
            ],
        ]
    )
    return keyboard


def get_social_remove_keyboard(profile_urls: dict) -> InlineKeyboardMarkup:
    """Create keyboard for removing social links"""
    network_names = {
        "instagram": "Instagram",
        "facebook": "Facebook",
        "twitter": "Twitter/X",
        "linkedin": "LinkedIn",
        "vk": "ВКонтакте",
        "telegram_channel": "Telegram канал",
        "youtube": "YouTube",
        "tiktok": "TikTok",
    }

    rows = []
    for network, url in profile_urls.items():
        if url:
            name = network_names.get(network, network)
            rows.append([
                InlineKeyboardButton(text=f"❌ {name}", callback_data=f"social_del_{network}")
            ])

    if not rows:
        rows.append([
            InlineKeyboardButton(text="Нет добавленных соцсетей", callback_data="noop")
        ])

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="social_back")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_timezone_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for selecting timezone"""
    # Common timezones relevant for Russian-speaking users
    timezones = [
        ("🇷🇺 Москва (UTC+3)", "Europe/Moscow"),
        ("🇷🇺 Калининград (UTC+2)", "Europe/Kaliningrad"),
        ("🇷🇺 Самара (UTC+4)", "Europe/Samara"),
        ("🇷🇺 Екатеринбург (UTC+5)", "Asia/Yekaterinburg"),
        ("🇷🇺 Омск (UTC+6)", "Asia/Omsk"),
        ("🇷🇺 Красноярск (UTC+7)", "Asia/Krasnoyarsk"),
        ("🇷🇺 Иркутск (UTC+8)", "Asia/Irkutsk"),
        ("🇷🇺 Якутск (UTC+9)", "Asia/Yakutsk"),
        ("🇷🇺 Владивосток (UTC+10)", "Asia/Vladivostok"),
        ("🇷🇺 Магадан (UTC+11)", "Asia/Magadan"),
        ("🇷🇺 Камчатка (UTC+12)", "Asia/Kamchatka"),
        ("🇺🇦 Киев (UTC+2)", "Europe/Kiev"),
        ("🇧🇾 Минск (UTC+3)", "Europe/Minsk"),
        ("🇰🇿 Алматы (UTC+6)", "Asia/Almaty"),
        ("🇺🇿 Ташкент (UTC+5)", "Asia/Tashkent"),
        ("🇬🇪 Тбилиси (UTC+4)", "Asia/Tbilisi"),
        ("🇦🇲 Ереван (UTC+4)", "Asia/Yerevan"),
        ("🇦🇿 Баку (UTC+4)", "Asia/Baku"),
        ("UTC (Универсальное)", "UTC"),
    ]

    rows = []
    for label, tz in timezones:
        rows.append([
            InlineKeyboardButton(text=label, callback_data=f"timezone_{tz}")
        ])

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_back")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_hours_keyboard(mode: str, start_hour: str = None) -> InlineKeyboardMarkup:
    """
    Create keyboard for selecting hours
    mode: 'start' or 'end'
    """
    hours = ["06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]

    # Create rows of 4 buttons each
    rows = []
    for i in range(0, len(hours), 4):
        row = []
        for hour in hours[i:i+4]:
            if mode == "start":
                callback_data = f"hour_start_{hour}"
            else:
                callback_data = f"hour_end_{hour}_{start_hour}"
            row.append(InlineKeyboardButton(text=f"{hour}:00", callback_data=callback_data))
        rows.append(row)

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_back")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_interval_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for selecting notification interval"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 час", callback_data="interval_1"),
                InlineKeyboardButton(text="2 часа", callback_data="interval_2"),
            ],
            [
                InlineKeyboardButton(text="3 часа", callback_data="interval_3"),
                InlineKeyboardButton(text="4 часа", callback_data="interval_4"),
            ],
            [
                InlineKeyboardButton(text="6 часов", callback_data="interval_6"),
                InlineKeyboardButton(text="8 часов", callback_data="interval_8"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_back"),
            ],
        ]
    )
    return keyboard


def get_address_form_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for address form selection"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="На «ты» 😊", callback_data="address_informal"),
                InlineKeyboardButton(text="На «вы» 🤝", callback_data="address_formal"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_back"),
            ],
        ]
    )
    return keyboard


def get_moments_keyboard(page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Create keyboard for moments list navigation"""
    buttons = []

    # Filter buttons row
    buttons.append([
        InlineKeyboardButton(text="Сегодня", callback_data="filter_today"),
        InlineKeyboardButton(text="Неделя", callback_data="filter_week"),
        InlineKeyboardButton(text="Месяц", callback_data="filter_month"),
    ])

    # Navigation row (if multiple pages)
    if total_pages > 1:
        nav_row = []
        if page > 1:
            nav_row.append(InlineKeyboardButton(text="⬅️", callback_data="moments_prev"))
        nav_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
        if page < total_pages:
            nav_row.append(InlineKeyboardButton(text="➡️", callback_data="moments_next"))
        buttons.append(nav_row)

    # Random moment button
    buttons.append([
        InlineKeyboardButton(text="🎲 Случайный момент", callback_data="moments_random"),
    ])

    # Back button
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_dialog_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for free dialog mode"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚪 Выйти из диалога", callback_data="dialog_exit"),
            ],
        ]
    )
    return keyboard


def get_delete_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for delete data confirmation"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Да, удалить всё", callback_data="delete_confirm"),
            ],
            [
                InlineKeyboardButton(text="✅ Нет, отменить", callback_data="delete_cancel"),
            ],
        ]
    )
    return keyboard


def get_question_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for scheduled question (with skip option)"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏭ Пропустить", callback_data="question_skip"),
            ],
        ]
    )
    return keyboard


def get_moment_delete_confirm_keyboard(moment_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for confirming moment deletion"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"moment_delete_{moment_id}"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="moments_random"),
            ],
        ]
    )
    return keyboard


def get_random_moment_keyboard(moment_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for random moment view with delete option"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎲 Ещё случайный", callback_data="moments_random"),
            ],
            [
                InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"moment_delete_confirm_{moment_id}"),
            ],
            [
                InlineKeyboardButton(text="📖 Все моменты", callback_data="menu_moments"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"),
            ],
        ]
    )
    return keyboard


def get_feedback_category_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for selecting feedback category"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💡 Идея/предложение", callback_data="feedback_suggestion"),
            ],
            [
                InlineKeyboardButton(text="🐛 Сообщить об ошибке", callback_data="feedback_bug"),
            ],
            [
                InlineKeyboardButton(text="💬 Другое", callback_data="feedback_other"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Отмена", callback_data="feedback_cancel"),
            ],
        ]
    )
    return keyboard


def get_feedback_confirm_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for confirming feedback submission"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Отправить", callback_data="feedback_submit"),
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="feedback_cancel"),
            ],
        ]
    )
    return keyboard


def get_feedback_thanks_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard after feedback submission"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💡 Предложить ещё", callback_data="feedback_new"),
            ],
            [
                InlineKeyboardButton(text="⬅️ В меню", callback_data="main_menu"),
            ],
        ]
    )
    return keyboard


def get_summary_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for selecting summary type"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 Еженедельное", callback_data="summary_weekly"),
            ],
            [
                InlineKeyboardButton(text="🗓 Месячное", callback_data="summary_monthly"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"),
            ],
        ]
    )
    return keyboard
