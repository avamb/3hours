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
                InlineKeyboardButton(text=get_menu_text("settings_language", language_code), callback_data="settings_language"),
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


def get_language_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for language selection with most common languages"""
    # Most common languages with native names and flags
    languages = [
        ("🇬🇧 English", "en"),
        ("🇷🇺 Русский", "ru"),
        ("🇺🇦 Українська", "uk"),
        ("🇪🇸 Español", "es"),
        ("🇩🇪 Deutsch", "de"),
        ("🇫🇷 Français", "fr"),
        ("🇵🇹 Português", "pt"),
        ("🇮🇹 Italiano", "it"),
        ("🇨🇳 中文", "zh"),
        ("🇯🇵 日本語", "ja"),
        ("🇮🇱 עברית", "he"),
    ]

    rows = []
    # Create 2 columns per row
    for i in range(0, len(languages), 2):
        row = []
        for label, lang_code in languages[i:i+2]:
            row.append(InlineKeyboardButton(text=label, callback_data=f"language_{lang_code}"))
        rows.append(row)

    rows.append([InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="settings_back")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


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


def get_timezone_regions_keyboard(language_code: str = "ru") -> InlineKeyboardMarkup:
    """Create keyboard for selecting timezone region (first step)"""
    regions = [
        ("🌍 Europe", "tz_region_europe"),
        ("🌎 Americas", "tz_region_americas"),
        ("🌏 Asia", "tz_region_asia"),
        ("🌏 Australia & Pacific", "tz_region_pacific"),
        ("🌍 Africa & Middle East", "tz_region_africa"),
        ("🕐 UTC", "timezone_UTC"),
    ]

    rows = []
    for label, callback_data in regions:
        rows.append([InlineKeyboardButton(text=label, callback_data=callback_data)])

    rows.append([InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="settings_back")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_timezone_keyboard(language_code: str = "ru", region: str = None) -> InlineKeyboardMarkup:
    """Create keyboard for selecting timezone within a region"""
    # International timezone database organized by region
    timezone_data = {
        "europe": [
            ("🇬🇧 London (UTC+0/+1)", "Europe/London"),
            ("🇫🇷 Paris (UTC+1/+2)", "Europe/Paris"),
            ("🇩🇪 Berlin (UTC+1/+2)", "Europe/Berlin"),
            ("🇪🇸 Madrid (UTC+1/+2)", "Europe/Madrid"),
            ("🇮🇹 Rome (UTC+1/+2)", "Europe/Rome"),
            ("🇳🇱 Amsterdam (UTC+1/+2)", "Europe/Amsterdam"),
            ("🇧🇪 Brussels (UTC+1/+2)", "Europe/Brussels"),
            ("🇨🇭 Zurich (UTC+1/+2)", "Europe/Zurich"),
            ("🇦🇹 Vienna (UTC+1/+2)", "Europe/Vienna"),
            ("🇵🇱 Warsaw (UTC+1/+2)", "Europe/Warsaw"),
            ("🇨🇿 Prague (UTC+1/+2)", "Europe/Prague"),
            ("🇸🇪 Stockholm (UTC+1/+2)", "Europe/Stockholm"),
            ("🇳🇴 Oslo (UTC+1/+2)", "Europe/Oslo"),
            ("🇫🇮 Helsinki (UTC+2/+3)", "Europe/Helsinki"),
            ("🇬🇷 Athens (UTC+2/+3)", "Europe/Athens"),
            ("🇧🇬 Sofia (UTC+2/+3)", "Europe/Sofia"),
            ("🇷🇴 Bucharest (UTC+2/+3)", "Europe/Bucharest"),
            ("🇺🇦 Kyiv (UTC+2/+3)", "Europe/Kyiv"),
            ("🇹🇷 Istanbul (UTC+3)", "Europe/Istanbul"),
            ("🇷🇺 Moscow (UTC+3)", "Europe/Moscow"),
            ("🇧🇾 Minsk (UTC+3)", "Europe/Minsk"),
            ("🇷🇺 Kaliningrad (UTC+2)", "Europe/Kaliningrad"),
            ("🇷🇺 Samara (UTC+4)", "Europe/Samara"),
            ("🇵🇹 Lisbon (UTC+0/+1)", "Europe/Lisbon"),
            ("🇮🇪 Dublin (UTC+0/+1)", "Europe/Dublin"),
        ],
        "americas": [
            ("🇺🇸 New York (UTC-5/-4)", "America/New_York"),
            ("🇺🇸 Chicago (UTC-6/-5)", "America/Chicago"),
            ("🇺🇸 Denver (UTC-7/-6)", "America/Denver"),
            ("🇺🇸 Phoenix (UTC-7)", "America/Phoenix"),
            ("🇺🇸 Los Angeles (UTC-8/-7)", "America/Los_Angeles"),
            ("🇺🇸 Anchorage (UTC-9/-8)", "America/Anchorage"),
            ("🇺🇸 Honolulu (UTC-10)", "Pacific/Honolulu"),
            ("🇨🇦 Toronto (UTC-5/-4)", "America/Toronto"),
            ("🇨🇦 Vancouver (UTC-8/-7)", "America/Vancouver"),
            ("🇲🇽 Mexico City (UTC-6/-5)", "America/Mexico_City"),
            ("🇧🇷 São Paulo (UTC-3)", "America/Sao_Paulo"),
            ("🇧🇷 Rio de Janeiro (UTC-3)", "America/Sao_Paulo"),
            ("🇦🇷 Buenos Aires (UTC-3)", "America/Argentina/Buenos_Aires"),
            ("🇨🇱 Santiago (UTC-4/-3)", "America/Santiago"),
            ("🇨🇴 Bogota (UTC-5)", "America/Bogota"),
            ("🇵🇪 Lima (UTC-5)", "America/Lima"),
            ("🇻🇪 Caracas (UTC-4)", "America/Caracas"),
            ("🇵🇦 Panama (UTC-5)", "America/Panama"),
            ("🇨🇷 San Jose (UTC-6)", "America/Costa_Rica"),
        ],
        "asia": [
            ("🇯🇵 Tokyo (UTC+9)", "Asia/Tokyo"),
            ("🇰🇷 Seoul (UTC+9)", "Asia/Seoul"),
            ("🇨🇳 Shanghai (UTC+8)", "Asia/Shanghai"),
            ("🇨🇳 Beijing (UTC+8)", "Asia/Shanghai"),
            ("🇭🇰 Hong Kong (UTC+8)", "Asia/Hong_Kong"),
            ("🇸🇬 Singapore (UTC+8)", "Asia/Singapore"),
            ("🇹🇼 Taipei (UTC+8)", "Asia/Taipei"),
            ("🇵🇭 Manila (UTC+8)", "Asia/Manila"),
            ("🇲🇾 Kuala Lumpur (UTC+8)", "Asia/Kuala_Lumpur"),
            ("🇮🇩 Jakarta (UTC+7)", "Asia/Jakarta"),
            ("🇹🇭 Bangkok (UTC+7)", "Asia/Bangkok"),
            ("🇻🇳 Ho Chi Minh (UTC+7)", "Asia/Ho_Chi_Minh"),
            ("🇮🇳 Mumbai (UTC+5:30)", "Asia/Kolkata"),
            ("🇮🇳 Delhi (UTC+5:30)", "Asia/Kolkata"),
            ("🇧🇩 Dhaka (UTC+6)", "Asia/Dhaka"),
            ("🇵🇰 Karachi (UTC+5)", "Asia/Karachi"),
            ("🇰🇿 Almaty (UTC+6)", "Asia/Almaty"),
            ("🇺🇿 Tashkent (UTC+5)", "Asia/Tashkent"),
            ("🇦🇿 Baku (UTC+4)", "Asia/Baku"),
            ("🇬🇪 Tbilisi (UTC+4)", "Asia/Tbilisi"),
            ("🇦🇲 Yerevan (UTC+4)", "Asia/Yerevan"),
            ("🇷🇺 Yekaterinburg (UTC+5)", "Asia/Yekaterinburg"),
            ("🇷🇺 Novosibirsk (UTC+7)", "Asia/Novosibirsk"),
            ("🇷🇺 Krasnoyarsk (UTC+7)", "Asia/Krasnoyarsk"),
            ("🇷🇺 Irkutsk (UTC+8)", "Asia/Irkutsk"),
            ("🇷🇺 Vladivostok (UTC+10)", "Asia/Vladivostok"),
        ],
        "pacific": [
            ("🇦🇺 Sydney (UTC+10/+11)", "Australia/Sydney"),
            ("🇦🇺 Melbourne (UTC+10/+11)", "Australia/Melbourne"),
            ("🇦🇺 Brisbane (UTC+10)", "Australia/Brisbane"),
            ("🇦🇺 Perth (UTC+8)", "Australia/Perth"),
            ("🇦🇺 Adelaide (UTC+9:30/+10:30)", "Australia/Adelaide"),
            ("🇳🇿 Auckland (UTC+12/+13)", "Pacific/Auckland"),
            ("🇳🇿 Wellington (UTC+12/+13)", "Pacific/Auckland"),
            ("🇫🇯 Fiji (UTC+12/+13)", "Pacific/Fiji"),
            ("🇵🇬 Port Moresby (UTC+10)", "Pacific/Port_Moresby"),
            ("🇬🇺 Guam (UTC+10)", "Pacific/Guam"),
        ],
        "africa": [
            ("🇿🇦 Johannesburg (UTC+2)", "Africa/Johannesburg"),
            ("🇪🇬 Cairo (UTC+2)", "Africa/Cairo"),
            ("🇲🇦 Casablanca (UTC+0/+1)", "Africa/Casablanca"),
            ("🇳🇬 Lagos (UTC+1)", "Africa/Lagos"),
            ("🇰🇪 Nairobi (UTC+3)", "Africa/Nairobi"),
            ("🇪🇹 Addis Ababa (UTC+3)", "Africa/Addis_Ababa"),
            ("🇸🇦 Riyadh (UTC+3)", "Asia/Riyadh"),
            ("🇦🇪 Dubai (UTC+4)", "Asia/Dubai"),
            ("🇮🇱 Tel Aviv (UTC+2/+3)", "Asia/Tel_Aviv"),
            ("🇶🇦 Doha (UTC+3)", "Asia/Qatar"),
            ("🇰🇼 Kuwait (UTC+3)", "Asia/Kuwait"),
            ("🇯🇴 Amman (UTC+2/+3)", "Asia/Amman"),
            ("🇱🇧 Beirut (UTC+2/+3)", "Asia/Beirut"),
        ],
    }

    # If no region specified, show region selection
    if not region:
        return get_timezone_regions_keyboard(language_code)

    # Get timezones for the selected region
    timezones = timezone_data.get(region, [])

    rows = []
    for label, tz in timezones:
        rows.append([
            InlineKeyboardButton(text=label, callback_data=f"timezone_{tz}")
        ])

    # Add back button to region selection
    rows.append([InlineKeyboardButton(text="⬅️ " + get_menu_text("back", language_code), callback_data="settings_timezone")])

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


def get_gender_keyboard(language_code: str = "ru", include_neutral: bool = False) -> InlineKeyboardMarkup:
    """Create keyboard for gender selection
    
    Args:
        language_code: User's language
        include_neutral: If True, adds "neutral/unknown" option (for onboarding)
    """
    buttons = [
        [
            InlineKeyboardButton(text=get_menu_text("gender_male", language_code), callback_data="gender_male"),
            InlineKeyboardButton(text=get_menu_text("gender_female", language_code), callback_data="gender_female"),
        ],
    ]
    
    if include_neutral:
        buttons.append([
            InlineKeyboardButton(text=get_menu_text("gender_neutral", language_code), callback_data="gender_neutral"),
        ])
    
    # Add back button only if not in onboarding
    if not include_neutral:
        buttons.append([
            InlineKeyboardButton(text=get_menu_text("back", language_code), callback_data="settings_back"),
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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
