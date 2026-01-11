"""
MINDSETHAPPYBOT - Inline keyboards
Inline buttons for various bot interactions
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.utils.localization import get_onboarding_text, get_menu_text


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


def get_main_menu_inline(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create inline main menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("menu_moments", language_code), callback_data="menu_moments"),
                InlineKeyboardButton(text=get_menu_text("menu_stats", language_code), callback_data="menu_stats"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("menu_settings", language_code), callback_data="menu_settings"),
                InlineKeyboardButton(text=get_menu_text("menu_talk", language_code), callback_data="menu_talk"),
            ],
        ]
    )
    return keyboard


def get_settings_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create settings menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("settings_hours", language_code), callback_data="settings_hours"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("settings_interval", language_code), callback_data="settings_interval"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("settings_timezone", language_code), callback_data="settings_timezone"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("settings_social", language_code), callback_data="settings_social"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("settings_address", language_code), callback_data="settings_address"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("settings_gender", language_code), callback_data="settings_gender"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("settings_notifications", language_code), callback_data="settings_notifications"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("settings_reset", language_code), callback_data="settings_reset"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="main_menu"),
            ],
        ]
    )
    return keyboard


def get_social_profile_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for social profile settings"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("social_add", language_code), callback_data="social_add"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("social_bio", language_code), callback_data="social_bio"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("social_parse", language_code), callback_data="social_parse"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("social_remove", language_code), callback_data="social_remove"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="settings_back"),
            ],
        ]
    )
    return keyboard


def get_social_remove_keyboard(profile_urls: dict, language_code: str = "ru") -> InlineKeyboardMarkup:
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
            InlineKeyboardButton(text=get_menu_text("no_social_links", language_code), callback_data="noop")
        ])

    rows.append([InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="social_back")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_timezone_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
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

    rows.append([InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="settings_back")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_hours_keyboard(mode: str, start_hour: str = None, language_code: str = "ru") -> InlineKeyboardMarkup:
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

    rows.append([InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="settings_back")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_interval_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for selecting notification interval"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("interval_1h", language_code), callback_data="interval_1"),
                InlineKeyboardButton(text=get_menu_text("interval_2h", language_code), callback_data="interval_2"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("interval_3h", language_code), callback_data="interval_3"),
                InlineKeyboardButton(text=get_menu_text("interval_4h", language_code), callback_data="interval_4"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("interval_6h", language_code), callback_data="interval_6"),
                InlineKeyboardButton(text=get_menu_text("interval_8h", language_code), callback_data="interval_8"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="settings_back"),
            ],
        ]
    )
    return keyboard


def get_address_form_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for address form selection"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("address_informal", language_code), callback_data="address_informal"),
                InlineKeyboardButton(text=get_menu_text("address_formal", language_code), callback_data="address_formal"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="settings_back"),
            ],
        ]
    )
    return keyboard


def get_gender_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for gender selection"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("gender_male", language_code), callback_data="gender_male"),
                InlineKeyboardButton(text=get_menu_text("gender_female", language_code), callback_data="gender_female"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="settings_back"),
            ],
        ]
    )
    return keyboard


def get_moments_keyboard(page: int = 1, total_pages: int = 1, language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for moments list navigation"""
    buttons = []

    # Filter buttons row
    buttons.append([
        InlineKeyboardButton(text=get_menu_text("filter_today", language_code), callback_data="filter_today"),
        InlineKeyboardButton(text=get_menu_text("filter_week", language_code), callback_data="filter_week"),
        InlineKeyboardButton(text=get_menu_text("filter_month", language_code), callback_data="filter_month"),
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
        InlineKeyboardButton(text=get_menu_text("random_moment", language_code), callback_data="moments_random"),
    ])

    # Back button
    buttons.append([
        InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="main_menu"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_dialog_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for free dialog mode"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("exit_dialog", language_code), callback_data="dialog_exit"),
            ],
        ]
    )
    return keyboard


def get_delete_confirmation_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for delete data confirmation"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("confirm_delete", language_code), callback_data="delete_confirm"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("cancel_delete", language_code), callback_data="delete_cancel"),
            ],
        ]
    )
    return keyboard


def get_question_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for scheduled question (with skip option)"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("skip_question", language_code), callback_data="question_skip"),
            ],
        ]
    )
    return keyboard


def get_moment_delete_confirm_keyboard(moment_id: int, language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for confirming moment deletion"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("confirm_delete_moment", language_code), callback_data=f"moment_delete_{moment_id}"),
                InlineKeyboardButton(text=get_menu_text("cancel", language_code), callback_data="moments_random"),
            ],
        ]
    )
    return keyboard


def get_random_moment_keyboard(moment_id: int, language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for random moment view with delete option"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("another_random", language_code), callback_data="moments_random"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("delete_moment", language_code), callback_data=f"moment_delete_confirm_{moment_id}"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("all_moments", language_code), callback_data="menu_moments"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="main_menu"),
            ],
        ]
    )
    return keyboard


def get_feedback_category_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for selecting feedback category"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("feedback_suggestion", language_code), callback_data="feedback_suggestion"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("feedback_bug", language_code), callback_data="feedback_bug"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("feedback_other", language_code), callback_data="feedback_other"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("feedback_cancel", language_code), callback_data="feedback_cancel"),
            ],
        ]
    )
    return keyboard


def get_feedback_confirm_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for confirming feedback submission"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("feedback_submit", language_code), callback_data="feedback_submit"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("cancel", language_code), callback_data="feedback_cancel"),
            ],
        ]
    )
    return keyboard


def get_feedback_thanks_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard after feedback submission"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("feedback_new", language_code), callback_data="feedback_new"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("feedback_menu", language_code), callback_data="main_menu"),
            ],
        ]
    )
    return keyboard


def get_summary_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for selecting summary type"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_menu_text("summary_weekly", language_code), callback_data="summary_weekly"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("summary_monthly", language_code), callback_data="summary_monthly"),
            ],
            [
                InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="main_menu"),
            ],
        ]
    )
    return keyboard
