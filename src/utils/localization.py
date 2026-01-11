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


# System/status messages for localization
SYSTEM_MESSAGES = {
    "ru": {
        # Status messages
        "saved": "Сохранено!",
        "error": "Ошибка",
        "success": "Успешно!",
        "cancelled": "Отменено",
        "loading": "Загрузка...",

        # Settings messages
        "active_hours_set": "Активные часы установлены: {start} - {end}",
        "interval_set": "Интервал уведомлений: {interval}",
        "timezone_set": "Часовой пояс установлен: {timezone}",
        "notifications_enabled": "🔔 Уведомления включены",
        "notifications_disabled": "🔕 Уведомления отключены",
        "settings_reset": "Настройки сброшены до значений по умолчанию",
        "language_changed": "Язык изменён на русский",
        "address_changed_informal": "Буду обращаться на «ты»",
        "address_changed_formal": "Буду обращаться на «вы»",
        "gender_set_male": "Пол установлен: мужской",
        "gender_set_female": "Пол установлен: женский",

        # Moments messages
        "no_moments": "У тебя пока нет сохранённых моментов. Расскажи, что хорошего произошло сегодня!",
        "no_moments_formal": "У Вас пока нет сохранённых моментов. Расскажите, что хорошего произошло сегодня!",
        "moment_deleted": "Момент удалён",
        "moments_count": "Найдено моментов: {count}",
        "random_moment_title": "🎲 Случайный радостный момент:",

        # Stats messages
        "stats_title": "📊 Твоя статистика",
        "stats_title_formal": "📊 Ваша статистика",
        "stats_total_moments": "Всего моментов: {count}",
        "stats_current_streak": "Текущая серия: {days} дн.",
        "stats_longest_streak": "Лучшая серия: {days} дн.",
        "stats_response_rate": "Процент ответов: {rate}%",
        "stats_not_available": "Статистика пока недоступна",

        # Dialog messages
        "dialog_started": "💬 Режим диалога. Я слушаю тебя. Напиши «выход» или нажми кнопку, чтобы выйти.",
        "dialog_started_formal": "💬 Режим диалога. Я слушаю Вас. Напишите «выход» или нажмите кнопку, чтобы выйти.",
        "dialog_ended": "Диалог завершён. Возвращаю в главное меню.",

        # Social profile messages
        "social_profile_updated": "Профиль обновлён",
        "social_link_removed": "Ссылка удалена",
        "enter_social_link": "Отправь ссылку на свой профиль в социальной сети:",
        "enter_social_link_formal": "Отправьте ссылку на Ваш профиль в социальной сети:",
        "enter_bio": "Расскажи немного о себе (увлечения, интересы):",
        "enter_bio_formal": "Расскажите немного о себе (увлечения, интересы):",
        "interests_detected": "✨ Определены интересы: {interests}",

        # Feedback messages
        "feedback_prompt": "Напиши своё предложение или идею:",
        "feedback_prompt_formal": "Напишите Ваше предложение или идею:",
        "feedback_sent": "Спасибо за обратную связь! 💝",
        "feedback_category": "Категория: {category}",

        # Help message
        "help_title": "📋 Доступные команды:",
        "help_start": "/start - Начать сначала",
        "help_help": "/help - Показать справку",
        "help_settings": "/settings - Настройки",
        "help_stats": "/stats - Статистика",
        "help_privacy": "/privacy - Политика конфиденциальности",
        "help_export": "/export_data - Экспорт данных",
        "help_delete": "/delete_data - Удаление данных",

        # Privacy policy
        "privacy_title": "🔒 Политика конфиденциальности",
        "privacy_text": (
            "Мы серьёзно относимся к вашей приватности.\n\n"
            "📌 Какие данные мы храним:\n"
            "• Ваши ответы на вопросы бота\n"
            "• Настройки (часовой пояс, язык, интервал)\n"
            "• Базовую информацию из Telegram профиля\n\n"
            "🔐 Как мы используем данные:\n"
            "• Только для персонализации вашего опыта\n"
            "• Для напоминания о хороших моментах\n"
            "• Данные не передаются третьим лицам\n\n"
            "🗑 Ваши права:\n"
            "• /export_data - экспортировать все данные\n"
            "• /delete_data - удалить все данные"
        ),

        # Data export/delete
        "export_confirm": "Экспортировать все твои данные?",
        "export_confirm_formal": "Экспортировать все Ваши данные?",
        "export_success": "Данные экспортированы",
        "delete_confirm": "⚠️ Внимание! Это действие удалит ВСЕ твои данные безвозвратно. Продолжить?",
        "delete_confirm_formal": "⚠️ Внимание! Это действие удалит ВСЕ Ваши данные безвозвратно. Продолжить?",
        "delete_success": "Все данные удалены. До свидания! 👋",

        # Timezone regions
        "timezone_select_region": "Выбери регион:",
        "timezone_select_region_formal": "Выберите регион:",

        # Active hours
        "select_start_hour": "Выбери начало активных часов:",
        "select_start_hour_formal": "Выберите начало активных часов:",
        "select_end_hour": "Выбери конец активных часов:",
        "select_end_hour_formal": "Выберите конец активных часов:",

        # Current settings display
        "current_settings": (
            "⚙️ Текущие настройки:\n\n"
            "🕐 Активные часы: {start_hour}:00 - {end_hour}:00\n"
            "⏰ Интервал: {interval}\n"
            "🌍 Часовой пояс: {timezone}\n"
            "🗣 Обращение: {address}\n"
            "🚻 Пол: {gender}\n"
            "🔔 Уведомления: {notifications}\n"
            "🌐 Язык: {language}"
        ),
    },
    "en": {
        # Status messages
        "saved": "Saved!",
        "error": "Error",
        "success": "Success!",
        "cancelled": "Cancelled",
        "loading": "Loading...",

        # Settings messages
        "active_hours_set": "Active hours set: {start} - {end}",
        "interval_set": "Notification interval: {interval}",
        "timezone_set": "Timezone set: {timezone}",
        "notifications_enabled": "🔔 Notifications enabled",
        "notifications_disabled": "🔕 Notifications disabled",
        "settings_reset": "Settings reset to defaults",
        "language_changed": "Language changed to English",
        "address_changed_informal": "I'll use informal communication",
        "address_changed_formal": "I'll use formal communication",
        "gender_set_male": "Gender set: male",
        "gender_set_female": "Gender set: female",

        # Moments messages
        "no_moments": "You don't have any saved moments yet. Tell me what good happened today!",
        "no_moments_formal": "You don't have any saved moments yet. Please tell me what good happened today!",
        "moment_deleted": "Moment deleted",
        "moments_count": "Found moments: {count}",
        "random_moment_title": "🎲 Random happy moment:",

        # Stats messages
        "stats_title": "📊 Your statistics",
        "stats_title_formal": "📊 Your statistics",
        "stats_total_moments": "Total moments: {count}",
        "stats_current_streak": "Current streak: {days} days",
        "stats_longest_streak": "Best streak: {days} days",
        "stats_response_rate": "Response rate: {rate}%",
        "stats_not_available": "Statistics not available yet",

        # Dialog messages
        "dialog_started": "💬 Dialog mode. I'm listening. Write 'exit' or press the button to exit.",
        "dialog_started_formal": "💬 Dialog mode. I'm listening. Please write 'exit' or press the button to exit.",
        "dialog_ended": "Dialog ended. Returning to main menu.",

        # Social profile messages
        "social_profile_updated": "Profile updated",
        "social_link_removed": "Link removed",
        "enter_social_link": "Send a link to your social media profile:",
        "enter_social_link_formal": "Please send a link to your social media profile:",
        "enter_bio": "Tell me a bit about yourself (hobbies, interests):",
        "enter_bio_formal": "Please tell me a bit about yourself (hobbies, interests):",
        "interests_detected": "✨ Interests detected: {interests}",

        # Feedback messages
        "feedback_prompt": "Write your suggestion or idea:",
        "feedback_prompt_formal": "Please write your suggestion or idea:",
        "feedback_sent": "Thanks for your feedback! 💝",
        "feedback_category": "Category: {category}",

        # Help message
        "help_title": "📋 Available commands:",
        "help_start": "/start - Start over",
        "help_help": "/help - Show help",
        "help_settings": "/settings - Settings",
        "help_stats": "/stats - Statistics",
        "help_privacy": "/privacy - Privacy policy",
        "help_export": "/export_data - Export data",
        "help_delete": "/delete_data - Delete data",

        # Privacy policy
        "privacy_title": "🔒 Privacy Policy",
        "privacy_text": (
            "We take your privacy seriously.\n\n"
            "📌 What data we store:\n"
            "• Your responses to bot questions\n"
            "• Settings (timezone, language, interval)\n"
            "• Basic Telegram profile information\n\n"
            "🔐 How we use data:\n"
            "• Only for personalizing your experience\n"
            "• To remind you of good moments\n"
            "• Data is not shared with third parties\n\n"
            "🗑 Your rights:\n"
            "• /export_data - export all your data\n"
            "• /delete_data - delete all your data"
        ),

        # Data export/delete
        "export_confirm": "Export all your data?",
        "export_confirm_formal": "Export all your data?",
        "export_success": "Data exported",
        "delete_confirm": "⚠️ Warning! This will permanently delete ALL your data. Continue?",
        "delete_confirm_formal": "⚠️ Warning! This will permanently delete ALL your data. Continue?",
        "delete_success": "All data deleted. Goodbye! 👋",

        # Timezone regions
        "timezone_select_region": "Select a region:",
        "timezone_select_region_formal": "Please select a region:",

        # Active hours
        "select_start_hour": "Select start hour:",
        "select_start_hour_formal": "Please select start hour:",
        "select_end_hour": "Select end hour:",
        "select_end_hour_formal": "Please select end hour:",

        # Current settings display
        "current_settings": (
            "⚙️ Current settings:\n\n"
            "🕐 Active hours: {start_hour}:00 - {end_hour}:00\n"
            "⏰ Interval: {interval}\n"
            "🌍 Timezone: {timezone}\n"
            "🗣 Address form: {address}\n"
            "🚻 Gender: {gender}\n"
            "🔔 Notifications: {notifications}\n"
            "🌐 Language: {language}"
        ),
    },
    "uk": {
        # Status messages
        "saved": "Збережено!",
        "error": "Помилка",
        "success": "Успішно!",
        "cancelled": "Скасовано",
        "loading": "Завантаження...",

        # Settings messages
        "active_hours_set": "Активні години встановлено: {start} - {end}",
        "interval_set": "Інтервал сповіщень: {interval}",
        "timezone_set": "Часовий пояс встановлено: {timezone}",
        "notifications_enabled": "🔔 Сповіщення увімкнено",
        "notifications_disabled": "🔕 Сповіщення вимкнено",
        "settings_reset": "Налаштування скинуто до значень за замовчуванням",
        "language_changed": "Мову змінено на українську",
        "address_changed_informal": "Буду звертатися на «ти»",
        "address_changed_formal": "Буду звертатися на «ви»",
        "gender_set_male": "Стать встановлено: чоловіча",
        "gender_set_female": "Стать встановлено: жіноча",

        # Moments messages
        "no_moments": "У тебе поки немає збережених моментів. Розкажи, що хорошого сталося сьогодні!",
        "no_moments_formal": "У Вас поки немає збережених моментів. Розкажіть, що хорошого сталося сьогодні!",
        "moment_deleted": "Момент видалено",
        "moments_count": "Знайдено моментів: {count}",
        "random_moment_title": "🎲 Випадковий радісний момент:",

        # Stats messages
        "stats_title": "📊 Твоя статистика",
        "stats_title_formal": "📊 Ваша статистика",
        "stats_total_moments": "Всього моментів: {count}",
        "stats_current_streak": "Поточна серія: {days} дн.",
        "stats_longest_streak": "Найкраща серія: {days} дн.",
        "stats_response_rate": "Відсоток відповідей: {rate}%",
        "stats_not_available": "Статистика поки недоступна",

        # Dialog messages
        "dialog_started": "💬 Режим діалогу. Я слухаю тебе. Напиши «вихід» або натисни кнопку, щоб вийти.",
        "dialog_started_formal": "💬 Режим діалогу. Я слухаю Вас. Напишіть «вихід» або натисніть кнопку, щоб вийти.",
        "dialog_ended": "Діалог завершено. Повертаю до головного меню.",

        # Social profile messages
        "social_profile_updated": "Профіль оновлено",
        "social_link_removed": "Посилання видалено",
        "enter_social_link": "Надішли посилання на свій профіль у соціальній мережі:",
        "enter_social_link_formal": "Надішліть посилання на Ваш профіль у соціальній мережі:",
        "enter_bio": "Розкажи трохи про себе (захоплення, інтереси):",
        "enter_bio_formal": "Розкажіть трохи про себе (захоплення, інтереси):",
        "interests_detected": "✨ Визначено інтереси: {interests}",

        # Feedback messages
        "feedback_prompt": "Напиши свою пропозицію або ідею:",
        "feedback_prompt_formal": "Напишіть Вашу пропозицію або ідею:",
        "feedback_sent": "Дякуємо за зворотний зв'язок! 💝",
        "feedback_category": "Категорія: {category}",

        # Help message
        "help_title": "📋 Доступні команди:",
        "help_start": "/start - Почати спочатку",
        "help_help": "/help - Показати довідку",
        "help_settings": "/settings - Налаштування",
        "help_stats": "/stats - Статистика",
        "help_privacy": "/privacy - Політика конфіденційності",
        "help_export": "/export_data - Експорт даних",
        "help_delete": "/delete_data - Видалення даних",

        # Privacy policy
        "privacy_title": "🔒 Політика конфіденційності",
        "privacy_text": (
            "Ми серйозно ставимося до вашої приватності.\n\n"
            "📌 Які дані ми зберігаємо:\n"
            "• Ваші відповіді на запитання бота\n"
            "• Налаштування (часовий пояс, мова, інтервал)\n"
            "• Базову інформацію з Telegram профілю\n\n"
            "🔐 Як ми використовуємо дані:\n"
            "• Тільки для персоналізації вашого досвіду\n"
            "• Для нагадування про хороші моменти\n"
            "• Дані не передаються третім особам\n\n"
            "🗑 Ваші права:\n"
            "• /export_data - експортувати всі дані\n"
            "• /delete_data - видалити всі дані"
        ),

        # Data export/delete
        "export_confirm": "Експортувати всі твої дані?",
        "export_confirm_formal": "Експортувати всі Ваші дані?",
        "export_success": "Дані експортовано",
        "delete_confirm": "⚠️ Увага! Це видалить ВСІ твої дані безповоротно. Продовжити?",
        "delete_confirm_formal": "⚠️ Увага! Це видалить ВСІ Ваші дані безповоротно. Продовжити?",
        "delete_success": "Всі дані видалено. До побачення! 👋",

        # Timezone regions
        "timezone_select_region": "Вибери регіон:",
        "timezone_select_region_formal": "Виберіть регіон:",

        # Active hours
        "select_start_hour": "Вибери початок активних годин:",
        "select_start_hour_formal": "Виберіть початок активних годин:",
        "select_end_hour": "Вибери кінець активних годин:",
        "select_end_hour_formal": "Виберіть кінець активних годин:",

        # Current settings display
        "current_settings": (
            "⚙️ Поточні налаштування:\n\n"
            "🕐 Активні години: {start_hour}:00 - {end_hour}:00\n"
            "⏰ Інтервал: {interval}\n"
            "🌍 Часовий пояс: {timezone}\n"
            "🗣 Звертання: {address}\n"
            "🚻 Стать: {gender}\n"
            "🔔 Сповіщення: {notifications}\n"
            "🌐 Мова: {language}"
        ),
    },
}


def get_system_message(key: str, language_code: str, formal: bool = False, **kwargs) -> str:
    """
    Get localized system/status message.

    Args:
        key: Message key (e.g., "saved", "active_hours_set")
        language_code: User's language code
        formal: Whether to use formal version if available
        **kwargs: Format parameters for the message

    Returns:
        Localized and formatted message
    """
    lang = get_language_code(language_code)
    texts = SYSTEM_MESSAGES.get(lang, SYSTEM_MESSAGES["ru"])

    # Try formal version first if requested
    if formal:
        formal_key = f"{key}_formal"
        if formal_key in texts:
            message = texts[formal_key]
        else:
            message = texts.get(key, SYSTEM_MESSAGES["ru"].get(key, key))
    else:
        message = texts.get(key, SYSTEM_MESSAGES["ru"].get(key, key))

    # Format with kwargs if any
    if kwargs:
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError):
            return message

    return message


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
