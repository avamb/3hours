"""
MINDSETHAPPYBOT - Extended Localization for 26 European Languages
Auto-detection from Telegram profile + full UI localization
"""

# =============================================================================
# SUPPORTED LANGUAGES (26 European Languages)
# =============================================================================

SUPPORTED_LANGUAGES = [
    # Core 3 (existing)
    "ru",  # Russian (Русский)
    "en",  # English  
    "uk",  # Ukrainian (Українська)
    
    # Western Europe (6)
    "de",  # German (Deutsch)
    "fr",  # French (Français)
    "es",  # Spanish (Español)
    "it",  # Italian (Italiano)
    "pt",  # Portuguese (Português)
    "nl",  # Dutch (Nederlands)
    
    # Northern Europe (5)
    "sv",  # Swedish (Svenska)
    "da",  # Danish (Dansk)
    "no",  # Norwegian (Norsk)
    "fi",  # Finnish (Suomi)
    "is",  # Icelandic (Íslenska)
    
    # Central Europe (4)
    "pl",  # Polish (Polski)
    "cs",  # Czech (Čeština)
    "sk",  # Slovak (Slovenčina)
    "hu",  # Hungarian (Magyar)
    
    # Southern Europe (3)
    "el",  # Greek (Ελληνικά)
    "hr",  # Croatian (Hrvatski)
    "sl",  # Slovenian (Slovenščina)
    
    # Eastern Europe (4)
    "ro",  # Romanian (Română)
    "bg",  # Bulgarian (Български)
    "lt",  # Lithuanian (Lietuvių)
    "lv",  # Latvian (Latviešu)
    
    # Baltic (1)
    "et",  # Estonian (Eesti)
]

# Language names in their native form
LANGUAGE_NAMES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "uk": "🇺🇦 Українська",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "it": "🇮🇹 Italiano",
    "pt": "🇵🇹 Português",
    "nl": "🇳🇱 Nederlands",
    "sv": "🇸🇪 Svenska",
    "da": "🇩🇰 Dansk",
    "no": "🇳🇴 Norsk",
    "fi": "🇫🇮 Suomi",
    "is": "🇮🇸 Íslenska",
    "pl": "🇵🇱 Polski",
    "cs": "🇨🇿 Čeština",
    "sk": "🇸🇰 Slovenčina",
    "hu": "🇭🇺 Magyar",
    "el": "🇬🇷 Ελληνικά",
    "hr": "🇭🇷 Hrvatski",
    "sl": "🇸🇮 Slovenščina",
    "ro": "🇷🇴 Română",
    "bg": "🇧🇬 Български",
    "lt": "🇱🇹 Lietuvių",
    "lv": "🇱🇻 Latviešu",
    "et": "🇪🇪 Eesti",
}

# Language regions for better targeting
LANGUAGE_REGIONS = {
    "western_europe": ["de", "fr", "nl"],
    "southern_europe": ["es", "it", "pt", "el", "hr", "sl"],
    "northern_europe": ["sv", "da", "no", "fi", "is"],
    "central_europe": ["pl", "cs", "sk", "hu"],
    "eastern_europe": ["ru", "uk", "ro", "bg", "lt", "lv", "et"],
}

# Telegram language_code mapping (more comprehensive)
TELEGRAM_LANG_MAP = {
    # Telegram codes → our codes
    "ru": "ru",
    "en": "en",
    "uk": "uk",
    "de": "de",
    "fr": "fr",
    "es": "es",
    "it": "it",
    "pt": "pt",
    "pt-br": "pt",  # Brazilian Portuguese
    "nl": "nl",
    "sv": "sv",
    "da": "da",
    "no": "no",
    "nb": "no",  # Norwegian Bokmål
    "nn": "no",  # Norwegian Nynorsk
    "fi": "fi",
    "is": "is",
    "pl": "pl",
    "cs": "cs",
    "sk": "sk",
    "hu": "hu",
    "el": "el",
    "hr": "hr",
    "sl": "sl",
    "ro": "ro",
    "bg": "bg",
    "lt": "lt",
    "lv": "lv",
    "et": "et",
    # Common variations
    "be": "ru",  # Belarusian → Russian
    "kk": "ru",  # Kazakh → Russian
    "uz": "ru",  # Uzbek → Russian
    "hy": "en",  # Armenian → English
    "ka": "en",  # Georgian → English
    "sq": "en",  # Albanian → English
    "mk": "en",  # Macedonian → English
    "sr": "en",  # Serbian → English
}


def get_language_code(language_code: str) -> str:
    """
    Normalize and validate language code.
    Returns the closest supported language or 'en' as default.
    
    Args:
        language_code: Raw language code (from Telegram or user)
        
    Returns:
        Normalized language code from SUPPORTED_LANGUAGES
    """
    if not language_code:
        return "en"  # Changed default to English for international audience

    # Take first 2 characters and lowercase
    lang = language_code[:2].lower()

    # Check if directly supported
    if lang in SUPPORTED_LANGUAGES:
        return lang
    
    # Check Telegram mapping
    if lang in TELEGRAM_LANG_MAP:
        return TELEGRAM_LANG_MAP[lang]

    # Default to English for unsupported languages
    return "en"


def detect_language_from_telegram(telegram_user) -> str:
    """
    Detect language from Telegram user profile.
    Uses language_code from Telegram API.
    
    Args:
        telegram_user: Telegram User object with language_code
        
    Returns:
        Detected language code
    """
    if not telegram_user:
        return "en"
    
    # Get language_code from Telegram
    telegram_lang = getattr(telegram_user, 'language_code', None)
    
    if not telegram_lang:
        return "en"
    
    # Map to our supported languages
    return get_language_code(telegram_lang)


def get_language_region(language_code: str) -> str:
    """
    Get region for a language code.
    
    Returns:
        Region name (western_europe, southern_europe, etc.) or "other"
    """
    lang = get_language_code(language_code)
    
    for region, languages in LANGUAGE_REGIONS.items():
        if lang in languages:
            return region
    
    return "other"


def is_rtl_language(language_code: str) -> bool:
    """
    Check if language is right-to-left.
    Currently none of European languages are RTL.
    
    Returns:
        False for all European languages
    """
    return False


# Export all supported language codes for use in other modules
__all__ = [
    'SUPPORTED_LANGUAGES',
    'LANGUAGE_NAMES',
    'LANGUAGE_REGIONS',
    'TELEGRAM_LANG_MAP',
    'get_language_code',
    'detect_language_from_telegram',
    'get_language_region',
    'is_rtl_language',
]
