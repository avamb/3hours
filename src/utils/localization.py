"""
MINDSETHAPPYBOT - Localization utilities
Centralized text localization for multi-language support
"""

# Supported languages
SUPPORTED_LANGUAGES = ["ru", "en", "uk"]


def get_language_code(language_code: str) -> str:
    """
    Normalize and validate language code.
    Returns the closest supported language or 'ru' as default.
    """
    if not language_code:
        return "ru"

    # Take first 2 characters and lowercase
    lang = language_code[:2].lower()

    if lang in SUPPORTED_LANGUAGES:
        return lang

    # Default to Russian for unsupported languages
    return "ru"


# Onboarding texts
ONBOARDING_TEXTS = {
    "ru": {
        "address_informal_button": "На «ты» 😊",
        "address_formal_button": "На «вы» 🤝",
        "address_informal_confirm": (
            "Отлично! Буду обращаться на «ты» 😊\n\n"
            "Теперь немного о том, как это работает:\n\n"
            "• Каждые несколько часов я спрошу: «Что хорошего произошло?»\n"
            "• Ты можешь ответить текстом или голосовым сообщением\n"
            "• Я сохраню твои моменты и напомню о них, когда понадобится поддержка\n\n"
            "🔒 Твои данные в безопасности и используются только для нашего общения.\n"
            "Подробнее: /privacy"
        ),
        "address_formal_confirm": (
            "Хорошо! Буду обращаться на «вы» 😊\n\n"
            "Теперь немного о том, как это работает:\n\n"
            "• Каждые несколько часов я спрошу: «Что хорошего произошло?»\n"
            "• Вы можете ответить текстом или голосовым сообщением\n"
            "• Я сохраню Ваши моменты и напомню о них, когда понадобится поддержка\n\n"
            "🔒 Ваши данные в безопасности и используются только для нашего общения.\n"
            "Подробнее: /privacy"
        ),
    },
    "en": {
        "address_informal_button": "Informal 😊",
        "address_formal_button": "Formal 🤝",
        "address_informal_confirm": (
            "Great! I'll use informal communication 😊\n\n"
            "Here's how it works:\n\n"
            "• Every few hours I'll ask: \"What good happened?\"\n"
            "• You can reply with text or voice message\n"
            "• I'll save your moments and remind you of them when you need support\n\n"
            "🔒 Your data is safe and used only for our communication.\n"
            "More info: /privacy"
        ),
        "address_formal_confirm": (
            "Understood! I'll use formal communication 😊\n\n"
            "Here's how it works:\n\n"
            "• Every few hours I'll ask: \"What good happened?\"\n"
            "• You can reply with text or voice message\n"
            "• I'll save your moments and remind you of them when you need support\n\n"
            "🔒 Your data is safe and used only for our communication.\n"
            "More info: /privacy"
        ),
    },
    "uk": {
        "address_informal_button": "На «ти» 😊",
        "address_formal_button": "На «ви» 🤝",
        "address_informal_confirm": (
            "Чудово! Буду звертатися на «ти» 😊\n\n"
            "Ось як це працює:\n\n"
            "• Кожні кілька годин я запитаю: «Що хорошого сталося?»\n"
            "• Ти можеш відповісти текстом або голосовим повідомленням\n"
            "• Я збережу твої моменти і нагадаю про них, коли потрібна підтримка\n\n"
            "🔒 Твої дані в безпеці і використовуються тільки для нашого спілкування.\n"
            "Детальніше: /privacy"
        ),
        "address_formal_confirm": (
            "Добре! Буду звертатися на «ви» 😊\n\n"
            "Ось як це працює:\n\n"
            "• Кожні кілька годин я запитаю: «Що хорошого сталося?»\n"
            "• Ви можете відповісти текстом або голосовим повідомленням\n"
            "• Я збережу Ваші моменти і нагадаю про них, коли потрібна підтримка\n\n"
            "🔒 Ваші дані в безпеці і використовуються тільки для нашого спілкування.\n"
            "Детальніше: /privacy"
        ),
    },
}


def get_onboarding_text(key: str, language_code: str) -> str:
    """
    Get localized onboarding text.

    Args:
        key: Text key (e.g., "address_informal_button", "address_informal_confirm")
        language_code: User's language code

    Returns:
        Localized text or Russian fallback
    """
    lang = get_language_code(language_code)
    texts = ONBOARDING_TEXTS.get(lang, ONBOARDING_TEXTS["ru"])
    return texts.get(key, ONBOARDING_TEXTS["ru"].get(key, ""))


def detect_language_from_text(text: str) -> str:
    """
    Detect language from text based on character analysis.

    This is a simple heuristic-based detection that:
    - Checks for Cyrillic characters (Russian/Ukrainian)
    - Distinguishes Ukrainian from Russian by specific characters
    - Falls back to English for Latin text

    Args:
        text: User's message text

    Returns:
        Detected language code ("ru", "en", "uk") or None if uncertain
    """
    if not text or len(text.strip()) < 3:
        return None

    # Count character types
    cyrillic_count = 0
    latin_count = 0
    ukrainian_specific = 0

    # Ukrainian-specific characters: і, ї, є, ґ (and uppercase)
    ukrainian_chars = set("іїєґІЇЄҐ")

    for char in text:
        if "\u0400" <= char <= "\u04FF":  # Cyrillic range
            cyrillic_count += 1
            if char in ukrainian_chars:
                ukrainian_specific += 1
        elif char.isalpha() and char.isascii():  # Latin letters
            latin_count += 1

    total_letters = cyrillic_count + latin_count

    if total_letters < 3:
        return None

    # If mostly Latin characters -> English
    if latin_count > cyrillic_count:
        return "en"

    # If Cyrillic with Ukrainian-specific characters -> Ukrainian
    if cyrillic_count > 0:
        # If we have Ukrainian-specific characters, it's likely Ukrainian
        if ukrainian_specific > 0:
            return "uk"
        # Otherwise, assume Russian (most common Cyrillic language)
        return "ru"

    return None


async def detect_and_update_language(telegram_id: int, text: str) -> str:
    """
    Detect language from user's text and update their language preference if different.

    Args:
        telegram_id: User's Telegram ID
        text: User's message text

    Returns:
        The detected/current language code
    """
    from src.services.user_service import UserService

    detected_lang = detect_language_from_text(text)

    if not detected_lang:
        # Can't detect, keep current language
        user_service = UserService()
        user = await user_service.get_user_by_telegram_id(telegram_id)
        return user.language_code if user else "ru"

    # Get current user language
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(telegram_id)

    if not user:
        return detected_lang

    current_lang = get_language_code(user.language_code)

    # If detected language differs from stored language, update it
    if detected_lang != current_lang:
        await user_service.update_user_settings(
            telegram_id=telegram_id,
            language_code=detected_lang
        )
        return detected_lang

    return current_lang
