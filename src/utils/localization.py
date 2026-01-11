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


# Menu button texts for localization
MENU_TEXTS = {
    "ru": {
        "menu_moments": "📖 Мои моменты",
        "menu_stats": "📊 Статистика",
        "menu_settings": "⚙️ Настройки",
        "menu_talk": "💬 Поговорить",
        "menu_feedback": "💡 Предложить идею",
        "settings_hours": "🕐 Активные часы",
        "settings_interval": "⏰ Интервал",
        "settings_timezone": "🌍 Часовой пояс",
        "settings_social": "👤 Социальный профиль",
        "settings_address": "🗣 Форма обращения",
        "settings_notifications": "🔔 Уведомления",
        "settings_reset": "🔄 Сбросить настройки",
        "back": "⬅️ Назад",
        "filter_today": "Сегодня",
        "filter_week": "Неделя",
        "filter_month": "Месяц",
        "random_moment": "🎲 Случайный момент",
        "another_random": "🎲 Ещё случайный",
        "delete_moment": "🗑️ Удалить",
        "all_moments": "📖 Все моменты",
        "exit_dialog": "🚪 Выйти из диалога",
        "confirm_delete": "❌ Да, удалить всё",
        "cancel_delete": "✅ Нет, отменить",
        "confirm_delete_moment": "✅ Да, удалить",
        "cancel": "❌ Отмена",
        "skip_question": "⏭ Пропустить",
        "social_add": "➕ Добавить соцсеть",
        "social_bio": "📝 Редактировать био",
        "social_parse": "🔍 Определить интересы",
        "social_remove": "🗑 Удалить ссылку",
        "no_social_links": "Нет добавленных соцсетей",
        "feedback_suggestion": "💡 Идея/предложение",
        "feedback_bug": "🐛 Сообщить об ошибке",
        "feedback_other": "💬 Другое",
        "feedback_cancel": "⬅️ Отмена",
        "feedback_submit": "✅ Отправить",
        "feedback_new": "💡 Предложить ещё",
        "feedback_menu": "⬅️ В меню",
        "summary_weekly": "📅 Еженедельное",
        "summary_monthly": "🗓 Месячное",
        "interval_1h": "1 час",
        "interval_2h": "2 часа",
        "interval_3h": "3 часа",
        "interval_4h": "4 часа",
        "interval_6h": "6 часов",
        "interval_8h": "8 часов",
        "address_informal": "На «ты» 😊",
        "address_formal": "На «вы» 🤝",
        "gender_male": "👨 Он",
        "gender_female": "👩 Она",
        "settings_gender": "🚻 Пол",
        "settings_language": "🌐 Язык интерфейса",
        "language_ru": "🇷🇺 Русский",
        "language_en": "🇬🇧 English",
        "language_uk": "🇺🇦 Українська",
        "language_es": "🇪🇸 Español",
        "language_de": "🇩🇪 Deutsch",
        "language_fr": "🇫🇷 Français",
        "language_pt": "🇧🇷 Português",
        "language_it": "🇮🇹 Italiano",
        "language_zh": "🇨🇳 中文",
        "language_ja": "🇯🇵 日本語",
        "social_link_saved": "✅ Ссылка сохранена",
        "social_parse_failed": "К сожалению, нам не удалось получить данные вашего профиля. Ссылка сохранена, но не будет использоваться для персонализации.",
    },
    "en": {
        "menu_moments": "📖 My moments",
        "menu_stats": "📊 Statistics",
        "menu_settings": "⚙️ Settings",
        "menu_talk": "💬 Talk",
        "menu_feedback": "💡 Suggest idea",
        "settings_hours": "🕐 Active hours",
        "settings_interval": "⏰ Interval",
        "settings_timezone": "🌍 Timezone",
        "settings_social": "👤 Social profile",
        "settings_address": "🗣 Address form",
        "settings_notifications": "🔔 Notifications",
        "settings_reset": "🔄 Reset settings",
        "back": "⬅️ Back",
        "filter_today": "Today",
        "filter_week": "Week",
        "filter_month": "Month",
        "random_moment": "🎲 Random moment",
        "another_random": "🎲 Another random",
        "delete_moment": "🗑️ Delete",
        "all_moments": "📖 All moments",
        "exit_dialog": "🚪 Exit dialog",
        "confirm_delete": "❌ Yes, delete all",
        "cancel_delete": "✅ No, cancel",
        "confirm_delete_moment": "✅ Yes, delete",
        "cancel": "❌ Cancel",
        "skip_question": "⏭ Skip",
        "social_add": "➕ Add social",
        "social_bio": "📝 Edit bio",
        "social_parse": "🔍 Detect interests",
        "social_remove": "🗑 Remove link",
        "no_social_links": "No social links added",
        "feedback_suggestion": "💡 Idea/suggestion",
        "feedback_bug": "🐛 Report bug",
        "feedback_other": "💬 Other",
        "feedback_cancel": "⬅️ Cancel",
        "feedback_submit": "✅ Submit",
        "feedback_new": "💡 Suggest more",
        "feedback_menu": "⬅️ To menu",
        "summary_weekly": "📅 Weekly",
        "summary_monthly": "🗓 Monthly",
        "interval_1h": "1 hour",
        "interval_2h": "2 hours",
        "interval_3h": "3 hours",
        "interval_4h": "4 hours",
        "interval_6h": "6 hours",
        "interval_8h": "8 hours",
        "address_informal": "Informal 😊",
        "address_formal": "Formal 🤝",
        "gender_male": "👨 He",
        "gender_female": "👩 She",
        "settings_gender": "🚻 Gender",
        "settings_language": "🌐 Interface language",
        "language_ru": "🇷🇺 Русский",
        "language_en": "🇬🇧 English",
        "language_uk": "🇺🇦 Українська",
        "language_es": "🇪🇸 Español",
        "language_de": "🇩🇪 Deutsch",
        "language_fr": "🇫🇷 Français",
        "language_pt": "🇧🇷 Português",
        "language_it": "🇮🇹 Italiano",
        "language_zh": "🇨🇳 中文",
        "language_ja": "🇯🇵 日本語",
        "social_link_saved": "✅ Link saved",
        "social_parse_failed": "Unfortunately, we couldn't get your profile data. The link has been saved, but won't be used for personalization.",
    },
    "uk": {
        "menu_moments": "📖 Мої моменти",
        "menu_stats": "📊 Статистика",
        "menu_settings": "⚙️ Налаштування",
        "menu_talk": "💬 Поговорити",
        "menu_feedback": "💡 Запропонувати ідею",
        "settings_hours": "🕐 Активні години",
        "settings_interval": "⏰ Інтервал",
        "settings_timezone": "🌍 Часовий пояс",
        "settings_social": "👤 Соціальний профіль",
        "settings_address": "🗣 Форма звертання",
        "settings_notifications": "🔔 Сповіщення",
        "settings_reset": "🔄 Скинути налаштування",
        "back": "⬅️ Назад",
        "filter_today": "Сьогодні",
        "filter_week": "Тиждень",
        "filter_month": "Місяць",
        "random_moment": "🎲 Випадковий момент",
        "another_random": "🎲 Ще випадковий",
        "delete_moment": "🗑️ Видалити",
        "all_moments": "📖 Усі моменти",
        "exit_dialog": "🚪 Вийти з діалогу",
        "confirm_delete": "❌ Так, видалити все",
        "cancel_delete": "✅ Ні, скасувати",
        "confirm_delete_moment": "✅ Так, видалити",
        "cancel": "❌ Скасувати",
        "skip_question": "⏭ Пропустити",
        "social_add": "➕ Додати соцмережу",
        "social_bio": "📝 Редагувати біо",
        "social_parse": "🔍 Визначити інтереси",
        "social_remove": "🗑 Видалити посилання",
        "no_social_links": "Немає доданих соцмереж",
        "feedback_suggestion": "💡 Ідея/пропозиція",
        "feedback_bug": "🐛 Повідомити про помилку",
        "feedback_other": "💬 Інше",
        "feedback_cancel": "⬅️ Скасувати",
        "feedback_submit": "✅ Надіслати",
        "feedback_new": "💡 Запропонувати ще",
        "feedback_menu": "⬅️ До меню",
        "summary_weekly": "📅 Щотижневе",
        "summary_monthly": "🗓 Щомісячне",
        "interval_1h": "1 година",
        "interval_2h": "2 години",
        "interval_3h": "3 години",
        "interval_4h": "4 години",
        "interval_6h": "6 годин",
        "interval_8h": "8 годин",
        "address_informal": "На «ти» 😊",
        "address_formal": "На «ви» 🤝",
        "gender_male": "👨 Він",
        "gender_female": "👩 Вона",
        "settings_gender": "🚻 Стать",
        "settings_language": "🌐 Мова інтерфейсу",
        "language_ru": "🇷🇺 Русский",
        "language_en": "🇬🇧 English",
        "language_uk": "🇺🇦 Українська",
        "language_es": "🇪🇸 Español",
        "language_de": "🇩🇪 Deutsch",
        "language_fr": "🇫🇷 Français",
        "language_pt": "🇧🇷 Português",
        "language_it": "🇮🇹 Italiano",
        "language_zh": "🇨🇳 中文",
        "language_ja": "🇯🇵 日本語",
        "social_link_saved": "✅ Посилання збережено",
        "social_parse_failed": "На жаль, нам не вдалося отримати дані вашого профілю. Посилання збережено, але не буде використовуватися для персоналізації.",
    },
}


def get_menu_text(key: str, language_code: str) -> str:
    lang = get_language_code(language_code)
    texts = MENU_TEXTS.get(lang, MENU_TEXTS["ru"])
    return texts.get(key, MENU_TEXTS["ru"].get(key, key))


def get_all_menu_button_texts(key: str) -> list:
    texts = []
    for lang in SUPPORTED_LANGUAGES:
        if key in MENU_TEXTS.get(lang, {}):
            texts.append(MENU_TEXTS[lang][key])
    return texts


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
