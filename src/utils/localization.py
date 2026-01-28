"""
MINDSETHAPPYBOT - Localization utilities
Centralized text localization for multi-language support
"""

# Supported languages
SUPPORTED_LANGUAGES = ['ru', 'en', 'uk', 'es', 'de', 'fr', 'pt', 'it', 'zh', 'ja', 'he']


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
        "menu_pause": "⏸ Остановить",
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
        "gender_neutral": "⚪ Нейтрально",
        "settings_gender": "🚻 Пол",
        "yes_start": "✅ Да, начать",
        "no_settings": "⚙️ Сначала настройки",
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
        "menu_pause": "⏸ Pause",
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
        "gender_neutral": "⚪ Neutral",
        "settings_gender": "🚻 Gender",
        "yes_start": "✅ Yes, start",
        "no_settings": "⚙️ Settings first",
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
        "menu_pause": "⏸ Зупинити",
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
        "gender_neutral": "⚪ Нейтрально",
        "settings_gender": "🚻 Стать",
        "yes_start": "✅ Так, почати",
        "no_settings": "⚙️ Спочатку налаштування",
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

    "he": {
        "menu_moments": "📖 הרגעים שלי",
        "menu_stats": "📊 סטטיסטיקה",
        "menu_settings": "⚙️ הגדרות",
        "menu_talk": "💬 לדבר",
        "menu_feedback": "💡 הצעת רעיון",
        "menu_pause": "⏸ השהיה",
        "settings_hours": "🕐 שעות פעילות",
        "settings_interval": "⏰ אינטרוול",
        "settings_timezone": "🌍 אזור זמן",
        "settings_social": "👤 פרופיל חברתי",
        "settings_address": "🗣 צורת פנייה",
        "settings_notifications": "🔔 התראות",
        "settings_reset": "🔄 אפס הגדרות",
        "back": "⬅️ חזרה",
        "filter_today": "היום",
        "filter_week": "שבוע",
        "filter_month": "חודש",
        "random_moment": "🎲 רגע אקראי",
        "another_random": "🎲 עוד רגע אקראי",
        "delete_moment": "🗑️ מחק",
        "all_moments": "📖 כל הרגעים",
        "exit_dialog": "🚪 לצאת מהשיחה",
        "confirm_delete": "❌ כן, למחוק הכל",
        "cancel_delete": "✅ לא, לבטל",
        "confirm_delete_moment": "✅ כן, למחוק",
        "cancel": "❌ ביטול",
        "skip_question": "⏭ לדלג",
        "social_add": "➕ להוסיף רשת חברתית",
        "social_bio": "📝 לערוך ביוגרפיה",
        "social_parse": "🔍 לקבוע תחומי עניין",
        "social_remove": "🗑 למחוק קישור",
        "no_social_links": "אין רשתות חברתיות נוספות",
        "feedback_suggestion": "💡 רעיון/הצעה",
        "feedback_bug": "🐛 לדווח על בעיה",
        "feedback_other": "💬 אחר",
        "feedback_cancel": "⬅️ ביטול",
        "feedback_submit": "✅ שלח",
        "feedback_new": "💡 להציע עוד",
        "feedback_menu": "⬅️ לתפריט",
        "summary_weekly": "📅 שבועי",
        "summary_monthly": "🗓 חודשי",
        "interval_1h": "שעה אחת",
        "interval_2h": "שעתיים",
        "interval_3h": "שלוש שעות",
        "interval_4h": "ארבע שעות",
        "interval_6h": "שש שעות",
        "interval_8h": "שמונה שעות",
        "address_informal": "ב'אתה' 😊",
        "address_formal": "ב'אתם' 🤝",
        "gender_male": "👨 הוא",
        "gender_female": "👩 היא",
        "gender_neutral": "⚪ נייטרלי",
        "settings_gender": "🚻 מין",
        "settings_language": "🌐 שפת ממשק",
        "language_ru": "🇷🇺 רוסית",
        "language_en": "🇬🇧 אנגלית",
        "language_uk": "🇺🇦 אוקראינית",
        "language_es": "🇪🇸 ספרדית",
        "language_de": "🇩🇪 גרמנית",
        "language_fr": "🇫🇷 צרפתית",
        "language_pt": "🇧🇷 פורטוגזית",
        "language_it": "🇮🇹 איטלקית",
        "language_zh": "🇨🇳 סינית",
        "language_ja": "🇯🇵 יפנית",
        "social_link_saved": "✅ הקישור נשמר",
        "social_parse_failed": "לצערנו, לא הצלחנו לקבל את הנתונים של הפרופיל שלך. הקישור נשמר, אך לא ישמש להתאמה אישית.",
    },
    "ja": {
        "menu_moments": "📖 私の瞬間",
        "menu_stats": "📊 統計",
        "menu_settings": "⚙️ 設定",
        "menu_talk": "💬 話す",
        "menu_feedback": "💡 アイデアを提案する",
        "menu_pause": "⏸ 一時停止",
        "settings_hours": "🕐 アクティブ時間",
        "settings_interval": "⏰ インターバル",
        "settings_timezone": "🌍 タイムゾーン",
        "settings_social": "👤 ソーシャルプロフィール",
        "settings_address": "🗣 呼び方",
        "settings_notifications": "🔔 通知",
        "settings_reset": "🔄 設定をリセット",
        "back": "⬅️ 戻る",
        "filter_today": "今日",
        "filter_week": "今週",
        "filter_month": "今月",
        "random_moment": "🎲 ランダムな瞬間",
        "another_random": "🎲 もう一つランダム",
        "delete_moment": "🗑️ 削除",
        "all_moments": "📖 すべての瞬間",
        "exit_dialog": "🚪 ダイアログを終了",
        "confirm_delete": "❌ はい、すべて削除",
        "cancel_delete": "✅ いいえ、キャンセル",
        "confirm_delete_moment": "✅ はい、削除",
        "cancel": "❌ キャンセル",
        "skip_question": "⏭ スキップ",
        "social_add": "➕ ソーシャルネットワークを追加",
        "social_bio": "📝 バイオを編集",
        "social_parse": "🔍 興味を特定",
        "social_remove": "🗑 リンクを削除",
        "no_social_links": "追加されたソーシャルネットワークはありません",
        "feedback_suggestion": "💡 アイデア/提案",
        "feedback_bug": "🐛 バグを報告",
        "feedback_other": "💬 その他",
        "feedback_cancel": "⬅️ キャンセル",
        "feedback_submit": "✅ 送信",
        "feedback_new": "💡 さらに提案する",
        "feedback_menu": "⬅️ メニューへ",
        "summary_weekly": "📅 週間",
        "summary_monthly": "🗓 月間",
        "interval_1h": "1時間",
        "interval_2h": "2時間",
        "interval_3h": "3時間",
        "interval_4h": "4時間",
        "interval_6h": "6時間",
        "interval_8h": "8時間",
        "address_informal": "「君」で 😊",
        "address_formal": "「あなた」で 🤝",
        "gender_male": "👨 彼",
        "gender_female": "👩 彼女",
        "gender_neutral": "⚪ ニュートラル",
        "settings_gender": "🚻 性別",
        "settings_language": "🌐 インターフェースの言語",
        "language_ru": "🇷🇺 ロシア語",
        "language_en": "🇬🇧 英語",
        "language_uk": "🇺🇦 ウクライナ語",
        "language_es": "🇪🇸 スペイン語",
        "language_de": "🇩🇪 ドイツ語",
        "language_fr": "🇫🇷 フランス語",
        "language_pt": "🇧🇷 ポルトガル語",
        "language_it": "🇮🇹 イタリア語",
        "language_zh": "🇨🇳 中国語",
        "language_ja": "🇯🇵 日本語",
        "social_link_saved": "✅ リンクが保存されました",
        "social_parse_failed": "申し訳ありませんが、プロフィールデータを取得できませんでした。リンクは保存されましたが、パーソナライズには使用されません。",
    },
    "zh": {
        "menu_moments": "📖 我的时刻",
        "menu_stats": "📊 统计",
        "menu_settings": "⚙️ 设置",
        "menu_talk": "💬 聊天",
        "menu_feedback": "💡 提出想法",
        "menu_pause": "⏸ 暂停",
        "settings_hours": "🕐 活动时间",
        "settings_interval": "⏰ 间隔",
        "settings_timezone": "🌍 时区",
        "settings_social": "👤 社交资料",
        "settings_address": "🗣 称呼方式",
        "settings_notifications": "🔔 通知",
        "settings_reset": "🔄 重置设置",
        "back": "⬅️ 返回",
        "filter_today": "今天",
        "filter_week": "一周",
        "filter_month": "一个月",
        "random_moment": "🎲 随机时刻",
        "another_random": "🎲 另一个随机",
        "delete_moment": "🗑️ 删除",
        "all_moments": "📖 所有时刻",
        "exit_dialog": "🚪 退出对话",
        "confirm_delete": "❌ 是的，删除所有",
        "cancel_delete": "✅ 不，取消",
        "confirm_delete_moment": "✅ 是的，删除",
        "cancel": "❌ 取消",
        "skip_question": "⏭ 跳过",
        "social_add": "➕ 添加社交网络",
        "social_bio": "📝 编辑个人简介",
        "social_parse": "🔍 确定兴趣",
        "social_remove": "🗑 删除链接",
        "no_social_links": "没有添加的社交网络",
        "feedback_suggestion": "💡 想法/建议",
        "feedback_bug": "🐛 报告错误",
        "feedback_other": "💬 其他",
        "feedback_cancel": "⬅️ 取消",
        "feedback_submit": "✅ 提交",
        "feedback_new": "💡 再提一个",
        "feedback_menu": "⬅️ 返回菜单",
        "summary_weekly": "📅 每周总结",
        "summary_monthly": "🗓 每月总结",
        "interval_1h": "1小时",
        "interval_2h": "2小时",
        "interval_3h": "3小时",
        "interval_4h": "4小时",
        "interval_6h": "6小时",
        "interval_8h": "8小时",
        "address_informal": "用“你” 😊",
        "address_formal": "用“您” 🤝",
        "gender_male": "👨 他",
        "gender_female": "👩 她",
        "gender_neutral": "⚪ 中性",
        "settings_gender": "🚻 性别",
        "settings_language": "🌐 界面语言",
        "language_ru": "🇷🇺 俄语",
        "language_en": "🇬🇧 英语",
        "language_uk": "🇺🇦 乌克兰语",
        "language_es": "🇪🇸 西班牙语",
        "language_de": "🇩🇪 德语",
        "language_fr": "🇫🇷 法语",
        "language_pt": "🇧🇷 葡萄牙语",
        "language_it": "🇮🇹 意大利语",
        "language_zh": "🇨🇳 中文",
        "language_ja": "🇯🇵 日语",
        "social_link_saved": "✅ 链接已保存",
        "social_parse_failed": "很抱歉，我们无法获取您的资料数据。链接已保存，但不会用于个性化。",
    },
    "it": {
        "menu_moments": "📖 I miei momenti",
        "menu_stats": "📊 Statistiche",
        "menu_settings": "⚙️ Impostazioni",
        "menu_talk": "💬 Parlare",
        "menu_feedback": "💡 Suggerire un'idea",
        "menu_pause": "⏸ Pausa",
        "settings_hours": "🕐 Ore attive",
        "settings_interval": "⏰ Intervallo",
        "settings_timezone": "🌍 Fuso orario",
        "settings_social": "👤 Profilo sociale",
        "settings_address": "🗣 Forma di saluto",
        "settings_notifications": "🔔 Notifiche",
        "settings_reset": "🔄 Ripristina impostazioni",
        "back": "⬅️ Indietro",
        "filter_today": "Oggi",
        "filter_week": "Settimana",
        "filter_month": "Mese",
        "random_moment": "🎲 Momento casuale",
        "another_random": "🎲 Altro casuale",
        "delete_moment": "🗑️ Elimina",
        "all_moments": "📖 Tutti i momenti",
        "exit_dialog": "🚪 Esci dalla conversazione",
        "confirm_delete": "❌ Sì, elimina tutto",
        "cancel_delete": "✅ No, annulla",
        "confirm_delete_moment": "✅ Sì, elimina",
        "cancel": "❌ Annulla",
        "skip_question": "⏭ Salta",
        "social_add": "➕ Aggiungi social",
        "social_bio": "📝 Modifica bio",
        "social_parse": "🔍 Determina interessi",
        "social_remove": "🗑 Elimina link",
        "no_social_links": "Nessun social aggiunto",
        "feedback_suggestion": "💡 Idea/suggerimento",
        "feedback_bug": "🐛 Segnala un errore",
        "feedback_other": "💬 Altro",
        "feedback_cancel": "⬅️ Annulla",
        "feedback_submit": "✅ Invia",
        "feedback_new": "💡 Suggerisci ancora",
        "feedback_menu": "⬅️ Torna al menu",
        "summary_weekly": "📅 Settimanale",
        "summary_monthly": "🗓 Mensile",
        "interval_1h": "1 ora",
        "interval_2h": "2 ore",
        "interval_3h": "3 ore",
        "interval_4h": "4 ore",
        "interval_6h": "6 ore",
        "interval_8h": "8 ore",
        "address_informal": "Al «tu» 😊",
        "address_formal": "Al «Lei» 🤝",
        "gender_male": "👨 Lui",
        "gender_female": "👩 Lei",
        "gender_neutral": "⚪ Neutro",
        "settings_gender": "🚻 Genere",
        "settings_language": "🌐 Lingua dell'interfaccia",
        "language_ru": "🇷🇺 Russo",
        "language_en": "🇬🇧 Inglese",
        "language_uk": "🇺🇦 Ucraino",
        "language_es": "🇪🇸 Spagnolo",
        "language_de": "🇩🇪 Tedesco",
        "language_fr": "🇫🇷 Francese",
        "language_pt": "🇧🇷 Portoghese",
        "language_it": "🇮🇹 Italiano",
        "language_zh": "🇨🇳 中文",
        "language_ja": "🇯🇵 日本語",
        "social_link_saved": "✅ Link salvato",
        "social_parse_failed": "Sfortunatamente, non siamo riusciti a ottenere i dati del tuo profilo. Il link è stato salvato, ma non sarà utilizzato per la personalizzazione.",
    },
    "pt": {
        "menu_moments": "📖 Meus momentos",
        "menu_stats": "📊 Estatísticas",
        "menu_settings": "⚙️ Configurações",
        "menu_talk": "💬 Conversar",
        "menu_feedback": "💡 Sugerir ideia",
        "menu_pause": "⏸ Pausar",
        "settings_hours": "🕐 Horas ativas",
        "settings_interval": "⏰ Intervalo",
        "settings_timezone": "🌍 Fuso horário",
        "settings_social": "👤 Perfil social",
        "settings_address": "🗣 Forma de tratamento",
        "settings_notifications": "🔔 Notificações",
        "settings_reset": "🔄 Redefinir configurações",
        "back": "⬅️ Voltar",
        "filter_today": "Hoje",
        "filter_week": "Semana",
        "filter_month": "Mês",
        "random_moment": "🎲 Momento aleatório",
        "another_random": "🎲 Outro aleatório",
        "delete_moment": "🗑️ Deletar",
        "all_moments": "📖 Todos os momentos",
        "exit_dialog": "🚪 Sair do diálogo",
        "confirm_delete": "❌ Sim, deletar tudo",
        "cancel_delete": "✅ Não, cancelar",
        "confirm_delete_moment": "✅ Sim, deletar",
        "cancel": "❌ Cancelar",
        "skip_question": "⏭ Pular",
        "social_add": "➕ Adicionar rede social",
        "social_bio": "📝 Editar bio",
        "social_parse": "🔍 Identificar interesses",
        "social_remove": "🗑 Remover link",
        "no_social_links": "Nenhuma rede social adicionada",
        "feedback_suggestion": "💡 Ideia/sugestão",
        "feedback_bug": "🐛 Reportar erro",
        "feedback_other": "💬 Outro",
        "feedback_cancel": "⬅️ Cancelar",
        "feedback_submit": "✅ Enviar",
        "feedback_new": "💡 Sugerir mais",
        "feedback_menu": "⬅️ No menu",
        "summary_weekly": "📅 Semanal",
        "summary_monthly": "🗓 Mensal",
        "interval_1h": "1 hora",
        "interval_2h": "2 horas",
        "interval_3h": "3 horas",
        "interval_4h": "4 horas",
        "interval_6h": "6 horas",
        "interval_8h": "8 horas",
        "address_informal": "No ‘tu’ 😊",
        "address_formal": "No ‘você’ 🤝",
        "gender_male": "👨 Ele",
        "gender_female": "👩 Ela",
        "gender_neutral": "⚪ Neutro",
        "settings_gender": "🚻 Gênero",
        "settings_language": "🌐 Idioma da interface",
        "language_ru": "🇷🇺 Russo",
        "language_en": "🇬🇧 Inglês",
        "language_uk": "🇺🇦 Ucraniano",
        "language_es": "🇪🇸 Espanhol",
        "language_de": "🇩🇪 Alemão",
        "language_fr": "🇫🇷 Francês",
        "language_pt": "🇧🇷 Português",
        "language_it": "🇮🇹 Italiano",
        "language_zh": "🇨🇳 中文",
        "language_ja": "🇯🇵 日本語",
        "social_link_saved": "✅ Link salvo",
        "social_parse_failed": "Infelizmente, não conseguimos obter os dados do seu perfil. O link foi salvo, mas não será utilizado para personalização.",
    },
    "fr": {
        "menu_moments": "📖 Mes moments",
        "menu_stats": "📊 Statistiques",
        "menu_settings": "⚙️ Paramètres",
        "menu_talk": "💬 Parler",
        "menu_feedback": "💡 Proposer une idée",
        "menu_pause": "⏸ Pause",
        "settings_hours": "🕐 Heures actives",
        "settings_interval": "⏰ Intervalle",
        "settings_timezone": "🌍 Fuseau horaire",
        "settings_social": "👤 Profil social",
        "settings_address": "🗣 Forme d'adresse",
        "settings_notifications": "🔔 Notifications",
        "settings_reset": "🔄 Réinitialiser les paramètres",
        "back": "⬅️ Retour",
        "filter_today": "Aujourd'hui",
        "filter_week": "Semaine",
        "filter_month": "Mois",
        "random_moment": "🎲 Moment aléatoire",
        "another_random": "🎲 Encore un aléatoire",
        "delete_moment": "🗑️ Supprimer",
        "all_moments": "📖 Tous les moments",
        "exit_dialog": "🚪 Quitter le dialogue",
        "confirm_delete": "❌ Oui, tout supprimer",
        "cancel_delete": "✅ Non, annuler",
        "confirm_delete_moment": "✅ Oui, supprimer",
        "cancel": "❌ Annuler",
        "skip_question": "⏭ Passer",
        "social_add": "➕ Ajouter un réseau social",
        "social_bio": "📝 Éditer la bio",
        "social_parse": "🔍 Déterminer les intérêts",
        "social_remove": "🗑 Supprimer le lien",
        "no_social_links": "Aucun réseau social ajouté",
        "feedback_suggestion": "💡 Idée/proposition",
        "feedback_bug": "🐛 Signaler un bug",
        "feedback_other": "💬 Autre",
        "feedback_cancel": "⬅️ Annuler",
        "feedback_submit": "✅ Soumettre",
        "feedback_new": "💡 Proposer encore",
        "feedback_menu": "⬅️ Dans le menu",
        "summary_weekly": "📅 Hebdomadaire",
        "summary_monthly": "🗓 Mensuel",
        "interval_1h": "1 heure",
        "interval_2h": "2 heures",
        "interval_3h": "3 heures",
        "interval_4h": "4 heures",
        "interval_6h": "6 heures",
        "interval_8h": "8 heures",
        "address_informal": "Sur «tu» 😊",
        "address_formal": "Sur «vous» 🤝",
        "gender_male": "👨 Il",
        "gender_female": "👩 Elle",
        "gender_neutral": "⚪ Neutre",
        "settings_gender": "🚻 Genre",
        "settings_language": "🌐 Langue de l'interface",
        "language_ru": "🇷🇺 Russe",
        "language_en": "🇬🇧 Anglais",
        "language_uk": "🇺🇦 Ukrainien",
        "language_es": "🇪🇸 Espagnol",
        "language_de": "🇩🇪 Allemand",
        "language_fr": "🇫🇷 Français",
        "language_pt": "🇧🇷 Portugais",
        "language_it": "🇮🇹 Italien",
        "language_zh": "🇨🇳 中文",
        "language_ja": "🇯🇵 日本語",
        "social_link_saved": "✅ Lien enregistré",
        "social_parse_failed": "Malheureusement, nous n'avons pas pu obtenir les données de votre profil. Le lien est enregistré, mais ne sera pas utilisé pour la personnalisation.",
    },
    "de": {
        "menu_moments": "📖 Meine Momente",
        "menu_stats": "📊 Statistiken",
        "menu_settings": "⚙️ Einstellungen",
        "menu_talk": "💬 Reden",
        "menu_feedback": "💡 Idee vorschlagen",
        "menu_pause": "⏸ Pause",
        "settings_hours": "🕐 Aktive Stunden",
        "settings_interval": "⏰ Intervall",
        "settings_timezone": "🌍 Zeitzone",
        "settings_social": "👤 Soziales Profil",
        "settings_address": "🗣 Anrede",
        "settings_notifications": "🔔 Benachrichtigungen",
        "settings_reset": "🔄 Einstellungen zurücksetzen",
        "back": "⬅️ Zurück",
        "filter_today": "Heute",
        "filter_week": "Woche",
        "filter_month": "Monat",
        "random_moment": "🎲 Zufälliger Moment",
        "another_random": "🎲 Noch ein Zufälliger",
        "delete_moment": "🗑️ Löschen",
        "all_moments": "📖 Alle Momente",
        "exit_dialog": "🚪 Aus dem Dialog austreten",
        "confirm_delete": "❌ Ja, alles löschen",
        "cancel_delete": "✅ Nein, abbrechen",
        "confirm_delete_moment": "✅ Ja, löschen",
        "cancel": "❌ Abbrechen",
        "skip_question": "⏭ Überspringen",
        "social_add": "➕ Soziale Netzwerke hinzufügen",
        "social_bio": "📝 Bio bearbeiten",
        "social_parse": "🔍 Interessen bestimmen",
        "social_remove": "🗑 Link entfernen",
        "no_social_links": "Keine hinzugefügten sozialen Netzwerke",
        "feedback_suggestion": "💡 Idee/Vorschlag",
        "feedback_bug": "🐛 Fehler melden",
        "feedback_other": "💬 Sonstiges",
        "feedback_cancel": "⬅️ Abbrechen",
        "feedback_submit": "✅ Einreichen",
        "feedback_new": "💡 Noch eine Idee vorschlagen",
        "feedback_menu": "⬅️ Zum Menü",
        "summary_weekly": "📅 Wöchentlich",
        "summary_monthly": "🗓 Monatlich",
        "interval_1h": "1 Stunde",
        "interval_2h": "2 Stunden",
        "interval_3h": "3 Stunden",
        "interval_4h": "4 Stunden",
        "interval_6h": "6 Stunden",
        "interval_8h": "8 Stunden",
        "address_informal": "Auf „du“ 😊",
        "address_formal": "Auf „Sie“ 🤝",
        "gender_male": "👨 Er",
        "gender_female": "👩 Sie",
        "gender_neutral": "⚪ Neutral",
        "settings_gender": "🚻 Geschlecht",
        "settings_language": "🌐 Sprache der Benutzeroberfläche",
        "language_ru": "🇷🇺 Russisch",
        "language_en": "🇬🇧 Englisch",
        "language_uk": "🇺🇦 Ukrainisch",
        "language_es": "🇪🇸 Spanisch",
        "language_de": "🇩🇪 Deutsch",
        "language_fr": "🇫🇷 Französisch",
        "language_pt": "🇧🇷 Portugiesisch",
        "language_it": "🇮🇹 Italienisch",
        "language_zh": "🇨🇳 中文",
        "language_ja": "🇯🇵 日本語",
        "social_link_saved": "✅ Link gespeichert",
        "social_parse_failed": "Leider konnten wir die Daten Ihres Profils nicht abrufen. Der Link wurde gespeichert, wird jedoch nicht zur Personalisierung verwendet.",
    },
    "es": {
        "menu_moments": "📖 Mis momentos",
        "menu_stats": "📊 Estadísticas",
        "menu_settings": "⚙️ Configuración",
        "menu_talk": "💬 Hablar",
        "menu_feedback": "💡 Sugerir una idea",
        "menu_pause": "⏸ Pausar",
        "settings_hours": "🕐 Horas activas",
        "settings_interval": "⏰ Intervalo",
        "settings_timezone": "🌍 Zona horaria",
        "settings_social": "👤 Perfil social",
        "settings_address": "🗣 Forma de trato",
        "settings_notifications": "🔔 Notificaciones",
        "settings_reset": "🔄 Restablecer configuración",
        "back": "⬅️ Atrás",
        "filter_today": "Hoy",
        "filter_week": "Semana",
        "filter_month": "Mes",
        "random_moment": "🎲 Momento aleatorio",
        "another_random": "🎲 Otro aleatorio",
        "delete_moment": "🗑️ Eliminar",
        "all_moments": "📖 Todos los momentos",
        "exit_dialog": "🚪 Salir del diálogo",
        "confirm_delete": "❌ Sí, eliminar todo",
        "cancel_delete": "✅ No, cancelar",
        "confirm_delete_moment": "✅ Sí, eliminar",
        "cancel": "❌ Cancelar",
        "skip_question": "⏭ Saltar",
        "social_add": "➕ Agregar red social",
        "social_bio": "📝 Editar bio",
        "social_parse": "🔍 Definir intereses",
        "social_remove": "🗑 Eliminar enlace",
        "no_social_links": "No hay redes sociales añadidas",
        "feedback_suggestion": "💡 Idea/sugerencia",
        "feedback_bug": "🐛 Reportar un error",
        "feedback_other": "💬 Otro",
        "feedback_cancel": "⬅️ Cancelar",
        "feedback_submit": "✅ Enviar",
        "feedback_new": "💡 Sugerir más",
        "feedback_menu": "⬅️ Volver al menú",
        "summary_weekly": "📅 Semanal",
        "summary_monthly": "🗓 Mensual",
        "interval_1h": "1 hora",
        "interval_2h": "2 horas",
        "interval_3h": "3 horas",
        "interval_4h": "4 horas",
        "interval_6h": "6 horas",
        "interval_8h": "8 horas",
        "address_informal": "De «tú» 😊",
        "address_formal": "De «usted» 🤝",
        "gender_male": "👨 Él",
        "gender_female": "👩 Ella",
        "gender_neutral": "⚪ Neutral",
        "settings_gender": "🚻 Género",
        "settings_language": "🌐 Idioma de la interfaz",
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
        "social_link_saved": "✅ Enlace guardado",
        "social_parse_failed": "Lamentablemente, no pudimos obtener los datos de tu perfil. El enlace se ha guardado, pero no se utilizará para la personalización.",
    },}


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
            "⚙️ <b>Важно:</b> Пожалуйста, настрой свой <b>часовой пояс</b> и <b>частоту сообщений</b> "
            "в разделе ⚙️ Настройки, чтобы я писал тебе в удобное время!\n\n"
            "🔒 Твои данные в безопасности и используются только для нашего общения.\n"
            "Подробнее: /privacy"
        ),
        "address_formal_confirm": (
            "Хорошо! Буду обращаться на «вы» 😊\n\n"
            "Теперь немного о том, как это работает:\n\n"
            "• Каждые несколько часов я спрошу: «Что хорошего произошло?»\n"
            "• Вы можете ответить текстом или голосовым сообщением\n"
            "• Я сохраню Ваши моменты и напомню о них, когда понадобится поддержка\n\n"
            "⚙️ <b>Важно:</b> Пожалуйста, настройте свой <b>часовой пояс</b> и <b>частоту сообщений</b> "
            "в разделе ⚙️ Настройки, чтобы я писал Вам в удобное время!\n\n"
            "🔒 Ваши данные в безопасности и используются только для нашего общения.\n"
            "Подробнее: /privacy"
        ),
        "welcome_with_voice": (
            "Привет, {first_name}! 👋\n\n"
            "Я — твой помощник для развития позитивного мышления. "
            "Каждый день я буду спрашивать тебя о хорошем, "
            "чтобы вместе замечать радостные моменты жизни. ✨\n\n"
            "💬 Ты можешь отвечать текстом или голосовыми сообщениями - я пойму оба варианта!\n\n"
            "Давай начнём! Как тебе удобнее общаться?"
        ),
        "onboarding_select_gender": (
            "Отлично! Буду обращаться на «ты» 😊\n\n"
            "Теперь выбери, как тебя лучше называть:\n\n"
            "Это поможет мне задавать более персонализированные вопросы."
        ),
        "onboarding_select_gender_formal": (
            "Хорошо! Буду обращаться на «вы» 😊\n\n"
            "Теперь выберите, как Вас лучше называть:\n\n"
            "Это поможет мне задавать более персонализированные вопросы."
        ),
        "onboarding_timezone_important": (
            "🌍 <b>Важно: Выбор часового пояса</b>\n\n"
            "Это очень важно! Без правильного часового пояса я могу начать отправлять "
            "сообщения ночью, когда ты не хочешь получать уведомления. 😴\n\n"
            "Я буду писать тебе только в активные часы (по умолчанию с 9:00 до 21:00), "
            "но для этого мне нужно знать твой часовой пояс.\n\n"
            "Пожалуйста, выбери свой часовой пояс:"
        ),
        "onboarding_ready_confirm": (
            "Всё готово! 🎉\n\n"
            "Я буду задавать тебе вопросы о хороших моментах дня.\n\n"
            "Готов начать? Или хочешь сначала настроить часовой пояс и интервал?"
        ),
        "onboarding_complete": (
            "Отлично! Всё готово! 🎉\n\n"
            "Теперь немного о том, как это работает:\n\n"
            "• Каждые несколько часов я спрошу: «Что хорошего произошло?»\n"
            "• Ты можешь ответить текстом или голосовым сообщением\n"
            "• Я сохраню твои моменты и напомню о них, когда понадобится поддержка\n\n"
            "📝 <b>Примеры ответов:</b>\n"
            "• «Сегодня прогулялся в парке, было очень красиво!»\n"
            "• «Встретился с друзьями, хорошо пообщались»\n"
            "• «Закончил важный проект, чувствую гордость»\n"
            "• «Выпил вкусный кофе и почитал книгу»\n\n"
            "🔒 Твои данные в безопасности и используются только для нашего общения.\n"
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
            "⚙️ <b>Important:</b> Please set up your <b>timezone</b> and <b>message frequency</b> "
            "in ⚙️ Settings, so I can message you at a convenient time!\n\n"
            "🔒 Your data is safe and used only for our communication.\n"
            "More info: /privacy"
        ),
        "address_formal_confirm": (
            "Understood! I'll use formal communication 😊\n\n"
            "Here's how it works:\n\n"
            "• Every few hours I'll ask: \"What good happened?\"\n"
            "• You can reply with text or voice message\n"
            "• I'll save your moments and remind you of them when you need support\n\n"
            "⚙️ <b>Important:</b> Please set up your <b>timezone</b> and <b>message frequency</b> "
            "in ⚙️ Settings, so I can message you at a convenient time!\n\n"
            "🔒 Your data is safe and used only for our communication.\n"
            "More info: /privacy"
        ),
        "welcome_with_voice": (
            "Hello, {first_name}! 👋\n\n"
            "I'm your assistant for developing positive thinking. "
            "Every day I will ask you about good things, "
            "so that we can notice the joyful moments of life together. ✨\n\n"
            "💬 You can reply with text or voice messages - I'll understand both!\n\n"
            "Let's begin! How would you prefer to communicate?"
        ),
        "onboarding_select_gender": (
            "Great! I'll use informal communication 😊\n\n"
            "Now choose how you'd like to be addressed:\n\n"
            "This will help me ask more personalized questions."
        ),
        "onboarding_select_gender_formal": (
            "Understood! I'll use formal communication 😊\n\n"
            "Now please choose how you'd like to be addressed:\n\n"
            "This will help me ask more personalized questions."
        ),
        "onboarding_timezone_important": (
            "🌍 <b>Important: Timezone Selection</b>\n\n"
            "This is very important! Without the correct timezone, I might start sending "
            "messages at night when you don't want to receive notifications. 😴\n\n"
            "I will only message you during active hours (default 9:00 AM to 9:00 PM), "
            "but I need to know your timezone for that.\n\n"
            "Please select your timezone:"
        ),
        "onboarding_ready_confirm": (
            "Everything is ready! 🎉\n\n"
            "I will ask you questions about good moments of the day.\n\n"
            "Ready to start? Or would you like to configure timezone and interval first?"
        ),
        "onboarding_complete": (
            "Excellent! Everything is ready! 🎉\n\n"
            "Here's how it works:\n\n"
            "• Every few hours I'll ask: \"What good happened?\"\n"
            "• You can reply with text or voice message\n"
            "• I'll save your moments and remind you of them when you need support\n\n"
            "📝 <b>Answer examples:</b>\n"
            "• \"Today I walked in the park, it was very beautiful!\"\n"
            "• \"Met with friends, had a good conversation\"\n"
            "• \"Finished an important project, feeling proud\"\n"
            "• \"Had a delicious coffee and read a book\"\n\n"
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
            "⚙️ <b>Важливо:</b> Будь ласка, налаштуй свій <b>часовий пояс</b> та <b>частоту повідомлень</b> "
            "в розділі ⚙️ Налаштування, щоб я писав тобі в зручний час!\n\n"
            "🔒 Твої дані в безпеці і використовуються тільки для нашого спілкування.\n"
            "Детальніше: /privacy"
        ),
        "address_formal_confirm": (
            "Добре! Буду звертатися на «ви» 😊\n\n"
            "Ось як це працює:\n\n"
            "• Кожні кілька годин я запитаю: «Що хорошого сталося?»\n"
            "• Ви можете відповісти текстом або голосовим повідомленням\n"
            "• Я збережу Ваші моменти і нагадаю про них, коли потрібна підтримка\n\n"
            "⚙️ <b>Важливо:</b> Будь ласка, налаштуйте свій <b>часовий пояс</b> та <b>частоту повідомлень</b> "
            "в розділі ⚙️ Налаштування, щоб я писав Вам в зручний час!\n\n"
            "🔒 Ваші дані в безпеці і використовуються тільки для нашого спілкування.\n"
            "Детальніше: /privacy"
        ),
        "welcome_with_voice": (
            "Привіт, {first_name}! 👋\n\n"
            "Я — твій помічник для розвитку позитивного мислення. "
            "Щодня я буду запитувати тебе про хороше, "
            "щоб разом помічати радісні моменти життя. ✨\n\n"
            "💬 Ти можеш відповідати текстом або голосовими повідомленнями - я зрозумію обидва варіанти!\n\n"
            "Давай почнемо! Як тобі зручніше спілкуватися?"
        ),
        "onboarding_select_gender": (
            "Чудово! Буду звертатися на «ти» 😊\n\n"
            "Тепер вибери, як тебе краще називати:\n\n"
            "Це допоможе мені задавати більш персоналізовані питання."
        ),
        "onboarding_select_gender_formal": (
            "Добре! Буду звертатися на «ви» 😊\n\n"
            "Тепер виберіть, як Вас краще називати:\n\n"
            "Це допоможе мені задавати більш персоналізовані питання."
        ),
        "onboarding_timezone_important": (
            "🌍 <b>Важливо: Вибір часового поясу</b>\n\n"
            "Це дуже важливо! Без правильного часового поясу я можу почати надсилати "
            "повідомлення вночі, коли ти не хочеш отримувати сповіщення. 😴\n\n"
            "Я буду писати тобі тільки в активні години (за замовчуванням з 9:00 до 21:00), "
            "але для цього мені потрібно знати твій часовий пояс.\n\n"
            "Будь ласка, вибери свій часовий пояс:"
        ),
        "onboarding_ready_confirm": (
            "Все готово! 🎉\n\n"
            "Я буду запитувати тебе про хороші моменти дня.\n\n"
            "Готовий почати? Чи хочеш спочатку налаштувати часовий пояс та інтервал?"
        ),
        "onboarding_complete": (
            "Чудово! Все готово! 🎉\n\n"
            "Ось як це працює:\n\n"
            "• Кожні кілька годин я запитаю: «Що хорошого сталося?»\n"
            "• Ти можеш відповісти текстом або голосовим повідомленням\n"
            "• Я збережу твої моменти і нагадаю про них, коли потрібна підтримка\n\n"
            "📝 <b>Приклади відповідей:</b>\n"
            "• «Сьогодні прогулявся в парку, було дуже красиво!»\n"
            "• «Зустрівся з друзями, добре поспілкувалися»\n"
            "• «Закінчив важливий проект, відчуваю гордість»\n"
            "• «Випив смачну каву і почитав книгу»\n\n"
            "🔒 Твої дані в безпеці і використовуються тільки для нашого спілкування.\n"
            "Детальніше: /privacy"
        ),
    },
    "he": {
        "address_informal_button": "ב«אתה» 😊",
        "address_formal_button": "ב«אתם» 🤝",
        "address_informal_confirm": (
            "מעולה! אפנה אליך ב«אתה» 😊\n\n"
            "איך זה עובד:\n\n"
            "• כל כמה שעות אשאל: «מה טוב קרה?»\n"
            "• תוכל לענות בטקסט או בהודעת קול\n"
            "• אשמור את הרגעים שלך ואזכיר לך כשתצטרך תמיכה\n\n"
            "⚙️ <b>חשוב:</b> אנא הגדר את <b>אזור הזמן</b> ו<b>תדירות ההודעות</b> "
            "ב⚙️ הגדרות, כדי שאכתוב לך בזמן הנוח!\n\n"
            "🔒 הנתונים שלך מאובטחים ומשמשים רק לתקשורת בינינו.\n"
            "מידע נוסף: /privacy"
        ),
        "address_formal_confirm": (
            "בסדר! אפנה אליכם ב«אתם» 😊\n\n"
            "איך זה עובד:\n\n"
            "• כל כמה שעות אשאל: «מה טוב קרה?»\n"
            "• תוכלו לענות בטקסט או בהודעת קול\n"
            "• אשמור את הרגעים שלכם ואזכיר כשתצטרכו תמיכה\n\n"
            "⚙️ <b>חשוב:</b> אנא הגדירו את <b>אזור הזמן</b> ו<b>תדירות ההודעות</b> "
            "ב⚙️ הגדרות, כדי שאכתוב בזמן הנוח!\n\n"
            "🔒 הנתונים שלכם מאובטחים ומשמשים רק לתקשורת בינינו.\n"
            "מידע נוסף: /privacy"
        ),
        "welcome_with_voice": (
            "שלום, {first_name}! 👋\n\n"
            "אני העוזר שלך לפיתוח חשיבה חיובית. "
            "בכל יום אשאל אותך על הדברים הטובים, "
            "כדי שנבחין יחד ברגעים השמחים של החיים. ✨\n\n"
            "💬 תוכל לענות בטקסט או בהודעות קול — אני אבין את שני האפשרויות!\n\n"
            "בואו נתחיל! איך נוח לך לתקשר?"
        ),
        "onboarding_select_gender": (
            "מעולה! אפנה אליך ב«אתה» 😊\n\n"
            "עכשיו בחר איך לכנות אותך:\n\n"
            "זה יעזור לי לשאול שאלות מותאמות יותר."
        ),
        "onboarding_select_gender_formal": (
            "בסדר! אפנה אליכם ב«אתם» 😊\n\n"
            "עכשיו בחרו איך לכנות אתכם:\n\n"
            "זה יעזור לי לשאול שאלות מותאמות יותר."
        ),
        "onboarding_timezone_important": (
            "🌍 <b>חשוב: בחירת אזור זמן</b>\n\n"
            "זה חשוב מאוד! בלי אזור זמן נכון אולי אתחיל לשלוח "
            "הודעות בלילה, כשאתה לא רוצה לקבל התראות. 😴\n\n"
            "אכתוב לך רק בשעות הפעילות (ברירת מחדל 9:00–21:00), "
            "אבל לשם כך אני צריך לדעת את אזור הזמן שלך.\n\n"
            "אנא בחר את אזור הזמן שלך:"
        ),
        "onboarding_ready_confirm": (
            "הכל מוכן! 🎉\n\n"
            "אשאל אותך שאלות על הרגעים הטובים של היום.\n\n"
            "מוכן להתחיל? או שברצונך קודם להגדיר אזור זמן ומרווח?"
        ),
        "onboarding_complete": (
            "מעולה! הכל מוכן! 🎉\n\n"
            "איך זה עובד:\n\n"
            "• כל כמה שעות אשאל: «מה טוב קרה?»\n"
            "• תוכל לענות בטקסט או בהודעת קול\n"
            "• אשמור את הרגעים שלך ואזכיר כשתצטרך תמיכה\n\n"
            "📝 <b>דוגמאות לתשובות:</b>\n"
            "• «הלכתי היום בפארק, היה יפה מאוד!»\n"
            "• «נפגשתי עם חברים, שוחחנו יפה»\n"
            "• «סיימתי פרויקט חשוב, מרגיש גאווה»\n"
            "• «שתיתי קפה טעים וקראתי ספר»\n\n"
            "🔒 הנתונים שלך מאובטחים ומשמשים רק לתקשורת בינינו.\n"
            "מידע נוסף: /privacy"
        ),
    },
    "es": {
        "address_informal_button": "De «tú» 😊",
        "address_formal_button": "De «usted» 🤝",
        "address_informal_confirm": (
            "¡Genial! Me dirigiré a ti de «tú» 😊\n\n"
            "Así funciona:\n\n"
            "• Cada pocas horas te preguntaré: «¿Qué bueno pasó?»\n"
            "• Puedes responder con texto o mensaje de voz\n"
            "• Guardaré tus momentos y te recordaré cuando necesites apoyo\n\n"
            "⚙️ <b>Importante:</b> Configura tu <b>zona horaria</b> y <b>frecuencia de mensajes</b> "
            "en ⚙️ Ajustes, para escribirte a una hora conveniente.\n\n"
            "🔒 Tus datos están seguros y se usan solo para nuestra comunicación.\n"
            "Más info: /privacy"
        ),
        "address_formal_confirm": (
            "Entendido. Me dirigiré a usted de «usted» 😊\n\n"
            "Así funciona:\n\n"
            "• Cada pocas horas le preguntaré: «¿Qué bueno pasó?»\n"
            "• Puede responder con texto o mensaje de voz\n"
            "• Guardaré sus momentos y le recordaré cuando necesite apoyo\n\n"
            "⚙️ <b>Importante:</b> Configure su <b>zona horaria</b> y <b>frecuencia de mensajes</b> "
            "en ⚙️ Ajustes.\n\n"
            "🔒 Sus datos están seguros. Más info: /privacy"
        ),
        "welcome_with_voice": (
            "¡Hola, {first_name}! 👋\n\n"
            "Soy tu asistente para desarrollar el pensamiento positivo. "
            "Cada día te preguntaré por lo bueno "
            "para notar juntos los momentos alegres de la vida. ✨\n\n"
            "💬 Puedes responder con texto o mensajes de voz, ¡entiendo ambos!\n\n"
            "¡Empecemos! ¿Cómo prefieres que te hable?"
        ),
        "onboarding_select_gender": (
            "¡Genial! De «tú» 😊\n\n"
            "Elige cómo prefieres que te llame:\n\n"
            "Así podré hacer preguntas más personalizadas."
        ),
        "onboarding_select_gender_formal": (
            "Entendido. De «usted» 😊\n\n"
            "Elija cómo prefiere que le llame:\n\n"
            "Así podré hacer preguntas más personalizadas."
        ),
        "onboarding_timezone_important": (
            "🌍 <b>Importante: zona horaria</b>\n\n"
            "Sin la zona correcta, podría enviarte mensajes de noche. 😴\n\n"
            "Te escribiré solo en horas activas (por defecto 9:00–21:00). "
            "Necesito saber tu zona horaria.\n\n"
            "Elige tu zona horaria:"
        ),
        "onboarding_ready_confirm": (
            "¡Todo listo! 🎉\n\n"
            "Te preguntaré por los buenos momentos del día.\n\n"
            "¿Comenzamos? ¿O prefieres configurar antes zona e intervalo?"
        ),
        "onboarding_complete": (
            "¡Excelente! Todo listo. 🎉\n\n"
            "• Cada pocas horas preguntaré: «¿Qué bueno pasó?»\n"
            "• Responde con texto o voz\n"
            "• Guardaré tus momentos y te recordaré cuando necesites apoyo\n\n"
            "📝 <b>Ejemplos:</b> «Paseé por el parque», «Quedé con amigos», «Terminé un proyecto».\n\n"
            "🔒 Tus datos seguros. Más info: /privacy"
        ),
    },
    "de": {
        "address_informal_button": "Mit «du» 😊",
        "address_formal_button": "Mit «Sie» 🤝",
        "address_informal_confirm": (
            "Super! Ich werde dich «du» nennen 😊\n\n"
            "So funktioniert es:\n\n"
            "• Alle paar Stunden frage ich: „Was war heute schön?“\n"
            "• Du kannst mit Text oder Sprachnachricht antworten\n"
            "• Ich speichere deine Momente und erinnere dich bei Bedarf\n\n"
            "⚙️ <b>Wichtig:</b> Stelle <b>Zeitzone</b> und <b>Nachrichtenrhythmus</b> "
            "unter ⚙️ Einstellungen ein.\n\n"
            "🔒 Deine Daten sind sicher. Mehr: /privacy"
        ),
        "address_formal_confirm": (
            "Verstanden. Ich werde Sie «Sie» nennen 😊\n\n"
            "So funktioniert es:\n\n"
            "• Alle paar Stunden frage ich: „Was war heute schön?“\n"
            "• Sie können mit Text oder Sprachnachricht antworten\n"
            "• Ich speichere Ihre Momente und erinnere Sie bei Bedarf\n\n"
            "⚙️ <b>Wichtig:</b> Legen Sie <b>Zeitzone</b> und <b>Rhythmus</b> in ⚙️ Einstellungen fest.\n\n"
            "🔒 Ihre Daten sind sicher. Mehr: /privacy"
        ),
        "welcome_with_voice": (
            "Hallo, {first_name}! 👋\n\n"
            "Ich bin dein Assistent für positives Denken. "
            "Jeden Tag frage ich dich nach dem Guten, "
            "damit wir gemeinsam die schönen Momente bemerken. ✨\n\n"
            "💬 Du kannst mit Text oder Sprachnachrichten antworten – beides verstehe ich!\n\n"
            "Lass uns starten! Wie soll ich dich ansprechen?"
        ),
        "onboarding_select_gender": (
            "Super! «Du» 😊\n\n"
            "Wähle, wie ich dich nennen soll:\n\n"
            "Das hilft mir, passendere Fragen zu stellen."
        ),
        "onboarding_select_gender_formal": (
            "Verstanden. «Sie» 😊\n\n"
            "Bitte wählen Sie, wie ich Sie ansprechen soll.\n\n"
            "Das hilft mir bei der Personalisierung."
        ),
        "onboarding_timezone_important": (
            "🌍 <b>Wichtig: Zeitzone</b>\n\n"
            "Ohne die richtige Zeitzone könnte ich dir nachts schreiben. 😴\n\n"
            "Ich schreibe nur in aktiven Stunden (Standard 9–21 Uhr). "
            "Dafür brauche ich deine Zeitzone.\n\n"
            "Bitte wähle deine Zeitzone:"
        ),
        "onboarding_ready_confirm": (
            "Alles bereit! 🎉\n\n"
            "Ich werde dich nach den schönen Momenten des Tages fragen.\n\n"
            "Bereit? Oder zuerst Zeitzone und Intervall einstellen?"
        ),
        "onboarding_complete": (
            "Alles klar! 🎉\n\n"
            "• Alle paar Stunden: „Was war heute schön?“\n"
            "• Antworte mit Text oder Sprachnachricht\n"
            "• Ich speichere deine Momente und erinnere dich\n\n"
            "📝 <b>Beispiele:</b> „Spaziergang im Park“, „Treffen mit Freunden“, „Projekt abgeschlossen“.\n\n"
            "🔒 Deine Daten sind sicher. Mehr: /privacy"
        ),
    },
    "fr": {
        "address_informal_button": "En «tu» 😊",
        "address_formal_button": "En «vous» 🤝",
        "address_informal_confirm": (
            "Parfait ! Je te tutoierai 😊\n\n"
            "Comment ça marche :\n\n"
            "• Toutes les quelques heures je demanderai : « Quoi de bon aujourd'hui ? »\n"
            "• Tu peux répondre par texte ou message vocal\n"
            "• Je sauvegarde tes moments et te rappellerai quand tu auras besoin de soutien\n\n"
            "⚙️ <b>Important :</b> Règle ta <b>fuseau horaire</b> et la <b>fréquence des messages</b> "
            "dans ⚙️ Paramètres.\n\n"
            "🔒 Tes données sont protégées. En savoir plus : /privacy"
        ),
        "address_formal_confirm": (
            "Très bien. Je vous vouvoyerai 😊\n\n"
            "Comment ça marche :\n\n"
            "• Toutes les quelques heures je demanderai : « Quoi de bon aujourd'hui ? »\n"
            "• Vous pouvez répondre par texte ou message vocal\n"
            "• Je sauvegarde vos moments et vous rappellerai si besoin\n\n"
            "⚙️ <b>Important :</b> Réglage du <b>fuseau</b> et de la <b>fréquence</b> dans ⚙️ Paramètres.\n\n"
            "🔒 Vos données sont protégées. /privacy"
        ),
        "welcome_with_voice": (
            "Salut, {first_name} ! 👋\n\n"
            "Je suis ton assistant pour la pensée positive. "
            "Chaque jour je te demanderai ce qui va bien "
            "pour repérer ensemble les moments joyeux. ✨\n\n"
            "💬 Tu peux répondre par texte ou vocal, je comprends les deux !\n\n"
            "C'est parti ! Tu préfères qu'on se tutoie ou qu'on se vouvoie ?"
        ),
        "onboarding_select_gender": (
            "Parfait ! Tutoiement 😊\n\n"
            "Choisis comment tu préfères que je t'appelle :\n\n"
            "Ça m'aide à poser des questions plus personnalisées."
        ),
        "onboarding_select_gender_formal": (
            "Très bien. Vouvoiement 😊\n\n"
            "Choisissez comment vous préférez que je vous appelle.\n\n"
            "Ça m'aide à personnaliser les questions."
        ),
        "onboarding_timezone_important": (
            "🌍 <b>Important : fuseau horaire</b>\n\n"
            "Sans le bon fuseau, je pourrais t'écrire la nuit. 😴\n\n"
            "J'écris seulement en heures actives (9h–21h par défaut). "
            "Il me faut ton fuseau.\n\n"
            "Choisis ton fuseau horaire :"
        ),
        "onboarding_ready_confirm": (
            "Tout est prêt ! 🎉\n\n"
            "Je te demanderai les bons moments de la journée.\n\n"
            "On commence ? Ou tu veux d'abord réglage fuseau et fréquence ?"
        ),
        "onboarding_complete": (
            "Tout est prêt ! 🎉\n\n"
            "• Toutes les quelques heures : « Quoi de bon ? »\n"
            "• Réponds par texte ou vocal\n"
            "• Je sauvegarde tes moments et te rappellerai\n\n"
            "📝 <b>Exemples :</b> « Balade au parc », « Café avec des amis », « Projet terminé ».\n\n"
            "🔒 Données protégées. /privacy"
        ),
    },
    "pt": {
        "address_informal_button": "Por «tu» 😊",
        "address_formal_button": "Por «você» 🤝",
        "address_informal_confirm": (
            "Ótimo! Vou falar contigo por «tu» 😊\n\n"
            "Assim funciona:\n\n"
            "• De tantas em tantas horas pergunto: «O que correu bem?»\n"
            "• Podes responder por texto ou voz\n"
            "• Guardo os teus momentos e lembro-te quando precisares de apoio\n\n"
            "⚙️ <b>Importante:</b> Configura <b>fuso horário</b> e <b>frequência</b> em ⚙️ Definições.\n\n"
            "🔒 Os teus dados estão seguros. Mais: /privacy"
        ),
        "address_formal_confirm": (
            "Entendido. «Você» 😊\n\n"
            "Assim funciona:\n\n"
            "• De tantas em tantas horas pergunto: «O que correu bem?»\n"
            "• Pode responder por texto ou voz\n"
            "• Guardo os seus momentos e lembro-o quando precisar\n\n"
            "⚙️ <b>Importante:</b> Configurar fuso e frequência em ⚙️ Definições.\n\n"
            "🔒 Dados seguros. /privacy"
        ),
        "welcome_with_voice": (
            "Olá, {first_name}! 👋\n\n"
            "Sou o teu assistente para o pensamento positivo. "
            "Todos os dias pergunto pelo que correu bem "
            "para notarmos juntos os momentos bons. ✨\n\n"
            "💬 Podes responder por texto ou voz – percebo os dois!\n\n"
            "Vamos começar! Como prefires que te trate?"
        ),
        "onboarding_select_gender": (
            "Ótimo! «Tu» 😊\n\n"
            "Escolhe como prefires ser tratado:\n\n"
            "Assim faço perguntas mais personalizadas."
        ),
        "onboarding_select_gender_formal": (
            "Entendido. «Você» 😊\n\n"
            "Escolha como prefere ser tratado.\n\n"
            "Ajuda a personalizar as perguntas."
        ),
        "onboarding_timezone_important": (
            "🌍 <b>Importante: fuso horário</b>\n\n"
            "Sem o fuso certo, posso enviar mensagens de noite. 😴\n\n"
            "Escrevo só em horas ativas (9h–21h). Preciso do teu fuso.\n\n"
            "Escolhe o teu fuso:"
        ),
        "onboarding_ready_confirm": (
            "Tudo pronto! 🎉\n\n"
            "Vou perguntar pelos bons momentos do dia.\n\n"
            "Começamos? Ou preferes configurar fuso e intervalo primeiro?"
        ),
        "onboarding_complete": (
            "Tudo pronto! 🎉\n\n"
            "• De tantas em tantas horas: «O que correu bem?»\n"
            "• Responde por texto ou voz\n"
            "• Guardo os teus momentos e lembro-te\n\n"
            "📝 <b>Exemplos:</b> «Passeio no parque», «Café com amigos», «Projeto concluído».\n\n"
            "🔒 Dados seguros. /privacy"
        ),
    },
    "it": {
        "address_informal_button": "Di «tu» 😊",
        "address_formal_button": "Di «Lei» 🤝",
        "address_informal_confirm": (
            "Perfetto! Mi rivolgerò a te con il «tu» 😊\n\n"
            "Come funziona:\n\n"
            "• Ogni tanto chiederò: «Cosa è andato bene oggi?»\n"
            "• Puoi rispondere con testo o messaggio vocale\n"
            "• Salverò i tuoi momenti e te li ricorderò quando servirà supporto\n\n"
            "⚙️ <b>Importante:</b> Imposta <b>fuso orario</b> e <b>frequenza messaggi</b> in ⚙️ Impostazioni.\n\n"
            "🔒 I tuoi dati sono al sicuro. Maggiori info: /privacy"
        ),
        "address_formal_confirm": (
            "Capito. Mi rivolgerò a Lei con il «Lei» 😊\n\n"
            "Come funziona:\n\n"
            "• Ogni tanto chiederò: «Cosa è andato bene oggi?»\n"
            "• Può rispondere con testo o messaggio vocale\n"
            "• Salverò i Suoi momenti e glieli ricorderò se necessario\n\n"
            "⚙️ <b>Importante:</b> Impostare fuso e frequenza in ⚙️ Impostazioni.\n\n"
            "🔒 Dati al sicuro. /privacy"
        ),
        "welcome_with_voice": (
            "Ciao, {first_name}! 👋\n\n"
            "Sono il tuo assistente per il pensiero positivo. "
            "Ogni giorno ti chiederò del buono "
            "per notare insieme i momenti belli. ✨\n\n"
            "💬 Puoi rispondere con testo o vocali – capisco entrambi!\n\n"
            "Iniziamo! Preferisci il «tu» o il «Lei»?"
        ),
        "onboarding_select_gender": (
            "Perfetto! «Tu» 😊\n\n"
            "Scegli come preferisci essere chiamato:\n\n"
            "Mi aiuta a fare domande più personalizzate."
        ),
        "onboarding_select_gender_formal": (
            "Capito. «Lei» 😊\n\n"
            "Scelga come preferisce essere chiamato.\n\n"
            "Aiuta a personalizzare le domande."
        ),
        "onboarding_timezone_important": (
            "🌍 <b>Importante: fuso orario</b>\n\n"
            "Senza il fuso corretto potrei scriverti di notte. 😴\n\n"
            "Scrivo solo in ore attive (9–21). Mi serve il tuo fuso.\n\n"
            "Scegli il fuso orario:"
        ),
        "onboarding_ready_confirm": (
            "Tutto pronto! 🎉\n\n"
            "Ti chiederò dei bei momenti della giornata.\n\n"
            "Partiamo? O preferisci prima fuso e intervallo?"
        ),
        "onboarding_complete": (
            "Tutto pronto! 🎉\n\n"
            "• Ogni tanto: «Cosa è andato bene?»\n"
            "• Rispondi con testo o vocale\n"
            "• Salvo i tuoi momenti e te li ricordo\n\n"
            "📝 <b>Esempi:</b> «Passeggiata al parco», «Caffè con amici», «Progetto finito».\n\n"
            "🔒 Dati al sicuro. /privacy"
        ),
    },
    "zh": {
        "address_informal_button": "随意 😊",
        "address_formal_button": "正式 🤝",
        "address_informal_confirm": (
            "好的！我们随意交流 😊\n\n"
            "使用方式：\n\n"
            "• 每隔几小时我会问：「今天有什么好事？」\n"
            "• 你可以用文字或语音回复\n"
            "• 我会保存你的美好时刻，在需要时提醒你\n\n"
            "⚙️ <b>重要：</b>请在 ⚙️ 设置 中配置 <b>时区</b> 和 <b>发送频率</b>。\n\n"
            "🔒 你的数据安全，仅用于我们的交流。详情：/privacy"
        ),
        "address_formal_confirm": (
            "好的！我们正式交流 😊\n\n"
            "使用方式：\n\n"
            "• 每隔几小时我会问：「今天有什么好事？」\n"
            "• 您可以用文字或语音回复\n"
            "• 我会保存您的美好时刻并在需要时提醒\n\n"
            "⚙️ <b>重要：</b>请在设置中配置时区与频率。\n\n"
            "🔒 数据安全。/privacy"
        ),
        "welcome_with_voice": (
            "你好，{first_name}！👋\n\n"
            "我是你的积极思维小助手。"
            "每天我会问你今天的好事，"
            "一起发现生活中的快乐时刻。✨\n\n"
            "💬 你可以用文字或语音回复，我都能理解！\n\n"
            "开始吧！你希望怎么交流？"
        ),
        "onboarding_select_gender": (
            "好的！随意 😊\n\n"
            "请选择你希望的称呼方式：\n\n"
            "这样我可以更贴心地提问。"
        ),
        "onboarding_select_gender_formal": (
            "好的！正式 😊\n\n"
            "请选择您希望的称呼方式。\n\n"
            "以便更好地个性化问题。"
        ),
        "onboarding_timezone_important": (
            "🌍 <b>重要：时区</b>\n\n"
            "时区不对，我可能在夜里发消息。😴\n\n"
            "我只在活跃时段（默认 9:00–21:00）发消息，需要知道你的时区。\n\n"
            "请选择你的时区："
        ),
        "onboarding_ready_confirm": (
            "一切就绪！🎉\n\n"
            "我会问你今天的好时刻。\n\n"
            "要开始吗？还是先设置时区和间隔？"
        ),
        "onboarding_complete": (
            "一切就绪！🎉\n\n"
            "• 每隔几小时问：「今天有什么好事？」\n"
            "• 文字或语音回复均可\n"
            "• 我会保存并适时提醒\n\n"
            "📝 <b>示例：</b>「今天逛了公园」「和朋友喝咖啡」「完成了一个项目」。\n\n"
            "🔒 数据安全。/privacy"
        ),
    },
    "ja": {
        "address_informal_button": "カジュアルに 😊",
        "address_formal_button": "丁寧に 🤝",
        "address_informal_confirm": (
            "了解！カジュアルに話します 😊\n\n"
            "使い方：\n\n"
            "• 数時間ごとに「今日いいことあった？」と聞きます\n"
            "• テキストか音声で返答できます\n"
            "• いい瞬間を保存し、必要なときに思い出します\n\n"
            "⚙️ <b>重要：</b>⚙️ 設定 で <b>タイムゾーン</b> と <b>送信頻度</b> を設定してください。\n\n"
            "🔒 データは安全に保管。詳細：/privacy"
        ),
        "address_formal_confirm": (
            "了解！丁寧に話します 😊\n\n"
            "使い方：\n\n"
            "• 数時間ごとに「今日いいことあった？」と聞きます\n"
            "• テキストか音声で返答できます\n"
            "• いい瞬間を保存し、必要なときに思い出します\n\n"
            "⚙️ <b>重要：</b>設定でタイムゾーン・頻度を設定してください。\n\n"
            "🔒 データは安全。/privacy"
        ),
        "welcome_with_voice": (
            "こんにちは、{first_name}！👋\n\n"
            "ポジティブ思考のアシスタントです。"
            "毎日「いいこと」を聞いて、"
            "一緒にうれしい瞬間を見つけます。✨\n\n"
            "💬 テキストも音声もOKです！\n\n"
            "始めましょう！どんな話し方にする？"
        ),
        "onboarding_select_gender": (
            "了解！カジュアル 😊\n\n"
            "呼び方を選んでください：\n\n"
            "よりパーソナルな質問ができます。"
        ),
        "onboarding_select_gender_formal": (
            "了解！丁寧に 😊\n\n"
            "呼び方を選んでください。\n\n"
            "質問のパーソナライズに使います。"
        ),
        "onboarding_timezone_important": (
            "🌍 <b>重要：タイムゾーン</b>\n\n"
            "タイムゾーンが違うと夜中に送信するかもしれません。😴\n\n"
            "アクティブ時間（既定 9–21時）にのみ送ります。タイムゾーンが必要です。\n\n"
            "タイムゾーンを選んでください："
        ),
        "onboarding_ready_confirm": (
            "準備完了！🎉\n\n"
            "今日のいい瞬間について聞きます。\n\n"
            "始めますか？それともタイムゾーンと間隔を先に設定しますか？"
        ),
        "onboarding_complete": (
            "準備完了！🎉\n\n"
            "• 数時間ごとに「今日いいことあった？」\n"
            "• テキストか音声で返信\n"
            "• いい瞬間を保存して思い出します\n\n"
            "📝 <b>例：</b>「公園を散歩」「友達とコーヒー」「プロジェクト完了」。\n\n"
            "🔒 データは安全。/privacy"
        ),
    },
}


def get_onboarding_text(key: str, language_code: str, **kwargs) -> str:
    """
    Get localized onboarding text.

    Args:
        key: Text key (e.g., "address_informal_button", "address_informal_confirm")
        language_code: User's language code
        **kwargs: Optional parameters to format the text (e.g., first_name="John")

    Returns:
        Localized text or Russian fallback
    """
    lang = get_language_code(language_code)
    texts = ONBOARDING_TEXTS.get(lang, ONBOARDING_TEXTS["ru"])
    text = texts.get(key, ONBOARDING_TEXTS["ru"].get(key, ""))
    
    # Format text with parameters if provided
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return text as-is
            return text
    
    return text


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
        "gender_set_neutral": "Пол установлен: нейтрально",

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

        # Pause messages
        "pause_title": "⏸ <b>Остановить бота</b>",
        "pause_title_formal": "⏸ <b>Остановить бота</b>",
        "pause_select_period": "На какой период остановить отправку сообщений?",
        "pause_select_period_formal": "На какой период остановить отправку сообщений?",
        "pause_day": "📅 На день",
        "pause_week": "📅 На неделю",
        "pause_two_weeks": "📅 На две недели",
        "pause_cancel": "⬅️ Отмена",
        "pause_confirmed": "✅ Бот остановлен до {date}. Я не буду отправлять тебе сообщения до этого времени. Если ты напишешь мне, отправка сообщений возобновится автоматически.",
        "pause_confirmed_formal": "✅ Бот остановлен до {date}. Я не буду отправлять Вам сообщения до этого времени. Если Вы напишете мне, отправка сообщений возобновится автоматически.",
        "pause_resumed": "✅ Отправка сообщений возобновлена!",
        "pause_resumed_formal": "✅ Отправка сообщений возобновлена!",

        # Social profile messages
        "social_profile_updated": "Профиль обновлён",
        "social_link_added": "Добавлена ссылка на {network}",
        "social_link_removed": "Ссылка удалена",
        "social_bio_updated": "Биография обновлена",
        "social_profile_not_configured": "Социальный профиль не настроен",
        "social_profile_empty": "Социальный профиль пуст. Добавьте ссылки на соцсети или биографию.",
        "social_networks_label": "<b>Социальные сети:</b>",
        "about_me_label": "<b>О себе:</b>",
        "interests_label": "<b>Интересы:</b>",
        "user_not_found": "Пользователь не найден",
        "profile_not_found": "Профиль не найден",
        "unknown_social_network": "Неизвестная социальная сеть",
        "social_network_not_detected": "Не удалось определить социальную сеть. Поддерживаются: Instagram, Facebook, Twitter/X, LinkedIn, VK, Telegram, YouTube, TikTok",
        "unknown_error": "Неизвестная ошибка",
        "bio_too_long": "❌ Биография слишком длинная. Максимум 1000 символов.",
        "bio_too_long_hint": "Попробуй сократить текст или отправь /cancel для отмены.",
        "bio_too_long_hint_formal": "Попробуйте сократить текст или отправьте /cancel для отмены.",
        "enter_social_link": "Отправь ссылку на свой профиль в социальной сети:",
        "enter_social_link_formal": "Отправьте ссылку на Ваш профиль в социальной сети:",
        "enter_bio": "Расскажи немного о себе (увлечения, интересы):",
        "enter_bio_formal": "Расскажите немного о себе (увлечения, интересы):",
        "interests_detected": "✨ Определены интересы: {interests}",

        # Feedback messages
        "feedback_title": "💡 <b>Предложить идею</b>",
        "feedback_intro": "Я буду рад услышать твои идеи и предложения!",
        "feedback_intro_formal": "Я буду рад услышать Ваши идеи и предложения!",
        "feedback_choose_category": "Выбери категорию:",
        "feedback_choose_category_formal": "Выберите категорию:",
        "feedback_suggestion_title": "💡 <b>Идея/предложение</b>",
        "feedback_suggestion_text": "Напиши свою идею или предложение. Я передам её разработчикам! 📝",
        "feedback_suggestion_text_formal": "Напишите свою идею или предложение. Я передам её разработчикам! 📝",
        "feedback_bug_title": "🐛 <b>Сообщение об ошибке</b>",
        "feedback_bug_text": "Опиши, что пошло не так. Укажи, что ты делал и что произошло. 📝",
        "feedback_bug_text_formal": "Опишите, что пошло не так. Укажите, что Вы делали и что произошло. 📝",
        "feedback_other_title": "💬 <b>Другое</b>",
        "feedback_other_text": "Напиши своё сообщение. 📝",
        "feedback_other_text_formal": "Напишите своё сообщение. 📝",
        "feedback_input_hint": "<i>Просто отправь текстовое сообщение:</i>",
        "feedback_cancelled": "❌ Отменено.",
        "feedback_cancelled_hint": "Если захочешь предложить идею позже, нажми кнопку «💡 Предложить идею» в меню.",
        "feedback_cancelled_hint_formal": "Если захотите предложить идею позже, нажмите кнопку «💡 Предложить идею» в меню.",
        "feedback_error": "😔 Что-то пошло не так. Попробуй ещё раз.",
        "feedback_error_formal": "😔 Что-то пошло не так. Попробуйте ещё раз.",
        "feedback_empty": "🤔 Кажется, сообщение пустое. Напиши текстом, что именно ты хотел(а) сообщить.",
        "feedback_empty_formal": "🤔 Кажется, сообщение пустое. Напишите текстом, что именно Вы хотели сообщить.",
        "feedback_saved": "✅ <b>Спасибо за отзыв!</b>",
        "feedback_saved_details": "📂 Категория: {category}\n📝 Сообщение: {content}",
        "feedback_saved_confirm": "Твоё сообщение сохранено и будет рассмотрено. 💝",
        "feedback_saved_confirm_formal": "Ваше сообщение сохранено и будет рассмотрено. 💝",
        "feedback_saved_short": "Сохранил — скоро посмотрим. 💝",
        "feedback_save_error": "😔 Не удалось сохранить отзыв. Попробуй позже.",
        "feedback_save_error_formal": "😔 Не удалось сохранить отзыв. Попробуйте позже.",
        "feedback_prompt": "Напиши своё предложение или идею:",
        "feedback_prompt_formal": "Напишите Ваше предложение или идею:",
        "feedback_sent": "Спасибо за обратную связь! 💝",
        "feedback_category": "Категория: {category}",
        
        # Question templates (for scheduler)
        "question_1_informal": "Что хорошего произошло сегодня? 🌟",
        "question_2_informal": "Расскажи, чему ты порадовался? ✨",
        "question_3_informal": "Что приятного случилось? 😊",
        "question_4_informal": "Какой момент сегодня был особенным? 💫",
        "question_5_informal": "Что тебя сегодня вдохновило? 🌈",
        "question_6_informal": "Расскажи о маленькой радости дня! 💝",
        "question_7_informal": "Что хорошего ты заметил сегодня? 🌻",
        "question_8_informal": "Чему ты улыбнулся сегодня? 😄",
        "question_1_formal": "Что хорошего произошло сегодня? 🌟",
        "question_2_formal": "Расскажите, чему Вы порадовались? ✨",
        "question_3_formal": "Что приятного случилось? 😊",
        "question_4_formal": "Какой момент сегодня был особенным? 💫",
        "question_5_formal": "Что Вас сегодня вдохновило? 🌈",
        "question_6_formal": "Расскажите о маленькой радости дня! 💝",
        "question_7_formal": "Что хорошего Вы заметили сегодня? 🌻",
        "question_8_formal": "Чему Вы улыбнулись сегодня? 😄",

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

        # Settings section headers
        "settings_title": "⚙️ <b>Настройки</b>",
        "active_hours_title": "🕐 <b>Активные часы</b>",
        "interval_title": "⏰ <b>Интервал между вопросами</b>",
        "address_form_title": "🗣 <b>Форма обращения</b>",
        "gender_title": "🚻 <b>Пол</b>",
        "language_title": "🌐 <b>Язык интерфейса</b>",
        "timezone_title": "🌍 <b>Часовой пояс</b>",
        "social_profile_title": "👤 <b>Социальный профиль</b>",

        # Settings prompts
        "select_active_hours_start": "Выбери время начала активного периода:",
        "select_active_hours_end": "Теперь выбери время окончания:",
        "start_hour_set": "🕐 Начало: {hour}:00",
        "how_often_ask": "Как часто мне спрашивать о хорошем?",
        "how_would_you_like": "Как тебе удобнее?",
        "current_value": "Текущий: {value}",
        "select_gender_prompt": "Выбери пол для правильного обращения:",
        "select_language_prompt": "Выбери язык интерфейса:",
        "select_timezone_prompt": "Выбери свой регион:",
        "select_timezone_city": "Выбери свой часовой пояс:",

        # Gender display values
        "gender_male_value": "мужской",
        "gender_female_value": "женский",
        "gender_unknown": "не указан",

        # Address display values
        "address_formal_value": "на «вы»",
        "address_informal_value": "на «ты»",

        # Notifications display
        "notifications_on": "включены",
        "notifications_off": "выключены",
        "notifications_toggled_on": "🔔 Уведомления включены",
        "notifications_toggled_off": "🔔 Уведомления выключены",
        
        # Settings values display
        "settings.active_hours_value": "🕐 Активные часы: {start} - {end}",
        "settings.interval_value": "⏰ Интервал: каждые {interval} ч.",
        "settings.timezone_value": "🌍 Часовой пояс: {timezone}",
        "settings.formality_value": "🗣 Обращение: {formality}",
        "settings.notifications_value": "🔔 Уведомления: {status}",

        # Interval display
        "every_n_hours": "каждые {hours} ч.",
        "interval_set_confirm": "✅ Интервал установлен: каждые {hours} ч.",

        # Timezone
        "timezone_invalid": "❌ Ошибка: неверный часовой пояс",
        "timezone_set_confirm": "✅ Часовой пояс установлен: {timezone}",

        # Settings reset
        "settings_reset_title": "✅ <b>Настройки сброшены!</b>",
        "settings_reset_error": "😔 Не удалось сбросить настройки. Попробуй позже.",

        # Social profile
        "social_add_prompt": (
            "🔗 <b>Добавить соцсеть</b>\n\n"
            "Отправь ссылку на свою страницу в соцсети.\n\n"
            "Поддерживаются:\n"
            "• Instagram\n• Facebook\n• Twitter/X\n• LinkedIn\n"
            "• ВКонтакте\n• Telegram канал\n• YouTube\n• TikTok\n\n"
            "Отправь /cancel чтобы отменить."
        ),
        "social_bio_prompt": (
            "📝 <b>Редактирование биографии</b>\n\n"
            "Напиши немного о себе, своих увлечениях и интересах.\n"
            "Это поможет мне лучше понять тебя и сделать наше общение более персональным.\n\n"
            "Отправь /cancel чтобы отменить."
        ),
        "social_parsing": "🔍 Анализирую профиль...",
        "social_interests_found": (
            "✅ <b>Интересы определены!</b>\n\n"
            "Твои интересы: {interests}\n\n"
            "Эта информация будет использоваться для персонализации нашего общения."
        ),
        "social_interests_failed": (
            "❌ Не удалось определить интересы.\n\n"
            "Добавь больше информации в свой профиль: ссылки на соцсети или биографию."
        ),
        "social_no_links": "У тебя нет добавленных соцсетей.",
        "social_remove_title": "🗑 <b>Удаление ссылки</b>\n\nВыбери соцсеть для удаления:",

        # Moments
        "moments_title": "📖 <b>Твои хорошие моменты</b>",
        "moments_empty": (
            "📖 У тебя пока нет сохранённых моментов.\n"
            "Когда придёт время вопроса, поделись чем-то хорошим! 🌟"
        ),
        "random_moment_header": "🎲 <b>Случайный хороший момент</b>",
        "moment_not_found": "😔 Момент не найден.",
        "moment_delete_title": "🗑️ <b>Удалить момент?</b>",
        "moment_delete_warning": "⚠️ Это действие необратимо!",
        "moment_deleted_confirm": "✅ Момент удалён.",
        "moment_delete_error": "😔 Не удалось удалить момент.",
        "no_moments_period": "📖 Нет моментов {period}.",
        "moments_period_title": "📖 <b>Моменты {period}</b>",
        "period_today": "сегодня",
        "period_week": "за неделю",
        "period_month": "за месяц",
        "moments_pagination_next": "Следующая страница",
        "moments_pagination_prev": "Предыдущая страница",

        # Dialog mode
        "dialog_intro": (
            "💬 <b>Режим диалога</b>\n\n"
            "Я готов выслушать тебя. Расскажи, что у тебя на душе. "
            "Я постараюсь помочь взглядом со стороны, "
            "но помни — все решения принимаешь ты сам. 💝\n\n"
            "Чтобы выйти из режима диалога, нажми кнопку ниже."
        ),
        "dialog_exit_confirm": "Вернулись в обычный режим. Чем могу помочь? 😊",
        "main_menu_prompt": "Чем могу помочь? 😊",

        # Delete data
        "delete_data_title": "⚠️ <b>Удаление данных</b>",
        "delete_data_confirm": "Ты уверен, что хочешь удалить ВСЕ свои данные из базы данных бота?",
        "delete_data_confirm_formal": "Вы уверены, что хотите удалить ВСЕ свои данные из базы данных бота?",
        "delete_data_warning": "Это действие удалит из базы данных бота:",
        "delete_data_warning_formal": "Это действие удалит из базы данных бота:",
        "delete_data_moments": "• Все твои моменты",
        "delete_data_moments_formal": "• Все Ваши моменты",
        "delete_data_conversations": "• Историю диалогов",
        "delete_data_stats": "• Статистику",
        "delete_data_settings": "• Настройки",
        "delete_data_irreversible": "⚠️ <b>Это действие необратимо!</b>",
        "delete_data_chat_note": "ℹ️ <i>Примечание: Переписка в этом чате на твоём устройстве останется. Удаляются только данные из базы данных бота.</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>Примечание: Переписка в этом чате на Вашем устройстве останется. Удаляются только данные из базы данных бота.</i>",
        "data_deleted": (
            "✅ Все твои данные удалены из базы данных бота.\n\n"
            "Если захочешь вернуться — просто напиши /start 💝"
        ),
        "data_deleted_formal": (
            "✅ Все Ваши данные удалены из базы данных бота.\n\n"
            "Если захотите вернуться — просто напишите /start 💝"
        ),
        "data_delete_error": "😔 Произошла ошибка при удалении. Попробуй позже.",
        "data_delete_error_formal": "😔 Произошла ошибка при удалении. Попробуйте позже.",
        "delete_cancelled": "👍 Удаление отменено. Твои данные в безопасности!",
        "delete_cancelled_formal": "👍 Удаление отменено. Ваши данные в безопасности!",

        # Question skip
        "question_skipped": "👍 Хорошо, пропустим этот вопрос. До скорой встречи! 😊",

        # Summary
        "summary_title": "📊 <b>Саммари моментов</b>",
        "summary_generating_weekly": "⏳ Готовлю еженедельное саммари...",
        "summary_generating_monthly": "⏳ Готовлю месячное саммари...",
        "summary_not_enough_weekly": (
            "📅 Недостаточно моментов для еженедельного саммари.\n\n"
            "Когда у тебя будет больше записей, я смогу создать красивый обзор! 🌟"
        ),
        "summary_not_enough_monthly": (
            "🗓 Недостаточно моментов для месячного саммари.\n\n"
            "Когда у тебя будет больше записей, я смогу создать красивый обзор! 🌟"
        ),

        # Stats
        "stats_empty": (
            "📊 Статистика пока недоступна.\n"
            "Начни отвечать на вопросы, и здесь появится твой прогресс! ✨"
        ),

        # Need to start first
        "please_start_first": "Пожалуйста, сначала запусти бота командой /start",
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
        "gender_set_neutral": "Gender set: neutral",

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

        # Pause messages
        "pause_title": "⏸ <b>Pause bot</b>",
        "pause_title_formal": "⏸ <b>Pause bot</b>",
        "pause_select_period": "For how long should I pause sending messages?",
        "pause_select_period_formal": "For how long should I pause sending messages?",
        "pause_day": "📅 For 1 day",
        "pause_week": "📅 For 1 week",
        "pause_two_weeks": "📅 For 2 weeks",
        "pause_cancel": "⬅️ Cancel",
        "pause_confirmed": "✅ Bot paused until {date}. I won't send you messages until then. If you message me, notifications will resume automatically.",
        "pause_confirmed_formal": "✅ Bot paused until {date}. I won't send you messages until then. If you message me, notifications will resume automatically.",
        "pause_resumed": "✅ Notifications resumed!",
        "pause_resumed_formal": "✅ Notifications resumed!",

        # Social profile messages
        "social_profile_updated": "Profile updated",
        "social_link_added": "✅ Link added to {network}",
        "social_link_removed": "Link removed",
        "social_bio_updated": "Biography updated",
        "social_profile_not_configured": "Social profile is not configured",
        "social_profile_empty": "Social profile is empty. Add social network links or biography.",
        "social_networks_label": "<b>Social Networks:</b>",
        "about_me_label": "<b>About me:</b>",
        "interests_label": "<b>Interests:</b>",
        "user_not_found": "User not found",
        "profile_not_found": "Profile not found",
        "unknown_social_network": "Unknown social network",
        "social_network_not_detected": "Could not detect social network. Supported: Instagram, Facebook, Twitter/X, LinkedIn, VK, Telegram, YouTube, TikTok",
        "unknown_error": "Unknown error",
        "bio_too_long": "❌ Biography is too long. Maximum 1000 characters.",
        "bio_too_long_hint": "Try to shorten the text or send /cancel to cancel.",
        "bio_too_long_hint_formal": "Please try to shorten the text or send /cancel to cancel.",
        "enter_social_link": "Send a link to your social media profile:",
        "enter_social_link_formal": "Please send a link to your social media profile:",
        "enter_bio": "Tell me a bit about yourself (hobbies, interests):",
        "enter_bio_formal": "Please tell me a bit about yourself (hobbies, interests):",
        "interests_detected": "✨ Interests detected: {interests}",

        # Feedback messages
        "feedback_title": "💡 <b>Suggest idea</b>",
        "feedback_intro": "I'll be glad to hear your ideas and suggestions!",
        "feedback_intro_formal": "I'll be glad to hear your ideas and suggestions!",
        "feedback_choose_category": "Choose a category:",
        "feedback_choose_category_formal": "Choose a category:",
        "feedback_suggestion_title": "💡 <b>Idea/suggestion</b>",
        "feedback_suggestion_text": "Write your idea or suggestion. I'll pass it on to the developers! 📝",
        "feedback_suggestion_text_formal": "Please write your idea or suggestion. I'll pass it on to the developers! 📝",
        "feedback_bug_title": "🐛 <b>Report bug</b>",
        "feedback_bug_text": "Describe what went wrong. Tell me what you were doing and what happened. 📝",
        "feedback_bug_text_formal": "Please describe what went wrong. Tell me what you were doing and what happened. 📝",
        "feedback_other_title": "💬 <b>Other</b>",
        "feedback_other_text": "Write your message. 📝",
        "feedback_other_text_formal": "Please write your message. 📝",
        "feedback_input_hint": "<i>Just send a text message:</i>",
        "feedback_cancelled": "❌ Cancelled.",
        "feedback_cancelled_hint": "If you want to suggest an idea later, press the «💡 Suggest idea» button in the menu.",
        "feedback_cancelled_hint_formal": "If you want to suggest an idea later, press the «💡 Suggest idea» button in the menu.",
        "feedback_error": "😔 Something went wrong. Try again.",
        "feedback_error_formal": "😔 Something went wrong. Please try again.",
        "feedback_empty": "🤔 Seems like the message is empty. Write in text what you wanted to report.",
        "feedback_empty_formal": "🤔 Seems like the message is empty. Please write in text what you wanted to report.",
        "feedback_saved": "✅ <b>Thanks for your feedback!</b>",
        "feedback_saved_details": "📂 Category: {category}\n📝 Message: {content}",
        "feedback_saved_confirm": "Your message has been saved and will be reviewed. 💝",
        "feedback_saved_confirm_formal": "Your message has been saved and will be reviewed. 💝",
        "feedback_saved_short": "Saved — we'll look at it soon. 💝",
        "feedback_save_error": "😔 Failed to save feedback. Try again later.",
        "feedback_save_error_formal": "😔 Failed to save feedback. Please try again later.",
        "feedback_prompt": "Write your suggestion or idea:",
        "feedback_prompt_formal": "Please write your suggestion or idea:",
        "feedback_sent": "Thanks for your feedback! 💝",
        "feedback_category": "Category: {category}",
        
        # Question templates (for scheduler)
        "question_1_informal": "What good happened today? 🌟",
        "question_2_informal": "Tell me, what made you happy? ✨",
        "question_3_informal": "What pleasant happened? 😊",
        "question_4_informal": "What moment today was special? 💫",
        "question_5_informal": "What inspired you today? 🌈",
        "question_6_informal": "Tell me about a little joy of the day! 💝",
        "question_7_informal": "What good did you notice today? 🌻",
        "question_8_informal": "What made you smile today? 😄",
        "question_1_formal": "What good happened today? 🌟",
        "question_2_formal": "Tell me, what made you happy? ✨",
        "question_3_formal": "What pleasant happened? 😊",
        "question_4_formal": "What moment today was special? 💫",
        "question_5_formal": "What inspired you today? 🌈",
        "question_6_formal": "Tell me about a little joy of the day! 💝",
        "question_7_formal": "What good did you notice today? 🌻",
        "question_8_formal": "What made you smile today? 😄",

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

        # Settings section headers
        "settings_title": "⚙️ <b>Settings</b>",
        "active_hours_title": "🕐 <b>Active Hours</b>",
        "interval_title": "⏰ <b>Question Interval</b>",
        "address_form_title": "🗣 <b>Address Form</b>",
        "gender_title": "🚻 <b>Gender</b>",
        "language_title": "🌐 <b>Interface Language</b>",
        "timezone_title": "🌍 <b>Timezone</b>",
        "social_profile_title": "👤 <b>Social Profile</b>",

        # Settings prompts
        "select_active_hours_start": "Select the start time of your active period:",
        "select_active_hours_end": "Now select the end time:",
        "start_hour_set": "🕐 Start: {hour}:00",
        "how_often_ask": "How often should I ask about good things?",
        "how_would_you_like": "How would you prefer?",
        "current_value": "Current: {value}",
        "select_gender_prompt": "Select your gender for proper addressing:",
        "select_language_prompt": "Select interface language:",
        "select_timezone_prompt": "Select your region:",
        "select_timezone_city": "Select your timezone:",

        # Gender display values
        "gender_male_value": "male",
        "gender_female_value": "female",
        "gender_unknown": "not specified",

        # Address display values
        "address_formal_value": "formal",
        "address_informal_value": "informal",

        # Notifications display
        "notifications_on": "enabled",
        "notifications_off": "disabled",
        "notifications_toggled_on": "🔔 Notifications enabled",
        "notifications_toggled_off": "🔔 Notifications disabled",
        
        # Settings values display
        "settings.active_hours_value": "🕐 Active hours: {start} - {end}",
        "settings.interval_value": "⏰ Interval: every {interval} h",
        "settings.timezone_value": "🌍 Timezone: {timezone}",
        "settings.formality_value": "🗣 Address form: {formality}",
        "settings.notifications_value": "🔔 Notifications: {status}",

        # Interval display
        "every_n_hours": "every {hours} h.",
        "interval_set_confirm": "✅ Interval set: every {hours} h.",

        # Timezone
        "timezone_invalid": "❌ Error: invalid timezone",
        "timezone_set_confirm": "✅ Timezone set: {timezone}",

        # Settings reset
        "settings_reset_title": "✅ <b>Settings reset!</b>",
        "settings_reset_error": "😔 Failed to reset settings. Try again later.",

        # Social profile
        "social_add_prompt": (
            "🔗 <b>Add Social Network</b>\n\n"
            "Send a link to your social media profile.\n\n"
            "Supported:\n"
            "• Instagram\n• Facebook\n• Twitter/X\n• LinkedIn\n"
            "• VKontakte\n• Telegram channel\n• YouTube\n• TikTok\n\n"
            "Send /cancel to cancel."
        ),
        "social_bio_prompt": (
            "📝 <b>Edit Biography</b>\n\n"
            "Tell me a bit about yourself, your hobbies and interests.\n"
            "This will help me understand you better and personalize our communication.\n\n"
            "Send /cancel to cancel."
        ),
        "social_parsing": "🔍 Analyzing profile...",
        "social_interests_found": (
            "✅ <b>Interests detected!</b>\n\n"
            "Your interests: {interests}\n\n"
            "This information will be used to personalize our communication."
        ),
        "social_interests_failed": (
            "❌ Could not detect interests.\n\n"
            "Add more information to your profile: social media links or biography."
        ),
        "social_no_links": "You don't have any social networks added.",
        "social_remove_title": "🗑 <b>Remove Link</b>\n\nSelect a social network to remove:",

        # Moments
        "moments_title": "📖 <b>Your Good Moments</b>",
        "moments_empty": (
            "📖 You don't have any saved moments yet.\n"
            "When it's time for a question, share something good! 🌟"
        ),
        "random_moment_header": "🎲 <b>Random Good Moment</b>",
        "moment_not_found": "😔 Moment not found.",
        "moment_delete_title": "🗑️ <b>Delete moment?</b>",
        "moment_delete_warning": "⚠️ This action cannot be undone!",
        "moment_deleted_confirm": "✅ Moment deleted.",
        "moment_delete_error": "😔 Failed to delete moment.",
        "no_moments_period": "📖 No moments {period}.",
        "moments_period_title": "📖 <b>Moments {period}</b>",
        "period_today": "today",
        "period_week": "this week",
        "period_month": "this month",
        "moments_pagination_next": "Next page",
        "moments_pagination_prev": "Previous page",

        # Dialog mode
        "dialog_intro": (
            "💬 <b>Dialog Mode</b>\n\n"
            "I'm ready to listen. Tell me what's on your mind. "
            "I'll try to help with an outside perspective, "
            "but remember — all decisions are yours. 💝\n\n"
            "To exit dialog mode, press the button below."
        ),
        "dialog_exit_confirm": "Returned to normal mode. How can I help? 😊",
        "main_menu_prompt": "How can I help? 😊",

        # Delete data
        "delete_data_title": "⚠️ <b>Data Deletion</b>",
        "delete_data_confirm": "Are you sure you want to delete ALL your data from the bot's database?",
        "delete_data_confirm_formal": "Are you sure you want to delete ALL your data from the bot's database?",
        "delete_data_warning": "This action will delete from the bot's database:",
        "delete_data_warning_formal": "This action will delete from the bot's database:",
        "delete_data_moments": "• All your moments",
        "delete_data_moments_formal": "• All your moments",
        "delete_data_conversations": "• Conversation history",
        "delete_data_stats": "• Statistics",
        "delete_data_settings": "• Settings",
        "delete_data_irreversible": "⚠️ <b>This action is irreversible!</b>",
        "delete_data_chat_note": "ℹ️ <i>Note: The chat history on your device will remain. Only data from the bot's database will be deleted.</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>Note: The chat history on your device will remain. Only data from the bot's database will be deleted.</i>",
        "data_deleted": (
            "✅ All your data has been deleted from the bot's database.\n\n"
            "If you want to come back — just write /start 💝"
        ),
        "data_deleted_formal": (
            "✅ All your data has been deleted from the bot's database.\n\n"
            "If you want to come back — just write /start 💝"
        ),
        "data_delete_error": "😔 An error occurred while deleting. Try again later.",
        "data_delete_error_formal": "😔 An error occurred while deleting. Please try again later.",
        "delete_cancelled": "👍 Deletion cancelled. Your data is safe!",
        "delete_cancelled_formal": "👍 Deletion cancelled. Your data is safe!",

        # Question skip
        "question_skipped": "👍 Okay, let's skip this question. See you soon! 😊",

        # Summary
        "summary_title": "📊 <b>Moments Summary</b>",
        "summary_generating_weekly": "⏳ Preparing weekly summary...",
        "summary_generating_monthly": "⏳ Preparing monthly summary...",
        "summary_not_enough_weekly": (
            "📅 Not enough moments for a weekly summary.\n\n"
            "When you have more entries, I'll be able to create a nice overview! 🌟"
        ),
        "summary_not_enough_monthly": (
            "🗓 Not enough moments for a monthly summary.\n\n"
            "When you have more entries, I'll be able to create a nice overview! 🌟"
        ),

        # Stats
        "stats_empty": (
            "📊 Statistics not available yet.\n"
            "Start answering questions, and your progress will appear here! ✨"
        ),

        # Need to start first
        "please_start_first": "Please start the bot first with /start command",
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
        "gender_set_neutral": "Стать встановлено: нейтрально",

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

        # Pause messages
        "pause_title": "⏸ <b>Зупинити бота</b>",
        "pause_title_formal": "⏸ <b>Зупинити бота</b>",
        "pause_select_period": "На який період зупинити відправку повідомлень?",
        "pause_select_period_formal": "На який період зупинити відправку повідомлень?",
        "pause_day": "📅 На день",
        "pause_week": "📅 На тиждень",
        "pause_two_weeks": "📅 На два тижні",
        "pause_cancel": "⬅️ Скасувати",
        "pause_confirmed": "✅ Бота зупинено до {date}. Я не буду надсилати тобі повідомлення до цього часу. Якщо ти напишеш мені, відправка повідомлень відновиться автоматично.",
        "pause_confirmed_formal": "✅ Бота зупинено до {date}. Я не буду надсилати Вам повідомлення до цього часу. Якщо Ви напишете мені, відправка повідомлень відновиться автоматично.",
        "pause_resumed": "✅ Відправка повідомлень відновлена!",
        "pause_resumed_formal": "✅ Відправка повідомлень відновлена!",

        # Social profile messages
        "social_profile_updated": "Профіль оновлено",
        "social_link_added": "✅ Додано посилання на {network}",
        "social_link_removed": "Посилання видалено",
        "social_bio_updated": "Біографія оновлена",
        "social_profile_not_configured": "Соціальний профіль не налаштовано",
        "social_profile_empty": "Соціальний профіль порожній. Додайте посилання на соцмережі або біографію.",
        "social_networks_label": "<b>Соціальні мережі:</b>",
        "about_me_label": "<b>Про себе:</b>",
        "interests_label": "<b>Інтереси:</b>",
        "user_not_found": "Користувача не знайдено",
        "profile_not_found": "Профіль не знайдено",
        "unknown_social_network": "Невідома соціальна мережа",
        "social_network_not_detected": "Не вдалося визначити соціальну мережу. Підтримуються: Instagram, Facebook, Twitter/X, LinkedIn, VK, Telegram, YouTube, TikTok",
        "unknown_error": "Невідома помилка",
        "bio_too_long": "❌ Біографія занадто довга. Максимум 1000 символів.",
        "bio_too_long_hint": "Спробуй скоротити текст або надішли /cancel для скасування.",
        "bio_too_long_hint_formal": "Спробуйте скоротити текст або надішліть /cancel для скасування.",
        "enter_social_link": "Надішли посилання на свій профіль у соціальній мережі:",
        "enter_social_link_formal": "Надішліть посилання на Ваш профіль у соціальній мережі:",
        "enter_bio": "Розкажи трохи про себе (захоплення, інтереси):",
        "enter_bio_formal": "Розкажіть трохи про себе (захоплення, інтереси):",
        "interests_detected": "✨ Визначено інтереси: {interests}",

        # Feedback messages
        "feedback_title": "💡 <b>Запропонувати ідею</b>",
        "feedback_intro": "Я буду радий почути твої ідеї та пропозиції!",
        "feedback_intro_formal": "Я буду радий почути Ваші ідеї та пропозиції!",
        "feedback_choose_category": "Виберіть категорію:",
        "feedback_choose_category_formal": "Виберіть категорію:",
        "feedback_suggestion_title": "💡 <b>Ідея/пропозиція</b>",
        "feedback_suggestion_text": "Напиши свою ідею або пропозицію. Я передам її розробникам! 📝",
        "feedback_suggestion_text_formal": "Напишіть свою ідею або пропозицію. Я передам її розробникам! 📝",
        "feedback_bug_title": "🐛 <b>Повідомлення про помилку</b>",
        "feedback_bug_text": "Опиши, що пішло не так. Вкажи, що ти робив і що сталося. 📝",
        "feedback_bug_text_formal": "Опишіть, що пішло не так. Вкажіть, що Ви робили і що сталося. 📝",
        "feedback_other_title": "💬 <b>Інше</b>",
        "feedback_other_text": "Напиши своє повідомлення. 📝",
        "feedback_other_text_formal": "Напишіть своє повідомлення. 📝",
        "feedback_input_hint": "<i>Просто надішліть текстове повідомлення:</i>",
        "feedback_cancelled": "❌ Скасовано.",
        "feedback_cancelled_hint": "Якщо захочеш запропонувати ідею пізніше, натисни кнопку «💡 Запропонувати ідею» в меню.",
        "feedback_cancelled_hint_formal": "Якщо захочете запропонувати ідею пізніше, натисніть кнопку «💡 Запропонувати ідею» в меню.",
        "feedback_error": "😔 Щось пішло не так. Спробуй ще раз.",
        "feedback_error_formal": "😔 Щось пішло не так. Спробуйте ще раз.",
        "feedback_empty": "🤔 Здається, повідомлення порожнє. Напиши текстом, що саме ти хотів(а) повідомити.",
        "feedback_empty_formal": "🤔 Здається, повідомлення порожнє. Напишіть текстом, що саме Ви хотіли повідомити.",
        "feedback_saved": "✅ <b>Дякуємо за відгук!</b>",
        "feedback_saved_details": "📂 Категорія: {category}\n📝 Повідомлення: {content}",
        "feedback_saved_confirm": "Твоє повідомлення збережено і буде розглянуто. 💝",
        "feedback_saved_confirm_formal": "Ваше повідомлення збережено і буде розглянуто. 💝",
        "feedback_saved_short": "Зберіг — скоро подивимось. 💝",
        "feedback_save_error": "😔 Не вдалося зберегти відгук. Спробуй пізніше.",
        "feedback_save_error_formal": "😔 Не вдалося зберегти відгук. Спробуйте пізніше.",
        "feedback_prompt": "Напиши свою пропозицію або ідею:",
        "feedback_prompt_formal": "Напишіть Вашу пропозицію або ідею:",
        "feedback_sent": "Дякуємо за зворотний зв'язок! 💝",
        "feedback_category": "Категорія: {category}",
        
        # Question templates (for scheduler)
        "question_1_informal": "Що хорошого сталося сьогодні? 🌟",
        "question_2_informal": "Розкажи, чому ти порадувався? ✨",
        "question_3_informal": "Що приємного сталося? 😊",
        "question_4_informal": "Який момент сьогодні був особливим? 💫",
        "question_5_informal": "Що тебе сьогодні надихнуло? 🌈",
        "question_6_informal": "Розкажи про маленьку радість дня! 💝",
        "question_7_informal": "Що хорошого ти помітив сьогодні? 🌻",
        "question_8_informal": "Чому ти посміхнувся сьогодні? 😄",
        "question_1_formal": "Що хорошого сталося сьогодні? 🌟",
        "question_2_formal": "Розкажіть, чому Ви порадувалися? ✨",
        "question_3_formal": "Що приємного сталося? 😊",
        "question_4_formal": "Який момент сьогодні був особливим? 💫",
        "question_5_formal": "Що Вас сьогодні надихнуло? 🌈",
        "question_6_formal": "Розкажіть про маленьку радість дня! 💝",
        "question_7_formal": "Що хорошого Ви помітили сьогодні? 🌻",
        "question_8_formal": "Чому Ви посміхнулися сьогодні? 😄",

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

        # Settings section headers
        "settings_title": "⚙️ <b>Налаштування</b>",
        "active_hours_title": "🕐 <b>Активні години</b>",
        "interval_title": "⏰ <b>Інтервал між запитаннями</b>",
        "address_form_title": "🗣 <b>Форма звертання</b>",
        "gender_title": "🚻 <b>Стать</b>",
        "language_title": "🌐 <b>Мова інтерфейсу</b>",
        "timezone_title": "🌍 <b>Часовий пояс</b>",
        "social_profile_title": "👤 <b>Соціальний профіль</b>",

        # Settings prompts
        "select_active_hours_start": "Вибери час початку активного періоду:",
        "select_active_hours_end": "Тепер вибери час закінчення:",
        "start_hour_set": "🕐 Початок: {hour}:00",
        "how_often_ask": "Як часто мені питати про хороше?",
        "how_would_you_like": "Як тобі зручніше?",
        "current_value": "Поточний: {value}",
        "select_gender_prompt": "Вибери стать для правильного звертання:",
        "select_language_prompt": "Вибери мову інтерфейсу:",
        "select_timezone_prompt": "Вибери свій регіон:",
        "select_timezone_city": "Вибери свій часовий пояс:",

        # Gender display values
        "gender_male_value": "чоловіча",
        "gender_female_value": "жіноча",
        "gender_unknown": "не вказано",

        # Address display values
        "address_formal_value": "на «ви»",
        "address_informal_value": "на «ти»",

        # Notifications display
        "notifications_on": "увімкнено",
        "notifications_off": "вимкнено",
        "notifications_toggled_on": "🔔 Сповіщення увімкнено",
        "notifications_toggled_off": "🔔 Сповіщення вимкнено",
        
        # Settings values display
        "settings.active_hours_value": "🕐 Активні години: {start} - {end}",
        "settings.interval_value": "⏰ Інтервал: кожні {interval} год.",
        "settings.timezone_value": "🌍 Часовий пояс: {timezone}",
        "settings.formality_value": "🗣 Звертання: {formality}",
        "settings.notifications_value": "🔔 Сповіщення: {status}",

        # Interval display
        "every_n_hours": "кожні {hours} год.",
        "interval_set_confirm": "✅ Інтервал встановлено: кожні {hours} год.",

        # Timezone
        "timezone_invalid": "❌ Помилка: неправильний часовий пояс",
        "timezone_set_confirm": "✅ Часовий пояс встановлено: {timezone}",

        # Settings reset
        "settings_reset_title": "✅ <b>Налаштування скинуто!</b>",
        "settings_reset_error": "😔 Не вдалося скинути налаштування. Спробуй пізніше.",

        # Social profile
        "social_add_prompt": (
            "🔗 <b>Додати соцмережу</b>\n\n"
            "Надішли посилання на свою сторінку в соцмережі.\n\n"
            "Підтримуються:\n"
            "• Instagram\n• Facebook\n• Twitter/X\n• LinkedIn\n"
            "• ВКонтакте\n• Telegram канал\n• YouTube\n• TikTok\n\n"
            "Надішли /cancel щоб скасувати."
        ),
        "social_bio_prompt": (
            "📝 <b>Редагування біографії</b>\n\n"
            "Напиши трохи про себе, свої захоплення та інтереси.\n"
            "Це допоможе мені краще зрозуміти тебе і зробити наше спілкування більш персональним.\n\n"
            "Надішли /cancel щоб скасувати."
        ),
        "social_parsing": "🔍 Аналізую профіль...",
        "social_interests_found": (
            "✅ <b>Інтереси визначено!</b>\n\n"
            "Твої інтереси: {interests}\n\n"
            "Ця інформація буде використовуватися для персоналізації нашого спілкування."
        ),
        "social_interests_failed": (
            "❌ Не вдалося визначити інтереси.\n\n"
            "Додай більше інформації до свого профілю: посилання на соцмережі або біографію."
        ),
        "social_no_links": "У тебе немає доданих соцмереж.",
        "social_remove_title": "🗑 <b>Видалення посилання</b>\n\nВибери соцмережу для видалення:",

        # Moments
        "moments_title": "📖 <b>Твої хороші моменти</b>",
        "moments_empty": (
            "📖 У тебе поки немає збережених моментів.\n"
            "Коли прийде час запитання, поділися чимось хорошим! 🌟"
        ),
        "random_moment_header": "🎲 <b>Випадковий хороший момент</b>",
        "moment_not_found": "😔 Момент не знайдено.",
        "moment_delete_title": "🗑️ <b>Видалити момент?</b>",
        "moment_delete_warning": "⚠️ Ця дія незворотна!",
        "moment_deleted_confirm": "✅ Момент видалено.",
        "moment_delete_error": "😔 Не вдалося видалити момент.",
        "no_moments_period": "📖 Немає моментів {period}.",
        "moments_period_title": "📖 <b>Моменти {period}</b>",
        "period_today": "сьогодні",
        "period_week": "за тиждень",
        "period_month": "за місяць",
        "moments_pagination_next": "Наступна сторінка",
        "moments_pagination_prev": "Попередня сторінка",

        # Dialog mode
        "dialog_intro": (
            "💬 <b>Режим діалогу</b>\n\n"
            "Я готовий вислухати тебе. Розкажи, що у тебе на душі. "
            "Я постараюся допомогти поглядом з боку, "
            "але пам'ятай — всі рішення приймаєш ти сам. 💝\n\n"
            "Щоб вийти з режиму діалогу, натисни кнопку нижче."
        ),
        "dialog_exit_confirm": "Повернулися до звичайного режиму. Чим можу допомогти? 😊",
        "main_menu_prompt": "Чим можу допомогти? 😊",

        # Delete data
        "delete_data_title": "⚠️ <b>Видалення даних</b>",
        "delete_data_confirm": "Ти впевнений, що хочеш видалити ВСІ свої дані з бази даних бота?",
        "delete_data_confirm_formal": "Ви впевнені, що хочете видалити ВСІ свої дані з бази даних бота?",
        "delete_data_warning": "Ця дія видалить з бази даних бота:",
        "delete_data_warning_formal": "Ця дія видалить з бази даних бота:",
        "delete_data_moments": "• Всі твої моменти",
        "delete_data_moments_formal": "• Всі Ваші моменти",
        "delete_data_conversations": "• Історію діалогів",
        "delete_data_stats": "• Статистику",
        "delete_data_settings": "• Налаштування",
        "delete_data_irreversible": "⚠️ <b>Ця дія незворотна!</b>",
        "delete_data_chat_note": "ℹ️ <i>Примітка: Переписка в цьому чаті на твоєму пристрої залишиться. Видаляються тільки дані з бази даних бота.</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>Примітка: Переписка в цьому чаті на Вашому пристрої залишиться. Видаляються тільки дані з бази даних бота.</i>",
        "data_deleted": (
            "✅ Всі твої дані видалено з бази даних бота.\n\n"
            "Якщо захочеш повернутися — просто напиши /start 💝"
        ),
        "data_deleted_formal": (
            "✅ Всі Ваші дані видалено з бази даних бота.\n\n"
            "Якщо захотите повернутися — просто напишіть /start 💝"
        ),
        "data_delete_error": "😔 Сталася помилка при видаленні. Спробуй пізніше.",
        "data_delete_error_formal": "😔 Сталася помилка при видаленні. Спробуйте пізніше.",
        "delete_cancelled": "👍 Видалення скасовано. Твої дані в безпеці!",
        "delete_cancelled_formal": "👍 Видалення скасовано. Ваші дані в безпеці!",

        # Question skip
        "question_skipped": "👍 Добре, пропустимо це запитання. До скорої зустрічі! 😊",

        # Summary
        "summary_title": "📊 <b>Саммарі моментів</b>",
        "summary_generating_weekly": "⏳ Готую щотижневе саммарі...",
        "summary_generating_monthly": "⏳ Готую місячне саммарі...",
        "summary_not_enough_weekly": (
            "📅 Недостатньо моментів для щотижневого саммарі.\n\n"
            "Коли у тебе буде більше записів, я зможу створити гарний огляд! 🌟"
        ),
        "summary_not_enough_monthly": (
            "🗓 Недостатньо моментів для місячного саммарі.\n\n"
            "Коли у тебе буде більше записів, я зможу створити гарний огляд! 🌟"
        ),

        # Stats
        "stats_empty": (
            "📊 Статистика поки недоступна.\n"
            "Почни відповідати на запитання, і тут з'явиться твій прогрес! ✨"
        ),

        # Need to start first
        "please_start_first": "Будь ласка, спочатку запусти бота командою /start",
    },

    "he": {
        "saved": "נשמר!",
        "error": "שגיאה",
        "success": "בהצלחה!",
        "cancelled": "בוטל",
        "loading": "טוען...",
        "active_hours_set": "שעות פעילות הוגדרו: {start} - {end}",
        "interval_set": "מרווח התראות: {interval}",
        "timezone_set": "אזור זמן הוגדר: {timezone}",
        "notifications_enabled": "🔔 התראות מופעלות",
        "notifications_disabled": "🔕 התראות כבויות",
        "settings_reset": "ההגדרות הוחזרו לערכים ברירת מחדל",
        "language_changed": "שפה שונתה לרוסית",
        "address_changed_informal": "אפנה אליך ב«אתה»",
        "address_changed_formal": "אפנה אליך ב«אתם»",
        "gender_set_male": "מין הוגדר: זכר",
        "gender_set_female": "מין הוגדר: נקבה",
        "no_moments": "עדיין אין לך רגעים שמורים. ספר לי מה טוב קרה היום!",
        "no_moments_formal": "עדיין אין לכם רגעים שמורים. ספרו לי מה טוב קרה היום!",
        "moment_deleted": "הרגע נמחק",
        "moments_count": "נמצאו רגעים: {count}",
        "random_moment_title": "🎲 רגע שמח אקראי:",
        "stats_title": "📊 הסטטיסטיקה שלך",
        "stats_title_formal": "📊 הסטטיסטיקה שלכם",
        "stats_total_moments": "סה\"כ רגעים: {count}",
        "stats_current_streak": "רצף נוכחי: {days} ימים",
        "stats_longest_streak": "הרצף הארוך ביותר: {days} ימים",
        "stats_response_rate": "אחוז תגובות: {rate}%",
        "stats_not_available": "הסטטיסטיקה עדיין לא זמינה",
        "dialog_started": "💬 מצב דיאלוג. אני מקשיב לך. כתוב «יציאה» או לחץ על הכפתור כדי לצאת.",
        "dialog_started_formal": "💬 מצב דיאלוג. אני מקשיב לכם. כתבו «יציאה» או לחצו על הכפתור כדי לצאת.",
        "dialog_ended": "הדיאלוג הסתיים. מחזיר לתפריט הראשי.",
        "pause_title": "⏸ <b>השהיית בוט</b>",
        "pause_title_formal": "⏸ <b>השהיית בוט</b>",
        "pause_select_period": "לכמה זמן להשהות את שליחת ההודעות?",
        "pause_select_period_formal": "לכמה זמן להשהות את שליחת ההודעות?",
        "pause_day": "📅 ליום אחד",
        "pause_week": "📅 לשבוע",
        "pause_two_weeks": "📅 לשבועיים",
        "pause_cancel": "⬅️ ביטול",
        "pause_confirmed": "✅ הבוט הושהה עד {date}. אני לא אשלח לך הודעות עד אז. אם תכתוב לי, ההודעות יתחדשו אוטומטית.",
        "pause_confirmed_formal": "✅ הבוט הושהה עד {date}. אני לא אשלח לכם הודעות עד אז. אם תכתבו לי, ההודעות יתחדשו אוטומטית.",
        "pause_resumed": "✅ ההודעות התחדשו!",
        "pause_resumed_formal": "✅ ההודעות התחדשו!",
        "social_profile_updated": "הפרופיל עודכן",
        "social_link_removed": "הקישור הוסר",
        "social_profile_not_configured": "פרופיל חברתי לא מוגדר",
        "social_profile_empty": "הפרופיל החברתי ריק. הוסף קישורים לרשתות או ביוגרפיה.",
        "social_networks_label": "<b>רשתות חברתיות:</b>",
        "about_me_label": "<b>עלי:</b>",
        "interests_label": "<b>תחומי עניין:</b>",
        "profile_not_found": "הפרופיל לא נמצא",
        "user_not_found": "המשתמש לא נמצא",
        "enter_social_link": "שלח קישור לפרופיל שלך ברשת החברתית:",
        "enter_social_link_formal": "שלחו קישור לפרופיל שלכם ברשת החברתית:",
        "enter_bio": "ספר קצת על עצמך (תחביבים, עניינים):",
        "enter_bio_formal": "ספרו קצת על עצמכם (תחביבים, עניינים):",
        "interests_detected": "✨ זוהו תחומים: {interests}",
        "feedback_prompt": "כתוב את ההצעה או הרעיון שלך:",
        "feedback_prompt_formal": "כתבו את ההצעה או הרעיון שלכם:",
        "feedback_sent": "תודה על המשוב! 💝",
        "feedback_category": "קטגוריה: {category}",
        "help_title": "📋 פקודות זמינות:",
        "help_start": "/start - להתחיל מחדש",
        "help_help": "/help - להציג עזרה",
        "help_settings": "/settings - הגדרות",
        "help_stats": "/stats - סטטיסטיקה",
        "help_privacy": "/privacy - מדיניות פרטיות",
        "help_export": "/export_data - ייצוא נתונים",
        "help_delete": "/delete_data - מחיקת נתונים",
        "privacy_title": "🔒 מדיניות פרטיות",
        "privacy_text": "אנחנו מתייחסים ברצינות לפרטיות שלך.\n\n📌 אילו נתונים אנחנו שומרים:\n• התשובות שלך לשאלות הבוט\n• הגדרות (אזור זמן, שפה, מרווח)\n• מידע בסיסי מפרופיל Telegram\n\n🔐 איך אנחנו משתמשים בנתונים:\n• רק כדי להתאים אישית את החוויה שלך\n• להזכיר רגעים טובים\n• הנתונים לא מועברים לגורמים שלישיים\n\n🗑 זכויותיך:\n• /export_data - לייצא את כל הנתונים\n• /delete_data - למחוק את כל הנתונים",
        "export_confirm": "לייצא את כל הנתונים שלך?",
        "export_confirm_formal": "לייצא את כל הנתונים שלכם?",
        "export_success": "הנתונים ייצאו",
        "delete_confirm": "⚠️ שים לב! פעולה זו תמחק את כל הנתונים שלך לצמיתות. להמשיך?",
        "delete_confirm_formal": "⚠️ שימו לב! פעולה זו תמחק את כל הנתונים שלכם לצמיתות. להמשיך?",
        "delete_success": "כל הנתונים נמחקו. להתראות! 👋",
        "delete_data_title": "⚠️ <b>מחיקת נתונים</b>",
        "delete_data_confirm": "האם אתה בטוח שברצונך למחוק את כל הנתונים שלך מבסיס הנתונים של הבוט?",
        "delete_data_confirm_formal": "האם אתם בטוחים שברצונכם למחוק את כל הנתונים שלכם מבסיס הנתונים של הבוט?",
        "delete_data_warning": "פעולה זו תמחק מבסיס הנתונים של הבוט:",
        "delete_data_warning_formal": "פעולה זו תמחק מבסיס הנתונים של הבוט:",
        "delete_data_moments": "• את כל הרגעים שלך",
        "delete_data_moments_formal": "• את כל הרגעים שלכם",
        "delete_data_conversations": "• את היסטוריית הדיאלוגים",
        "delete_data_stats": "• סטטיסטיקות",
        "delete_data_settings": "• הגדרות",
        "delete_data_irreversible": "⚠️ <b>פעולה זו אינה הפיכה!</b>",
        "delete_data_chat_note": "ℹ️ <i>ההתכתבות במכשיר שלך תישאר. נמחקים רק הנתונים מבסיס הנתונים של הבוט.</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>ההתכתבות במכשיר שלכם תישאר. נמחקים רק הנתונים מבסיס הנתונים של הבוט.</i>",
        "timezone_select_region": "בחר אזור:",
        "timezone_select_region_formal": "בחרו אזור:",
        "select_start_hour": "בחר את תחילת שעות הפעילות:",
        "select_start_hour_formal": "בחרו את תחילת שעות הפעילות:",
        "select_end_hour": "בחר את סוף שעות הפעילות:",
        "select_end_hour_formal": "בחרו את סוף שעות הפעילות:",
        "current_settings": "⚙️ הגדרות נוכחיות:\n\n🕐 שעות פעילות: {start_hour}:00 - {end_hour}:00\n⏰ מרווח: {interval}\n🌍 אזור זמן: {timezone}\n🗣 פנייה: {address}\n🚻 מין: {gender}\n🔔 התראות: {notifications}\n🌐 שפה: {language}",
        "settings_title": "⚙️ <b>הגדרות</b>",
        "active_hours_title": "🕐 <b>שעות פעילות</b>",
        "interval_title": "⏰ <b>מרווח בין שאלות</b>",
        "address_form_title": "🗣 <b>צורת פנייה</b>",
        "gender_title": "🚻 <b>מין</b>",
        "language_title": "🌐 <b>שפת הממשק</b>",
        "timezone_title": "🌍 <b>אזור זמן</b>",
        "social_profile_title": "👤 <b>פרופיל חברתי</b>",
        "select_active_hours_start": "בחר את זמן תחילת התקופה הפעילה:",
        "select_active_hours_end": "עכשיו בחר את זמן הסיום:",
        "start_hour_set": "🕐 התחלה: {hour}:00",
        "how_often_ask": "כמה פעמים לשאול על הטוב?",
        "how_would_you_like": "איך זה נוח לך?",
        "current_value": "נוכחי: {value}",
        "select_gender_prompt": "בחר מין לפנייה נכונה:",
        "select_language_prompt": "בחר שפת ממשק:",
        "select_timezone_prompt": "בחר את האזור שלך:",
        "select_timezone_city": "בחר את אזור הזמן שלך:",
        "gender_male_value": "זכר",
        "gender_female_value": "נקבה",
        "gender_unknown": "לא צוין",
        "address_formal_value": "ב«אתם»",
        "address_informal_value": "ב«אתה»",
        "notifications_on": "מופעלות",
        "notifications_off": "כבויות",
        "notifications_toggled_on": "🔔 התראות מופעלות",
        "notifications_toggled_off": "🔔 התראות כבויות",
        "settings.active_hours_value": "🕐 שעות פעילות: {start} - {end}",
        "settings.interval_value": "⏰ מרווח: כל {interval} שעות.",
        "settings.timezone_value": "🌍 אזור זמן: {timezone}",
        "settings.formality_value": "🗣 פנייה: {formality}",
        "settings.notifications_value": "🔔 התראות: {status}",
        "every_n_hours": "כל {hours} שעות.",
        "interval_set_confirm": "✅ המרווח הוגדר: כל {hours} שעות.",
        "timezone_invalid": "❌ שגיאה: אזור זמן לא תקין",
        "timezone_set_confirm": "✅ אזור הזמן הוגדר: {timezone}",
        "settings_reset_title": "✅ <b>ההגדרות הוחזרו!</b>",
        "settings_reset_error": "😔 לא הצלחנו לאפס את ההגדרות. נסה שוב מאוחר יותר.",
        "social_add_prompt": "🔗 <b>הוסף רשת חברתית</b>\n\nשלח קישור לדף שלך ברשת החברתית.\n\nנתמכים:\n• אינסטגרם\n• פייסבוק\n• טוויטר/X\n• לינקדאין\n• ויקונטקטה\n• ערוץ טלגרם\n• יוטיוב\n• טיקטוק\n\nשלח /cancel כדי לבטל.",
        "social_bio_prompt": "📝 <b>עריכת ביוגרפיה</b>\n\nכתוב קצת על עצמך, תחביבים ועניינים.\nזה יעזור לי להבין אותך טוב יותר ולעשות את השיחה שלנו יותר אישית.\n\nשלח /cancel כדי לבטל.",
        "social_parsing": "🔍 מנתח את הפרופיל...",
        "social_interests_found": "✅ <b>תחומי עניין זוהו!</b>\n\nתחומי העניין שלך: {interests}\n\nמידע זה ישמש להתאמה אישית של השיחה שלנו.",
        "social_interests_failed": "❌ לא הצלחנו לזהות תחומי עניין.\n\nהוסף יותר מידע לפרופיל שלך: קישורים לרשתות חברתיות או ביוגרפיה.",
        "social_no_links": "אין לך רשתות חברתיות נוספות.",
        "social_remove_title": "🗑 <b>מחיקת קישור</b>\n\nבחר רשת חברתית למחיקה:",
        "moments_title": "📖 <b>הרגעים הטובים שלך</b>",
        "moments_empty": "📖 עדיין אין לך רגעים שמורים.\nכשיגיע זמן השאלה, שתף משהו טוב! 🌟",
        "random_moment_header": "🎲 <b>רגע טוב אקראי</b>",
        "moment_not_found": "😔 הרגע לא נמצא.",
        "moment_delete_title": "🗑️ <b>למחוק את הרגע?</b>",
        "moment_delete_warning": "⚠️ פעולה זו אינה הפיכה!",
        "moment_deleted_confirm": "✅ הרגע נמחק.",
        "moment_delete_error": "😔 לא הצלחנו למחוק את הרגע.",
        "no_moments_period": "📖 אין רגעים {period}.",
        "moments_period_title": "📖 <b>רגעים {period}</b>",
        "period_today": "היום",
        "period_week": "בשבוע",
        "period_month": "בחודש",
        "moments_pagination_next": "דף הבא",
        "moments_pagination_prev": "דף קודם",
        "dialog_intro": "💬 <b>מצב דיאלוג</b>\n\nאני מוכן להקשיב לך. ספר לי מה על ליבך. אנסה לעזור לך מנקודת מבט חיצונית, אבל זכור — כל ההחלטות הן שלך. 💝\n\nכדי לצאת ממצב הדיאלוג, לחץ על הכפתור למטה.",
        "dialog_exit_confirm": "חזרנו למצב הרגיל. איך אני יכול לעזור? 😊",
        "main_menu_prompt": "איך אני יכול לעזור? 😊",
        "data_deleted": "✅ כל הנתונים שלך נמחקו.\n\nאם תרצה לחזור — פשוט כתוב /start 💝",
        "data_delete_error": "😔 אירעה שגיאה במחקה. נסה שוב מאוחר יותר.",
        "delete_cancelled": "👍 המחיקה בוטלה. הנתונים שלך בטוחים!",
        "question_skipped": "👍 בסדר, נדלג על השאלה הזו. נתראה בקרוב! 😊",
        "summary_title": "📊 <b>סיכום רגעים</b>",
        "summary_generating_weekly": "⏳ מכין סיכום שבועי...",
        "summary_generating_monthly": "⏳ מכין סיכום חודשי...",
        "summary_not_enough_weekly": "📅 אין מספיק רגעים לסיכום שבועי.\n\nכשיהיו לך יותר רשומות, אוכל ליצור סקירה יפה! 🌟",
        "summary_not_enough_monthly": "🗓 אין מספיק רגעים לסיכום חודשי.\n\nכשיהיו לך יותר רשומות, אוכל ליצור סקירה יפה! 🌟",
        "stats_empty": "📊 הסטטיסטיקה עדיין לא זמינה.\nהתחל לענות על שאלות, וכאן יופיע ההתקדמות שלך! ✨",
        "question_1_informal": "מה טוב קרה היום? 🌟",
        "question_2_informal": "ספר לי, מה שימח אותך? ✨",
        "question_3_informal": "מה נעים קרה? 😊",
        "question_4_informal": "איזה רגע היה מיוחד היום? 💫",
        "question_5_informal": "מה נתן לך השראה היום? 🌈",
        "question_6_informal": "ספר על שמחה קטנה של היום! 💝",
        "question_7_informal": "מה טוב שמת לב אליו היום? 🌻",
        "question_8_informal": "למה חייכת היום? 😄",
        "question_1_formal": "מה טוב קרה היום? 🌟",
        "question_2_formal": "ספרו לי, מה שימח אתכם? ✨",
        "question_3_formal": "מה נעים קרה? 😊",
        "question_4_formal": "איזה רגע היה מיוחד היום? 💫",
        "question_5_formal": "מה נתן לכם השראה היום? 🌈",
        "question_6_formal": "ספרו על שמחה קטנה של היום! 💝",
        "question_7_formal": "מה טוב ששמתם לב אליו היום? 🌻",
        "question_8_formal": "למה חייכתם היום? 😄",
        "please_start_first": "אנא הפעל את הבוט קודם עם הפקודה /start",
    },
    "ja": {
        "saved": "保存されました！",
        "error": "エラー",
        "success": "成功！",
        "cancelled": "キャンセルされました",
        "loading": "読み込み中...",
        "active_hours_set": "アクティブ時間が設定されました: {start} - {end}",
        "interval_set": "通知の間隔: {interval}",
        "timezone_set": "タイムゾーンが設定されました: {timezone}",
        "notifications_enabled": "🔔 通知が有効になりました",
        "notifications_disabled": "🔕 通知が無効になりました",
        "settings_reset": "設定がデフォルト値にリセットされました",
        "language_changed": "言語がロシア語に変更されました",
        "address_changed_informal": "「君」と呼びますね",
        "address_changed_formal": "「あなた」と呼びますね",
        "gender_set_male": "性別が設定されました: 男性",
        "gender_set_female": "性別が設定されました: 女性",
        "no_moments": "まだ保存された瞬間がありません。今日良いことがあったら教えてください！",
        "no_moments_formal": "まだ保存された瞬間がありません。今日良いことがあったら教えてください！",
        "moment_deleted": "瞬間が削除されました",
        "moments_count": "見つかった瞬間: {count}",
        "random_moment_title": "🎲 ランダムな楽しい瞬間:",
        "stats_title": "📊 あなたの統計",
        "stats_title_formal": "📊 あなたの統計",
        "stats_total_moments": "合計瞬間: {count}",
        "stats_current_streak": "現在の連続日数: {days} 日",
        "stats_longest_streak": "最高の連続日数: {days} 日",
        "stats_response_rate": "回答率: {rate}%",
        "stats_not_available": "統計はまだ利用できません",
        "dialog_started": "💬 ダイアログモード。あなたの話を聞いています。「終了」と書くか、ボタンを押して終了してください。",
        "dialog_started_formal": "💬 ダイアログモード。あなたの話を聞いています。「終了」と書くか、ボタンを押して終了してください。",
        "dialog_ended": "ダイアログが終了しました。メインメニューに戻ります。",
        "pause_title": "⏸ <b>ボットを一時停止</b>",
        "pause_title_formal": "⏸ <b>ボットを一時停止</b>",
        "pause_select_period": "メッセージ送信をどの期間一時停止しますか？",
        "pause_select_period_formal": "メッセージ送信をどの期間一時停止しますか？",
        "pause_day": "📅 1日間",
        "pause_week": "📅 1週間",
        "pause_two_weeks": "📅 2週間",
        "pause_cancel": "⬅️ キャンセル",
        "pause_confirmed": "✅ ボットは {date} まで一時停止されました。それまでメッセージを送信しません。メッセージを送信すると、通知は自動的に再開されます。",
        "pause_confirmed_formal": "✅ ボットは {date} まで一時停止されました。それまでメッセージを送信しません。メッセージを送信すると、通知は自動的に再開されます。",
        "pause_resumed": "✅ 通知が再開されました！",
        "pause_resumed_formal": "✅ 通知が再開されました！",
        "social_profile_updated": "プロフィールが更新されました",
        "social_link_removed": "リンクが削除されました",
        "social_profile_not_configured": "ソーシャルプロフィールが設定されていません",
        "social_profile_empty": "ソーシャルプロフィールが空です。ソーシャルネットワークのリンクまたはバイオを追加してください。",
        "social_networks_label": "<b>ソーシャルネットワーク:</b>",
        "about_me_label": "<b>自己紹介:</b>",
        "interests_label": "<b>興味:</b>",
        "profile_not_found": "プロフィールが見つかりません",
        "user_not_found": "ユーザーが見つかりません",
        "enter_social_link": "あなたのソーシャルメディアプロフィールのリンクを送ってください:",
        "enter_social_link_formal": "あなたのソーシャルメディアプロフィールのリンクを送ってください:",
        "enter_bio": "自分について少し教えてください（趣味、興味など）:",
        "enter_bio_formal": "自分について少し教えてください（趣味、興味など）:",
        "interests_detected": "✨ 興味が特定されました: {interests}",
        "feedback_prompt": "あなたの提案やアイデアを書いてください:",
        "feedback_prompt_formal": "あなたの提案やアイデアを書いてください:",
        "feedback_sent": "フィードバックありがとうございます！ 💝",
        "feedback_category": "カテゴリー: {category}",
        "help_title": "📋 利用可能なコマンド:",
        "help_start": "/start - 最初から始める",
        "help_help": "/help - ヘルプを表示",
        "help_settings": "/settings - 設定",
        "help_stats": "/stats - 統計",
        "help_privacy": "/privacy - プライバシーポリシー",
        "help_export": "/export_data - データをエクスポート",
        "help_delete": "/delete_data - データを削除",
        "privacy_title": "🔒 プライバシーポリシー",
        "privacy_text": "私たちはあなたのプライバシーを真剣に考えています。\n\n📌 私たちが保存するデータ:\n• ボットへの質問に対するあなたの回答\n• 設定（タイムゾーン、言語、間隔）\n• Telegramプロフィールからの基本情報\n\n🔐 データの使用方法:\n• あなたの体験をパーソナライズするためだけ\n• 良い瞬間を思い出させるため\n• データは第三者に提供されません\n\n🗑 あなたの権利:\n• /export_data - すべてのデータをエクスポート\n• /delete_data - すべてのデータを削除",
        "export_confirm": "すべてのデータをエクスポートしますか？",
        "export_confirm_formal": "すべてのデータをエクスポートしますか？",
        "export_success": "データがエクスポートされました",
        "delete_confirm": "⚠️ 注意！この操作はあなたのすべてのデータを永久に削除します。続行しますか？",
        "delete_confirm_formal": "⚠️ 注意！この操作はあなたのすべてのデータを永久に削除します。続行しますか？",
        "delete_success": "すべてのデータが削除されました。さようなら！ 👋",
        "delete_data_title": "⚠️ <b>データ削除</b>",
        "delete_data_confirm": "ボットのデータベースからすべてのデータを削除してもよろしいですか？",
        "delete_data_confirm_formal": "ボットのデータベースからすべてのデータを削除してもよろしいですか？",
        "delete_data_warning": "この操作でボットのデータベースから削除されます：",
        "delete_data_warning_formal": "この操作でボットのデータベースから削除されます：",
        "delete_data_moments": "• すべての瞬間",
        "delete_data_moments_formal": "• すべての瞬間",
        "delete_data_conversations": "• 会話履歴",
        "delete_data_stats": "• 統計",
        "delete_data_settings": "• 設定",
        "delete_data_irreversible": "⚠️ <b>この操作は取り消せません！</b>",
        "delete_data_chat_note": "ℹ️ <i>デバイスのチャット履歴は残ります。削除されるのはボットのデータベースのデータのみです。</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>デバイスのチャット履歴は残ります。削除されるのはボットのデータベースのデータのみです。</i>",
        "timezone_select_region": "地域を選んでください:",
        "timezone_select_region_formal": "地域を選んでください:",
        "select_start_hour": "アクティブ時間の開始を選んでください:",
        "select_start_hour_formal": "アクティブ時間の開始を選んでください:",
        "select_end_hour": "アクティブ時間の終了を選んでください:",
        "select_end_hour_formal": "アクティブ時間の終了を選んでください:",
        "current_settings": "⚙️ 現在の設定:\n\n🕐 アクティブ時間: {start_hour}:00 - {end_hour}:00\n⏰ 間隔: {interval}\n🌍 タイムゾーン: {timezone}\n🗣 呼称: {address}\n🚻 性別: {gender}\n🔔 通知: {notifications}\n🌐 言語: {language}",
        "settings_title": "⚙️ <b>設定</b>",
        "active_hours_title": "🕐 <b>アクティブ時間</b>",
        "interval_title": "⏰ <b>質問間の間隔</b>",
        "address_form_title": "🗣 <b>呼称の形式</b>",
        "gender_title": "🚻 <b>性別</b>",
        "language_title": "🌐 <b>インターフェースの言語</b>",
        "timezone_title": "🌍 <b>タイムゾーン</b>",
        "social_profile_title": "👤 <b>ソーシャルプロフィール</b>",
        "select_active_hours_start": "アクティブ期間の開始時間を選んでください:",
        "select_active_hours_end": "次に終了時間を選んでください:",
        "start_hour_set": "🕐 開始: {hour}:00",
        "how_often_ask": "どのくらいの頻度で良いことを尋ねますか？",
        "how_would_you_like": "どのようにしたいですか？",
        "current_value": "現在の値: {value}",
        "select_gender_prompt": "正しい呼称のために性別を選んでください:",
        "select_language_prompt": "インターフェースの言語を選んでください:",
        "select_timezone_prompt": "自分の地域を選んでください:",
        "select_timezone_city": "自分のタイムゾーンを選んでください:",
        "gender_male_value": "男性",
        "gender_female_value": "女性",
        "gender_unknown": "指定されていません",
        "address_formal_value": "「あなた」と呼ぶ",
        "address_informal_value": "「君」と呼ぶ",
        "notifications_on": "有効",
        "notifications_off": "無効",
        "notifications_toggled_on": "🔔 通知が有効になりました",
        "notifications_toggled_off": "🔔 通知が無効になりました",
        "settings.active_hours_value": "🕐 アクティブ時間: {start} - {end}",
        "settings.interval_value": "⏰ 間隔: {hours} 時間ごと",
        "settings.timezone_value": "🌍 タイムゾーン: {timezone}",
        "settings.formality_value": "🗣 呼称: {formality}",
        "settings.notifications_value": "🔔 通知: {status}",
        "every_n_hours": "{hours} 時間ごと",
        "interval_set_confirm": "✅ 間隔が設定されました: {hours} 時間ごと。",
        "timezone_invalid": "❌ エラー: 無効なタイムゾーン",
        "timezone_set_confirm": "✅ タイムゾーンが設定されました: {timezone}",
        "settings_reset_title": "✅ <b>設定がリセットされました！</b>",
        "settings_reset_error": "😔 設定のリセットに失敗しました。後で再試行してください。",
        "social_add_prompt": "🔗 <b>ソーシャルネットワークを追加</b>\n\nあなたのソーシャルメディアページのリンクを送ってください。\n\nサポートされている:\n• Instagram\n• Facebook\n• Twitter/X\n• LinkedIn\n• VKontakte\n• Telegramチャンネル\n• YouTube\n• TikTok\n\nキャンセルするには /cancel を送ってください。",
        "social_bio_prompt": "📝 <b>プロフィール編集</b>\n\n自分について少し書いてください。趣味や興味など。\nこれにより、あなたをよりよく理解し、私たちのコミュニケーションをよりパーソナルにすることができます。\n\nキャンセルするには /cancel を送ってください。",
        "social_parsing": "🔍 プロフィールを分析中...",
        "social_interests_found": "✅ <b>興味が特定されました！</b>\n\nあなたの興味: {interests}\n\nこの情報は、私たちのコミュニケーションをパーソナライズするために使用されます。",
        "social_interests_failed": "❌ 興味を特定できませんでした。\n\nソーシャルメディアのリンクやプロフィールを追加してください。",
        "social_no_links": "追加されたソーシャルメディアがありません。",
        "social_remove_title": "🗑 <b>リンクを削除</b>\n\n削除するソーシャルメディアを選んでください:",
        "moments_title": "📖 <b>あなたの良い瞬間</b>",
        "moments_empty": "📖 まだ保存された瞬間がありません。\n質問の時間が来たら、何か良いことを共有してください！ 🌟",
        "random_moment_header": "🎲 <b>ランダムな良い瞬間</b>",
        "moment_not_found": "😔 瞬間が見つかりませんでした。",
        "moment_delete_title": "🗑️ <b>瞬間を削除しますか？</b>",
        "moment_delete_warning": "⚠️ この操作は元に戻せません！",
        "moment_deleted_confirm": "✅ 瞬間が削除されました。",
        "moment_delete_error": "😔 瞬間を削除できませんでした。",
        "no_moments_period": "📖 瞬間がありません {period}。",
        "moments_period_title": "📖 <b>瞬間 {period}</b>",
        "period_today": "今日",
        "period_week": "今週",
        "period_month": "今月",
        "moments_pagination_next": "次のページ",
        "moments_pagination_prev": "前のページ",
        "dialog_intro": "💬 <b>ダイアログモード</b>\n\nあなたの話を聞く準備ができています。あなたの心の中のことを教えてください。私は外からの視点で助けようとしますが、すべての決定はあなた自身が行うことを忘れないでください。 💝\n\nダイアログモードを終了するには、下のボタンを押してください。",
        "dialog_exit_confirm": "通常モードに戻りました。何かお手伝いできることはありますか？ 😊",
        "main_menu_prompt": "何かお手伝いできることはありますか？ 😊",
        "data_deleted": "✅ あなたのすべてのデータが削除されました。\n\n戻りたい場合は、単に /start と書いてください 💝",
        "data_delete_error": "😔 削除中にエラーが発生しました。後で再試行してください。",
        "delete_cancelled": "👍 削除がキャンセルされました。あなたのデータは安全です！",
        "question_skipped": "👍 わかりました、この質問はスキップしましょう。またお会いしましょう！ 😊",
        "summary_title": "📊 <b>瞬間のサマリー</b>",
        "summary_generating_weekly": "⏳ 週次サマリーを作成中...",
        "summary_generating_monthly": "⏳ 月次サマリーを作成中...",
        "summary_not_enough_weekly": "📅 週次サマリーに十分な瞬間がありません。\n\nもっと記録が増えたら、素敵なレビューを作成できます！ 🌟",
        "summary_not_enough_monthly": "🗓 月次サマリーに十分な瞬間がありません。\n\nもっと記録が増えたら、素敵なレビューを作成できます！ 🌟",
        "stats_empty": "📊 統計はまだ利用できません。\n質問に答え始めると、ここにあなたの進捗が表示されます！ ✨",
        "question_1_informal": "今日いいことはあった？ 🌟",
        "question_2_informal": "教えて、何が嬉しかった？ ✨",
        "question_3_informal": "今日何か嬉しいことあった？ 😊",
        "question_4_informal": "今日いちばんよかった瞬間は？ 💫",
        "question_5_informal": "今日やる気が出たこと、何だった？ 🌈",
        "question_6_informal": "今日の小さな喜びを教えて！ 💝",
        "question_7_informal": "今日いいなと思ったこと、何かあった？ 🌻",
        "question_8_informal": "今日何に笑った？ 😄",
        "question_1_formal": "今日いいことはありましたか？ 🌟",
        "question_2_formal": "教えてください、何が嬉しかったですか？ ✨",
        "question_3_formal": "今日何か嬉しいことはありましたか？ 😊",
        "question_4_formal": "今日いちばんよかった瞬間は何ですか？ 💫",
        "question_5_formal": "今日やる気が出たことは何でしたか？ 🌈",
        "question_6_formal": "今日の小さな喜びを教えてください！ 💝",
        "question_7_formal": "今日いいなと思ったことはありますか？ 🌻",
        "question_8_formal": "今日何に笑いましたか？ 😄",
        "please_start_first": "まずは /start コマンドでボットを起動してください",
    },
    "zh": {
        "saved": "已保存！",
        "error": "错误",
        "success": "成功！",
        "cancelled": "已取消",
        "loading": "加载中...",
        "active_hours_set": "活动时间已设置：{start} - {end}",
        "interval_set": "通知间隔：{interval}",
        "timezone_set": "时区已设置：{timezone}",
        "notifications_enabled": "🔔 通知已开启",
        "notifications_disabled": "🔕 通知已关闭",
        "settings_reset": "设置已重置为默认值",
        "language_changed": "语言已更改为俄语",
        "address_changed_informal": "我会用“你”来称呼你",
        "address_changed_formal": "我会用“您”来称呼您",
        "gender_set_male": "性别已设置：男性",
        "gender_set_female": "性别已设置：女性",
        "no_moments": "你还没有保存的时刻。告诉我今天发生了什么好事！",
        "no_moments_formal": "您还没有保存的时刻。请告诉我今天发生了什么好事！",
        "moment_deleted": "时刻已删除",
        "moments_count": "找到的时刻：{count}",
        "random_moment_title": "🎲 随机快乐时刻：",
        "stats_title": "📊 你的统计数据",
        "stats_title_formal": "📊 您的统计数据",
        "stats_total_moments": "总时刻：{count}",
        "stats_current_streak": "当前连续天数：{days} 天",
        "stats_longest_streak": "最长连续天数：{days} 天",
        "stats_response_rate": "回复率：{rate}%",
        "stats_not_available": "统计数据暂时不可用",
        "dialog_started": "💬 对话模式。我在听你说。输入“退出”或点击按钮以退出。",
        "dialog_started_formal": "💬 对话模式。我在听您说。请写“退出”或点击按钮以退出。",
        "dialog_ended": "对话结束。返回主菜单。",
        "pause_title": "⏸ <b>暂停机器人</b>",
        "pause_title_formal": "⏸ <b>暂停机器人</b>",
        "pause_select_period": "暂停发送消息多长时间？",
        "pause_select_period_formal": "暂停发送消息多长时间？",
        "pause_day": "📅 1天",
        "pause_week": "📅 1周",
        "pause_two_weeks": "📅 2周",
        "pause_cancel": "⬅️ 取消",
        "pause_confirmed": "✅ 机器人已暂停至 {date}。在此之前我不会向您发送消息。如果您给我发消息，通知将自动恢复。",
        "pause_confirmed_formal": "✅ 机器人已暂停至 {date}。在此之前我不会向您发送消息。如果您给我发消息，通知将自动恢复。",
        "pause_resumed": "✅ 通知已恢复！",
        "pause_resumed_formal": "✅ 通知已恢复！",
        "social_profile_updated": "个人资料已更新",
        "social_link_removed": "链接已删除",
        "social_profile_not_configured": "社交资料未设置",
        "social_profile_empty": "社交资料为空。请添加社交媒体链接或个人简介。",
        "social_networks_label": "<b>社交媒体：</b>",
        "about_me_label": "<b>关于我：</b>",
        "interests_label": "<b>兴趣：</b>",
        "profile_not_found": "未找到资料",
        "user_not_found": "未找到用户",
        "enter_social_link": "发送您的社交媒体个人资料链接：",
        "enter_social_link_formal": "发送您的社交媒体个人资料链接：",
        "enter_bio": "简单介绍一下自己（兴趣，爱好）：",
        "enter_bio_formal": "简单介绍一下自己（兴趣，爱好）：",
        "interests_detected": "✨ 识别到的兴趣：{interests}",
        "feedback_prompt": "写下你的建议或想法：",
        "feedback_prompt_formal": "写下您的建议或想法：",
        "feedback_sent": "感谢您的反馈！💝",
        "feedback_category": "类别：{category}",
        "help_title": "📋 可用命令：",
        "help_start": "/start - 从头开始",
        "help_help": "/help - 显示帮助",
        "help_settings": "/settings - 设置",
        "help_stats": "/stats - 统计",
        "help_privacy": "/privacy - 隐私政策",
        "help_export": "/export_data - 导出数据",
        "help_delete": "/delete_data - 删除数据",
        "privacy_title": "🔒 隐私政策",
        "privacy_text": "我们非常重视您的隐私。\n\n📌 我们存储的数据：\n• 您对机器人的回答\n• 设置（时区，语言，间隔）\n• Telegram 个人资料中的基本信息\n\n🔐 我们如何使用数据：\n• 仅用于个性化您的体验\n• 用于提醒美好时刻\n• 数据不会传递给第三方\n\n🗑 您的权利：\n• /export_data - 导出所有数据\n• /delete_data - 删除所有数据",
        "export_confirm": "导出所有你的数据？",
        "export_confirm_formal": "导出所有您的数据？",
        "export_success": "数据已导出",
        "delete_confirm": "⚠️ 注意！此操作将永久删除您所有的数据。继续吗？",
        "delete_confirm_formal": "⚠️ 注意！此操作将永久删除您所有的数据。继续吗？",
        "delete_success": "所有数据已删除。再见！👋",
        "delete_data_title": "⚠️ <b>删除数据</b>",
        "delete_data_confirm": "你确定要从机器人数据库中删除你的全部数据吗？",
        "delete_data_confirm_formal": "您确定要从机器人数据库中删除您的全部数据吗？",
        "delete_data_warning": "此操作将从机器人数据库中删除：",
        "delete_data_warning_formal": "此操作将从机器人数据库中删除：",
        "delete_data_moments": "• 你的所有时刻",
        "delete_data_moments_formal": "• 您的所有时刻",
        "delete_data_conversations": "• 对话历史",
        "delete_data_stats": "• 统计数据",
        "delete_data_settings": "• 设置",
        "delete_data_irreversible": "⚠️ <b>此操作不可逆！</b>",
        "delete_data_chat_note": "ℹ️ <i>说明：本聊天在你设备上的记录会保留。仅删除机器人数据库中的数据。</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>说明：本聊天在您设备上的记录会保留。仅删除机器人数据库中的数据。</i>",
        "timezone_select_region": "选择地区：",
        "timezone_select_region_formal": "选择地区：",
        "select_start_hour": "选择活动时间开始：",
        "select_start_hour_formal": "选择活动时间开始：",
        "select_end_hour": "选择活动时间结束：",
        "select_end_hour_formal": "选择活动时间结束：",
        "current_settings": "⚙️ 当前设置：\n\n🕐 活动时间：{start_hour}:00 - {end_hour}:00\n⏰ 间隔：{interval}\n🌍 时区：{timezone}\n🗣 称呼：{address}\n🚻 性别：{gender}\n🔔 通知：{notifications}\n🌐 语言：{language}",
        "settings_title": "⚙️ <b>设置</b>",
        "active_hours_title": "🕐 <b>活动时间</b>",
        "interval_title": "⏰ <b>问题间隔</b>",
        "address_form_title": "🗣 <b>称呼形式</b>",
        "gender_title": "🚻 <b>性别</b>",
        "language_title": "🌐 <b>界面语言</b>",
        "timezone_title": "🌍 <b>时区</b>",
        "social_profile_title": "👤 <b>社交资料</b>",
        "select_active_hours_start": "选择活动时间开始：",
        "select_active_hours_end": "现在选择活动时间结束：",
        "start_hour_set": "🕐 开始：{hour}:00",
        "how_often_ask": "我多久问一次好事？",
        "how_would_you_like": "你觉得哪个更方便？",
        "current_value": "当前：{value}",
        "select_gender_prompt": "选择性别以便正确称呼：",
        "select_language_prompt": "选择界面语言：",
        "select_timezone_prompt": "选择您的地区：",
        "select_timezone_city": "选择您的时区：",
        "gender_male_value": "男性",
        "gender_female_value": "女性",
        "gender_unknown": "未指定",
        "address_formal_value": "用“您”",
        "address_informal_value": "用“你”",
        "notifications_on": "已开启",
        "notifications_off": "已关闭",
        "notifications_toggled_on": "🔔 通知已开启",
        "notifications_toggled_off": "🔔 通知已关闭",
        "settings.active_hours_value": "🕐 活动时间：{start} - {end}",
        "settings.interval_value": "⏰ 间隔：每 {interval} 小时。",
        "settings.timezone_value": "🌍 时区：{timezone}",
        "settings.formality_value": "🗣 称呼：{formality}",
        "settings.notifications_value": "🔔 通知：{status}",
        "every_n_hours": "每 {hours} 小时。",
        "interval_set_confirm": "✅ 间隔已设置：每 {hours} 小时。",
        "timezone_invalid": "❌ 错误：无效的时区",
        "timezone_set_confirm": "✅ 时区已设置：{timezone}",
        "settings_reset_title": "✅ <b>设置已重置！</b>",
        "settings_reset_error": "😔 无法重置设置。请稍后再试。",
        "social_add_prompt": "🔗 <b>添加社交媒体</b>\n\n发送您的社交媒体页面链接。\n\n支持：\n• Instagram\n• Facebook\n• Twitter/X\n• LinkedIn\n• VK\n• Telegram 频道\n• YouTube\n• TikTok\n\n发送 /cancel 以取消。",
        "social_bio_prompt": "📝 <b>编辑个人简介</b>\n\n写下关于自己、兴趣和爱好的信息。\n这将帮助我更好地了解您，使我们的交流更加个性化。\n\n发送 /cancel 以取消。",
        "social_parsing": "🔍 正在分析个人资料...",
        "social_interests_found": "✅ <b>兴趣已识别！</b>\n\n你的兴趣：{interests}\n\n这些信息将用于个性化我们的交流。",
        "social_interests_failed": "❌ 无法识别兴趣。\n\n请在您的个人资料中添加更多信息：社交媒体链接或个人简介。",
        "social_no_links": "您没有添加的社交媒体。",
        "social_remove_title": "🗑 <b>删除链接</b>\n\n选择要删除的社交媒体：",
        "moments_title": "📖 <b>你的美好时刻</b>",
        "moments_empty": "📖 你还没有保存的时刻。\n当提问时间到时，分享一些美好的事情！🌟",
        "random_moment_header": "🎲 <b>随机美好时刻</b>",
        "moment_not_found": "😔 时刻未找到。",
        "moment_delete_title": "🗑️ <b>删除时刻？</b>",
        "moment_delete_warning": "⚠️ 此操作不可逆！",
        "moment_deleted_confirm": "✅ 时刻已删除。",
        "moment_delete_error": "😔 无法删除时刻。",
        "no_moments_period": "📖 没有时刻 {period}。",
        "moments_period_title": "📖 <b>时刻 {period}</b>",
        "period_today": "今天",
        "period_week": "一周内",
        "period_month": "一个月内",
        "moments_pagination_next": "下一页",
        "moments_pagination_prev": "上一页",
        "dialog_intro": "💬 <b>对话模式</b>\n\n我准备好倾听你。告诉我你的心声。我会尽量提供外部的视角，但请记住——所有的决定由你自己做。💝\n\n要退出对话模式，请点击下面的按钮。",
        "dialog_exit_confirm": "返回常规模式。我能帮您什么？😊",
        "main_menu_prompt": "我能帮您什么？😊",
        "data_deleted": "✅ 您的所有数据已删除。\n\n如果您想回来——只需输入 /start 💝",
        "data_delete_error": "😔 删除时发生错误。请稍后再试。",
        "delete_cancelled": "👍 删除已取消。您的数据安全！",
        "question_skipped": "👍 好的，我们跳过这个问题。期待再见！😊",
        "summary_title": "📊 <b>时刻总结</b>",
        "summary_generating_weekly": "⏳ 正在准备每周总结...",
        "summary_generating_monthly": "⏳ 正在准备每月总结...",
        "summary_not_enough_weekly": "📅 每周总结的时刻不足。\n\n当您有更多记录时，我将能够创建一个漂亮的概述！🌟",
        "summary_not_enough_monthly": "🗓 每月总结的时刻不足。\n\n当您有更多记录时，我将能够创建一个漂亮的概述！🌟",
        "stats_empty": "📊 统计数据暂时不可用。\n开始回答问题，这里将显示您的进展！✨",
        "question_1_informal": "今天有什么好事？ 🌟",
        "question_2_informal": "说说看，什么让你开心？ ✨",
        "question_3_informal": "今天有什么开心事？ 😊",
        "question_4_informal": "今天最特别的时刻是？ 💫",
        "question_5_informal": "今天什么给了你灵感？ 🌈",
        "question_6_informal": "分享今天的一个小确幸吧！ 💝",
        "question_7_informal": "今天你留意到什么好事？ 🌻",
        "question_8_informal": "今天为什么笑了？ 😄",
        "question_1_formal": "今天有什么好事？ 🌟",
        "question_2_formal": "请说说，什么让您开心？ ✨",
        "question_3_formal": "今天有什么开心事？ 😊",
        "question_4_formal": "今天最特别的时刻是什么？ 💫",
        "question_5_formal": "今天什么给了您灵感？ 🌈",
        "question_6_formal": "请分享今天的一个小确幸！ 💝",
        "question_7_formal": "今天您留意到什么好事？ 🌻",
        "question_8_formal": "今天为什么笑了？ 😄",
        "please_start_first": "请先通过 /start 启动机器人",
    },
    "it": {
        "saved": "Salvato!",
        "error": "Errore",
        "success": "Successo!",
        "cancelled": "Annullato",
        "loading": "Caricamento...",
        "active_hours_set": "Ore attive impostate: {start} - {end}",
        "interval_set": "Intervallo di notifiche: {interval}",
        "timezone_set": "Fuso orario impostato: {timezone}",
        "notifications_enabled": "🔔 Notifiche attivate",
        "notifications_disabled": "🔕 Notifiche disattivate",
        "settings_reset": "Impostazioni ripristinate ai valori predefiniti",
        "language_changed": "Lingua cambiata in russo",
        "address_changed_informal": "Ti parlerò con «tu»",
        "address_changed_formal": "Ti parlerò con «Lei»",
        "gender_set_male": "Genere impostato: maschile",
        "gender_set_female": "Genere impostato: femminile",
        "no_moments": "Non hai ancora momenti salvati. Raccontami cosa di buono è successo oggi!",
        "no_moments_formal": "Non ha ancora momenti salvati. Racconti cosa di buono è successo oggi!",
        "moment_deleted": "Momento eliminato",
        "moments_count": "Momenti trovati: {count}",
        "random_moment_title": "🎲 Momento felice casuale:",
        "stats_title": "📊 La tua statistica",
        "stats_title_formal": "📊 La Sua statistica",
        "stats_total_moments": "Totale momenti: {count}",
        "stats_current_streak": "Serie attuale: {days} giorni",
        "stats_longest_streak": "Migliore serie: {days} giorni",
        "stats_response_rate": "Percentuale di risposte: {rate}%",
        "stats_not_available": "Statistiche non disponibili per ora",
        "dialog_started": "💬 Modalità dialogo. Ti ascolto. Scrivi «uscita» o premi il pulsante per uscire.",
        "dialog_started_formal": "💬 Modalità dialogo. La ascolto. Scriva «uscita» o premi il pulsante per uscire.",
        "dialog_ended": "Dialogo terminato. Torno al menu principale.",
        "pause_title": "⏸ <b>Pausa bot</b>",
        "pause_title_formal": "⏸ <b>Pausa bot</b>",
        "pause_select_period": "Per quanto tempo vuoi sospendere l'invio di messaggi?",
        "pause_select_period_formal": "Per quanto tempo vuole sospendere l'invio di messaggi?",
        "pause_day": "📅 Per 1 giorno",
        "pause_week": "📅 Per 1 settimana",
        "pause_two_weeks": "📅 Per 2 settimane",
        "pause_cancel": "⬅️ Annulla",
        "pause_confirmed": "✅ Bot in pausa fino al {date}. Non ti invierò messaggi fino a quel momento. Se mi scrivi, le notifiche riprenderanno automaticamente.",
        "pause_confirmed_formal": "✅ Bot in pausa fino al {date}. Non Le invierò messaggi fino a quel momento. Se mi scrive, le notifiche riprenderanno automaticamente.",
        "pause_resumed": "✅ Notifiche riprese!",
        "pause_resumed_formal": "✅ Notifiche riprese!",
        "social_profile_updated": "Profilo aggiornato",
        "social_link_removed": "Link rimosso",
        "social_profile_not_configured": "Profilo sociale non configurato",
        "social_profile_empty": "Profilo sociale vuoto. Aggiungi link ai social o una bio.",
        "social_networks_label": "<b>Reti sociali:</b>",
        "about_me_label": "<b>Chi sono:</b>",
        "interests_label": "<b>Interessi:</b>",
        "profile_not_found": "Profilo non trovato",
        "user_not_found": "Utente non trovato",
        "enter_social_link": "Invia il link al tuo profilo sui social:",
        "enter_social_link_formal": "Invii il link al Suo profilo sui social:",
        "enter_bio": "Raccontami un po' di te (hobby, interessi):",
        "enter_bio_formal": "Racconti un po' di sé (hobby, interessi):",
        "interests_detected": "✨ Interessi rilevati: {interests}",
        "feedback_prompt": "Scrivi la tua proposta o idea:",
        "feedback_prompt_formal": "Scriva la Sua proposta o idea:",
        "feedback_sent": "Grazie per il feedback! 💝",
        "feedback_category": "Categoria: {category}",
        "help_title": "📋 Comandi disponibili:",
        "help_start": "/start - Iniziare da capo",
        "help_help": "/help - Mostrare aiuto",
        "help_settings": "/settings - Impostazioni",
        "help_stats": "/stats - Statistiche",
        "help_privacy": "/privacy - Politica sulla privacy",
        "help_export": "/export_data - Esportare dati",
        "help_delete": "/delete_data - Eliminare dati",
        "privacy_title": "🔒 Politica sulla privacy",
        "privacy_text": "Prendiamo sul serio la tua privacy.\n\n📌 Quali dati conserviamo:\n• Le tue risposte alle domande del bot\n• Impostazioni (fuso orario, lingua, intervallo)\n• Informazioni di base dal profilo Telegram\n\n🔐 Come utilizziamo i dati:\n• Solo per personalizzare la tua esperienza\n• Per ricordare i bei momenti\n• I dati non vengono condivisi con terze parti\n\n🗑 I tuoi diritti:\n• /export_data - esportare tutti i dati\n• /delete_data - eliminare tutti i dati",
        "export_confirm": "Esportare tutti i tuoi dati?",
        "export_confirm_formal": "Esportare tutti i Suoi dati?",
        "export_success": "Dati esportati",
        "delete_confirm": "⚠️ Attenzione! Questa azione eliminerà TUTTI i tuoi dati in modo irreversibile. Continuare?",
        "delete_confirm_formal": "⚠️ Attenzione! Questa azione eliminerà TUTTI i Suoi dati in modo irreversibile. Continuare?",
        "delete_success": "Tutti i dati eliminati. Arrivederci! 👋",
        "delete_data_title": "⚠️ <b>Eliminazione dati</b>",
        "delete_data_confirm": "Sei sicuro di voler eliminare TUTTI i tuoi dati dal database del bot?",
        "delete_data_confirm_formal": "È sicuro di voler eliminare TUTTI i Suoi dati dal database del bot?",
        "delete_data_warning": "Questa azione eliminerà dal database del bot:",
        "delete_data_warning_formal": "Questa azione eliminerà dal database del bot:",
        "delete_data_moments": "• Tutti i tuoi momenti",
        "delete_data_moments_formal": "• Tutti i Suoi momenti",
        "delete_data_conversations": "• La cronologia delle conversazioni",
        "delete_data_stats": "• Le statistiche",
        "delete_data_settings": "• Le impostazioni",
        "delete_data_irreversible": "⚠️ <b>Questa azione è irreversibile!</b>",
        "delete_data_chat_note": "ℹ️ <i>Nota: La cronologia della chat sul tuo dispositivo resterà. Verranno eliminati solo i dati dal database del bot.</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>Nota: La cronologia della chat sul Suo dispositivo resterà. Verranno eliminati solo i dati dal database del bot.</i>",
        "timezone_select_region": "Scegli la regione:",
        "timezone_select_region_formal": "Selezioni la regione:",
        "select_start_hour": "Scegli l'inizio delle ore attive:",
        "select_start_hour_formal": "Selezioni l'inizio delle ore attive:",
        "select_end_hour": "Scegli la fine delle ore attive:",
        "select_end_hour_formal": "Selezioni la fine delle ore attive:",
        "current_settings": "⚙️ Impostazioni attuali:\n\n🕐 Ore attive: {start_hour}:00 - {end_hour}:00\n⏰ Intervallo: {interval}\n🌍 Fuso orario: {timezone}\n🗣 Forma di indirizzo: {address}\n🚻 Genere: {gender}\n🔔 Notifiche: {notifications}\n🌐 Lingua: {language}",
        "settings_title": "⚙️ <b>Impostazioni</b>",
        "active_hours_title": "🕐 <b>Ore attive</b>",
        "interval_title": "⏰ <b>Intervallo tra le domande</b>",
        "address_form_title": "🗣 <b>Forma di indirizzo</b>",
        "gender_title": "🚻 <b>Genere</b>",
        "language_title": "🌐 <b>Lingua dell'interfaccia</b>",
        "timezone_title": "🌍 <b>Fuso orario</b>",
        "social_profile_title": "👤 <b>Profilo sociale</b>",
        "select_active_hours_start": "Scegli l'ora di inizio del periodo attivo:",
        "select_active_hours_end": "Ora scegli l'ora di fine:",
        "start_hour_set": "🕐 Inizio: {hour}:00",
        "how_often_ask": "Con quale frequenza dovrei chiedere del buono?",
        "how_would_you_like": "Come preferisci?",
        "current_value": "Attuale: {value}",
        "select_gender_prompt": "Scegli il genere per un corretto indirizzo:",
        "select_language_prompt": "Scegli la lingua dell'interfaccia:",
        "select_timezone_prompt": "Scegli la tua regione:",
        "select_timezone_city": "Scegli il tuo fuso orario:",
        "gender_male_value": "maschile",
        "gender_female_value": "femminile",
        "gender_unknown": "non specificato",
        "address_formal_value": "con «Lei»",
        "address_informal_value": "con «tu»",
        "notifications_on": "attivate",
        "notifications_off": "disattivate",
        "notifications_toggled_on": "🔔 Notifiche attivate",
        "notifications_toggled_off": "🔔 Notifiche disattivate",
        "settings.active_hours_value": "🕐 Ore attive: {start} - {end}",
        "settings.interval_value": "⏰ Intervallo: ogni {interval} ore.",
        "settings.timezone_value": "🌍 Fuso orario: {timezone}",
        "settings.formality_value": "🗣 Forma di indirizzo: {formality}",
        "settings.notifications_value": "🔔 Notifiche: {status}",
        "every_n_hours": "ogni {hours} ore.",
        "interval_set_confirm": "✅ Intervallo impostato: ogni {hours} ore.",
        "timezone_invalid": "❌ Errore: fuso orario non valido",
        "timezone_set_confirm": "✅ Fuso orario impostato: {timezone}",
        "settings_reset_title": "✅ <b>Impostazioni ripristinate!</b>",
        "settings_reset_error": "😔 Impossibile ripristinare le impostazioni. Riprova più tardi.",
        "social_add_prompt": "🔗 <b>Aggiungi social network</b>\n\nInvia il link alla tua pagina sui social.\n\nSupportati:\n• Instagram\n• Facebook\n• Twitter/X\n• LinkedIn\n• VKontakte\n• Canale Telegram\n• YouTube\n• TikTok\n\nInvia /cancel per annullare.",
        "social_bio_prompt": "📝 <b>Modifica biografia</b>\n\nScrivi un po' di te, dei tuoi hobby e interessi.\nQuesto mi aiuterà a capire meglio te e rendere la nostra comunicazione più personale.\n\nInvia /cancel per annullare.",
        "social_parsing": "🔍 Analizzando il profilo...",
        "social_interests_found": "✅ <b>Interessi rilevati!</b>\n\nI tuoi interessi: {interests}\n\nQueste informazioni saranno utilizzate per personalizzare la nostra comunicazione.",
        "social_interests_failed": "❌ Impossibile rilevare gli interessi.\n\nAggiungi più informazioni al tuo profilo: link ai social o biografia.",
        "social_no_links": "Non hai social aggiunti.",
        "social_remove_title": "🗑 <b>Rimuovere link</b>\n\nScegli il social da rimuovere:",
        "moments_title": "📖 <b>I tuoi bei momenti</b>",
        "moments_empty": "📖 Non hai ancora momenti salvati.\nQuando arriva il momento della domanda, condividi qualcosa di buono! 🌟",
        "random_moment_header": "🎲 <b>Momento buono casuale</b>",
        "moment_not_found": "😔 Momento non trovato.",
        "moment_delete_title": "🗑️ <b>Eliminare momento?</b>",
        "moment_delete_warning": "⚠️ Questa azione è irreversibile!",
        "moment_deleted_confirm": "✅ Momento eliminato.",
        "moment_delete_error": "😔 Impossibile eliminare il momento.",
        "no_moments_period": "📖 Nessun momento {period}.",
        "moments_period_title": "📖 <b>Momenti {period}</b>",
        "period_today": "oggi",
        "period_week": "questa settimana",
        "period_month": "questo mese",
        "moments_pagination_next": "Pagina successiva",
        "moments_pagination_prev": "Pagina precedente",
        "dialog_intro": "💬 <b>Modalità dialogo</b>\n\nSono pronto ad ascoltarti. Raccontami cosa hai nel cuore. Cercherò di aiutarti con una prospettiva esterna, ma ricorda — tutte le decisioni le prendi tu. 💝\n\nPer uscire dalla modalità dialogo, premi il pulsante qui sotto.",
        "dialog_exit_confirm": "Tornati alla modalità normale. Come posso aiutarti? 😊",
        "main_menu_prompt": "Come posso aiutarti? 😊",
        "data_deleted": "✅ Tutti i tuoi dati sono stati eliminati.\n\nSe vuoi tornare — scrivi semplicemente /start 💝",
        "data_delete_error": "😔 Si è verificato un errore durante l'eliminazione. Riprova più tardi.",
        "delete_cancelled": "👍 Eliminazione annullata. I tuoi dati sono al sicuro!",
        "question_skipped": "👍 Va bene, saltiamo questa domanda. A presto! 😊",
        "summary_title": "📊 <b>Riepilogo dei momenti</b>",
        "summary_generating_weekly": "⏳ Sto preparando il riepilogo settimanale...",
        "summary_generating_monthly": "⏳ Sto preparando il riepilogo mensile...",
        "summary_not_enough_weekly": "📅 Non ci sono abbastanza momenti per il riepilogo settimanale.\n\nQuando avrai più registrazioni, potrò creare una bella panoramica! 🌟",
        "summary_not_enough_monthly": "🗓 Non ci sono abbastanza momenti per il riepilogo mensile.\n\nQuando avrai più registrazioni, potrò creare una bella panoramica! 🌟",
        "stats_empty": "📊 Le statistiche non sono disponibili per ora.\nInizia a rispondere alle domande e qui apparirà il tuo progresso! ✨",
        "question_1_informal": "Cosa è andato bene oggi? 🌟",
        "question_2_informal": "Raccontami, cosa ti ha fatto felice? ✨",
        "question_3_informal": "Cosa di bello è successo oggi? 😊",
        "question_4_informal": "Quale momento di oggi è stato speciale? 💫",
        "question_5_informal": "Cosa ti ha ispirato oggi? 🌈",
        "question_6_informal": "Raccontami una piccola gioia di oggi! 💝",
        "question_7_informal": "Cosa di bello hai notato oggi? 🌻",
        "question_8_informal": "Per cosa hai sorriso oggi? 😄",
        "question_1_formal": "Cosa è andato bene oggi? 🌟",
        "question_2_formal": "Racconti, cosa La ha resa felice? ✨",
        "question_3_formal": "Cosa di bello è successo oggi? 😊",
        "question_4_formal": "Quale momento di oggi è stato speciale? 💫",
        "question_5_formal": "Cosa L'ha ispirata oggi? 🌈",
        "question_6_formal": "Racconti una piccola gioia di oggi! 💝",
        "question_7_formal": "Cosa di bello ha notato oggi? 🌻",
        "question_8_formal": "Per cosa ha sorriso oggi? 😄",
        "please_start_first": "Per favore, avvia prima il bot con il comando /start",
    },
    "pt": {
        "saved": "Salvo!",
        "error": "Erro",
        "success": "Sucesso!",
        "cancelled": "Cancelado",
        "loading": "Carregando...",
        "active_hours_set": "Horas ativas definidas: {start} - {end}",
        "interval_set": "Intervalo de notificações: {interval}",
        "timezone_set": "Fuso horário definido: {timezone}",
        "notifications_enabled": "🔔 Notificações ativadas",
        "notifications_disabled": "🔕 Notificações desativadas",
        "settings_reset": "Configurações redefinidas para os valores padrão",
        "language_changed": "Idioma alterado para português",
        "address_changed_informal": "Vou me referir a você como «tu»",
        "address_changed_formal": "Vou me referir ao senhor/a senhora como «você»",
        "gender_set_male": "Gênero definido: masculino",
        "gender_set_female": "Gênero definido: feminino",
        "no_moments": "Você ainda não tem momentos salvos. Conte-me algo bom que aconteceu hoje!",
        "no_moments_formal": "O senhor/a senhora ainda não tem momentos salvos. Conte-me algo bom que aconteceu hoje!",
        "moment_deleted": "Momento deletado",
        "moments_count": "Momentos encontrados: {count}",
        "random_moment_title": "🎲 Momento feliz aleatório:",
        "stats_title": "📊 Sua estatística",
        "stats_title_formal": "📊 Sua estatística",
        "stats_total_moments": "Total de momentos: {count}",
        "stats_current_streak": "Série atual: {days} dias.",
        "stats_longest_streak": "Melhor série: {days} dias.",
        "stats_response_rate": "Taxa de respostas: {rate}%",
        "stats_not_available": "Estatísticas ainda não disponíveis",
        "dialog_started": "💬 Modo de diálogo. Estou ouvindo você. Escreva «sair» ou pressione o botão para sair.",
        "dialog_started_formal": "💬 Modo de diálogo. Estou ouvindo o senhor/a senhora. Escreva «sair» ou pressione o botão para sair.",
        "dialog_ended": "Diálogo encerrado. Retornando ao menu principal.",
        "pause_title": "⏸ <b>Pausar bot</b>",
        "pause_title_formal": "⏸ <b>Pausar bot</b>",
        "pause_select_period": "Por quanto tempo deseja pausar o envio de mensagens?",
        "pause_select_period_formal": "Por quanto tempo deseja pausar o envio de mensagens?",
        "pause_day": "📅 Por 1 dia",
        "pause_week": "📅 Por 1 semana",
        "pause_two_weeks": "📅 Por 2 semanas",
        "pause_cancel": "⬅️ Cancelar",
        "pause_confirmed": "✅ Bot pausado até {date}. Não enviarei mensagens até então. Se você me enviar uma mensagem, as notificações serão retomadas automaticamente.",
        "pause_confirmed_formal": "✅ Bot pausado até {date}. Não enviarei mensagens até então. Se você me enviar uma mensagem, as notificações serão retomadas automaticamente.",
        "pause_resumed": "✅ Notificações retomadas!",
        "pause_resumed_formal": "✅ Notificações retomadas!",
        "social_profile_updated": "Perfil atualizado",
        "social_link_removed": "Link removido",
        "social_profile_not_configured": "Perfil social não configurado",
        "social_profile_empty": "Perfil social vazio. Adicione links de redes sociais ou biografia.",
        "social_networks_label": "<b>Redes sociais:</b>",
        "about_me_label": "<b>Sobre mim:</b>",
        "interests_label": "<b>Interesses:</b>",
        "profile_not_found": "Perfil não encontrado",
        "user_not_found": "Usuário não encontrado",
        "enter_social_link": "Envie o link do seu perfil na rede social:",
        "enter_social_link_formal": "Envie o link do seu perfil na rede social:",
        "enter_bio": "Conte um pouco sobre você (hobbies, interesses):",
        "enter_bio_formal": "Conte um pouco sobre o senhor/a senhora (hobbies, interesses):",
        "interests_detected": "✨ Interesses detectados: {interests}",
        "feedback_prompt": "Escreva sua sugestão ou ideia:",
        "feedback_prompt_formal": "Escreva sua sugestão ou ideia:",
        "feedback_sent": "Obrigado pelo feedback! 💝",
        "feedback_category": "Categoria: {category}",
        "help_title": "📋 Comandos disponíveis:",
        "help_start": "/start - Começar de novo",
        "help_help": "/help - Mostrar ajuda",
        "help_settings": "/settings - Configurações",
        "help_stats": "/stats - Estatísticas",
        "help_privacy": "/privacy - Política de privacidade",
        "help_export": "/export_data - Exportar dados",
        "help_delete": "/delete_data - Deletar dados",
        "privacy_title": "🔒 Política de privacidade",
        "privacy_text": "Levamos sua privacidade a sério.\n\n📌 Quais dados armazenamos:\n• Suas respostas às perguntas do bot\n• Configurações (fuso horário, idioma, intervalo)\n• Informações básicas do perfil do Telegram\n\n🔐 Como usamos os dados:\n• Apenas para personalizar sua experiência\n• Para lembrar bons momentos\n• Os dados não são compartilhados com terceiros\n\n🗑 Seus direitos:\n• /export_data - exportar todos os dados\n• /delete_data - deletar todos os dados",
        "export_confirm": "Exportar todos os seus dados?",
        "export_confirm_formal": "Exportar todos os seus dados?",
        "export_success": "Dados exportados",
        "delete_confirm": "⚠️ Atenção! Esta ação deletará TODOS os seus dados permanentemente. Continuar?",
        "delete_confirm_formal": "⚠️ Atenção! Esta ação deletará TODOS os seus dados permanentemente. Continuar?",
        "delete_success": "Todos os dados foram deletados. Até logo! 👋",
        "delete_data_title": "⚠️ <b>Eliminação de dados</b>",
        "delete_data_confirm": "Tem certeza de que deseja eliminar TODOS os seus dados da base de dados do bot?",
        "delete_data_confirm_formal": "Tem certeza de que deseja eliminar TODOS os seus dados da base de dados do bot?",
        "delete_data_warning": "Esta ação eliminará da base de dados do bot:",
        "delete_data_warning_formal": "Esta ação eliminará da base de dados do bot:",
        "delete_data_moments": "• Todos os seus momentos",
        "delete_data_moments_formal": "• Todos os seus momentos",
        "delete_data_conversations": "• O histórico de conversas",
        "delete_data_stats": "• Estatísticas",
        "delete_data_settings": "• Configurações",
        "delete_data_irreversible": "⚠️ <b>Esta ação é irreversível!</b>",
        "delete_data_chat_note": "ℹ️ <i>Nota: O histórico do chat no seu dispositivo permanecerá. Apenas os dados da base do bot serão eliminados.</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>Nota: O histórico do chat no seu dispositivo permanecerá. Apenas os dados da base do bot serão eliminados.</i>",
        "timezone_select_region": "Escolha a região:",
        "timezone_select_region_formal": "Escolha a região:",
        "select_start_hour": "Escolha o início das horas ativas:",
        "select_start_hour_formal": "Escolha o início das horas ativas:",
        "select_end_hour": "Escolha o fim das horas ativas:",
        "select_end_hour_formal": "Escolha o fim das horas ativas:",
        "current_settings": "⚙️ Configurações atuais:\n\n🕐 Horas ativas: {start_hour}:00 - {end_hour}:00\n⏰ Intervalo: {interval}\n🌍 Fuso horário: {timezone}\n🗣 Tratamento: {address}\n🚻 Gênero: {gender}\n🔔 Notificações: {notifications}\n🌐 Idioma: {language}",
        "settings_title": "⚙️ <b>Configurações</b>",
        "active_hours_title": "🕐 <b>Horas Ativas</b>",
        "interval_title": "⏰ <b>Intervalo entre perguntas</b>",
        "address_form_title": "🗣 <b>Forma de tratamento</b>",
        "gender_title": "🚻 <b>Gênero</b>",
        "language_title": "🌐 <b>Idioma da interface</b>",
        "timezone_title": "🌍 <b>Fuso horário</b>",
        "social_profile_title": "👤 <b>Perfil Social</b>",
        "select_active_hours_start": "Escolha o horário de início do período ativo:",
        "select_active_hours_end": "Agora escolha o horário de término:",
        "start_hour_set": "🕐 Início: {hour}:00",
        "how_often_ask": "Com que frequência devo perguntar sobre coisas boas?",
        "how_would_you_like": "Como você prefere?",
        "current_value": "Atual: {value}",
        "select_gender_prompt": "Escolha o gênero para o tratamento correto:",
        "select_language_prompt": "Escolha o idioma da interface:",
        "select_timezone_prompt": "Escolha sua região:",
        "select_timezone_city": "Escolha seu fuso horário:",
        "gender_male_value": "masculino",
        "gender_female_value": "feminino",
        "gender_unknown": "não especificado",
        "address_formal_value": "como «você»",
        "address_informal_value": "como «tu»",
        "notifications_on": "ativadas",
        "notifications_off": "desativadas",
        "notifications_toggled_on": "🔔 Notificações ativadas",
        "notifications_toggled_off": "🔔 Notificações desativadas",
        "settings.active_hours_value": "🕐 Horas ativas: {start} - {end}",
        "settings.interval_value": "⏰ Intervalo: a cada {interval} h.",
        "settings.timezone_value": "🌍 Fuso horário: {timezone}",
        "settings.formality_value": "🗣 Tratamento: {formality}",
        "settings.notifications_value": "🔔 Notificações: {status}",
        "every_n_hours": "a cada {hours} h.",
        "interval_set_confirm": "✅ Intervalo definido: a cada {hours} h.",
        "timezone_invalid": "❌ Erro: fuso horário inválido",
        "timezone_set_confirm": "✅ Fuso horário definido: {timezone}",
        "settings_reset_title": "✅ <b>Configurações redefinidas!</b>",
        "settings_reset_error": "😔 Não foi possível redefinir as configurações. Tente mais tarde.",
        "social_add_prompt": "🔗 <b>Adicionar rede social</b>\n\nEnvie o link da sua página na rede social.\n\nSuportados:\n• Instagram\n• Facebook\n• Twitter/X\n• LinkedIn\n• VKontakte\n• Canal do Telegram\n• YouTube\n• TikTok\n\nEnvie /cancel para cancelar.",
        "social_bio_prompt": "📝 <b>Edição de biografia</b>\n\nEscreva um pouco sobre você, seus hobbies e interesses.\nIsso me ajudará a entender melhor você e tornar nossa comunicação mais pessoal.\n\nEnvie /cancel para cancelar.",
        "social_parsing": "🔍 Analisando perfil...",
        "social_interests_found": "✅ <b>Interesses detectados!</b>\n\nSeus interesses: {interests}\n\nEssas informações serão usadas para personalizar nossa comunicação.",
        "social_interests_failed": "❌ Não foi possível detectar interesses.\n\nAdicione mais informações ao seu perfil: links para redes sociais ou biografia.",
        "social_no_links": "Você não tem redes sociais adicionadas.",
        "social_remove_title": "🗑 <b>Remover link</b>\n\nEscolha a rede social para remoção:",
        "moments_title": "📖 <b>Seus bons momentos</b>",
        "moments_empty": "📖 Você ainda não tem momentos salvos.\nQuando chegar a hora da pergunta, compartilhe algo bom! 🌟",
        "random_moment_header": "🎲 <b>Momento bom aleatório</b>",
        "moment_not_found": "😔 Momento não encontrado.",
        "moment_delete_title": "🗑️ <b>Excluir momento?</b>",
        "moment_delete_warning": "⚠️ Esta ação é irreversível!",
        "moment_deleted_confirm": "✅ Momento deletado.",
        "moment_delete_error": "😔 Não foi possível deletar o momento.",
        "no_moments_period": "📖 Sem momentos {period}.",
        "moments_period_title": "📖 <b>Momentos {period}</b>",
        "period_today": "hoje",
        "period_week": "na semana",
        "period_month": "no mês",
        "moments_pagination_next": "Próxima página",
        "moments_pagination_prev": "Página anterior",
        "dialog_intro": "💬 <b>Modo de diálogo</b>\n\nEstou pronto para ouvir você. Conte-me o que está em sua mente. Tentarei ajudar com uma visão externa, mas lembre-se — todas as decisões são suas. 💝\n\nPara sair do modo de diálogo, pressione o botão abaixo.",
        "dialog_exit_confirm": "Voltamos ao modo normal. Como posso ajudar? 😊",
        "main_menu_prompt": "Como posso ajudar? 😊",
        "data_deleted": "✅ Todos os seus dados foram deletados.\n\nSe você quiser voltar — basta escrever /start 💝",
        "data_delete_error": "😔 Ocorreu um erro ao deletar. Tente mais tarde.",
        "delete_cancelled": "👍 Exclusão cancelada. Seus dados estão seguros!",
        "question_skipped": "👍 Tudo bem, vamos pular esta pergunta. Até logo! 😊",
        "summary_title": "📊 <b>Resumo dos momentos</b>",
        "summary_generating_weekly": "⏳ Preparando resumo semanal...",
        "summary_generating_monthly": "⏳ Preparando resumo mensal...",
        "summary_not_enough_weekly": "📅 Momentos insuficientes para resumo semanal.\n\nQuando você tiver mais registros, poderei criar uma bela visão geral! 🌟",
        "summary_not_enough_monthly": "🗓 Momentos insuficientes para resumo mensal.\n\nQuando você tiver mais registros, poderei criar uma bela visão geral! 🌟",
        "stats_empty": "📊 Estatísticas ainda não disponíveis.\nComece a responder às perguntas e seu progresso aparecerá aqui! ✨",
        "question_1_informal": "O que correu bem hoje? 🌟",
        "question_2_informal": "Conta-me, o que te deixou feliz? ✨",
        "question_3_informal": "O que de bom aconteceu hoje? 😊",
        "question_4_informal": "Que momento de hoje foi especial? 💫",
        "question_5_informal": "O que te inspirou hoje? 🌈",
        "question_6_informal": "Conta uma pequena alegria de hoje! 💝",
        "question_7_informal": "O que de bom reparaste hoje? 🌻",
        "question_8_informal": "Por que razão sorriste hoje? 😄",
        "question_1_formal": "O que correu bem hoje? 🌟",
        "question_2_formal": "Conte-me, o que o(a) deixou feliz? ✨",
        "question_3_formal": "O que de bom aconteceu hoje? 😊",
        "question_4_formal": "Que momento de hoje foi especial? 💫",
        "question_5_formal": "O que o(a) inspirou hoje? 🌈",
        "question_6_formal": "Conte uma pequena alegria de hoje! 💝",
        "question_7_formal": "O que de bom reparou hoje? 🌻",
        "question_8_formal": "Por que razão sorriu hoje? 😄",
        "please_start_first": "Por favor, inicie o bot primeiro com o comando /start",
    },
    "fr": {
        "saved": "Enregistré!",
        "error": "Erreur",
        "success": "Réussi!",
        "cancelled": "Annulé",
        "loading": "Chargement...",
        "active_hours_set": "Heures actives définies : {start} - {end}",
        "interval_set": "Intervalle de notifications : {interval}",
        "timezone_set": "Fuseau horaire défini : {timezone}",
        "notifications_enabled": "🔔 Notifications activées",
        "notifications_disabled": "🔕 Notifications désactivées",
        "settings_reset": "Paramètres réinitialisés aux valeurs par défaut",
        "language_changed": "Langue changée en russe",
        "address_changed_informal": "Je vais m'adresser à toi en « tu »",
        "address_changed_formal": "Je vais m'adresser à vous en « vous »",
        "gender_set_male": "Genre défini : masculin",
        "gender_set_female": "Genre défini : féminin",
        "no_moments": "Tu n'as pas encore de moments enregistrés. Raconte-moi ce qui s'est bien passé aujourd'hui!",
        "no_moments_formal": "Vous n'avez pas encore de moments enregistrés. Racontez-moi ce qui s'est bien passé aujourd'hui!",
        "moment_deleted": "Moment supprimé",
        "moments_count": "Moments trouvés : {count}",
        "random_moment_title": "🎲 Moment joyeux aléatoire :",
        "stats_title": "📊 Tes statistiques",
        "stats_title_formal": "📊 Vos statistiques",
        "stats_total_moments": "Total des moments : {count}",
        "stats_current_streak": "Série actuelle : {days} j.",
        "stats_longest_streak": "Meilleure série : {days} j.",
        "stats_response_rate": "Taux de réponses : {rate}%",
        "stats_not_available": "Statistiques non disponibles pour le moment",
        "dialog_started": "💬 Mode dialogue. Je t'écoute. Écris « sortie » ou appuie sur le bouton pour sortir.",
        "dialog_started_formal": "💬 Mode dialogue. Je vous écoute. Écrivez « sortie » ou appuyez sur le bouton pour sortir.",
        "dialog_ended": "Dialogue terminé. Retour au menu principal.",
        "pause_title": "⏸ <b>Mettre le bot en pause</b>",
        "pause_title_formal": "⏸ <b>Mettre le bot en pause</b>",
        "pause_select_period": "Pour combien de temps souhaitez-vous suspendre l'envoi de messages ?",
        "pause_select_period_formal": "Pour combien de temps souhaitez-vous suspendre l'envoi de messages ?",
        "pause_day": "📅 Pour 1 jour",
        "pause_week": "📅 Pour 1 semaine",
        "pause_two_weeks": "📅 Pour 2 semaines",
        "pause_cancel": "⬅️ Annuler",
        "pause_confirmed": "✅ Bot en pause jusqu'au {date}. Je ne t'enverrai pas de messages jusqu'à cette date. Si tu m'écris, les notifications reprendront automatiquement.",
        "pause_confirmed_formal": "✅ Bot en pause jusqu'au {date}. Je ne vous enverrai pas de messages jusqu'à cette date. Si vous m'écrivez, les notifications reprendront automatiquement.",
        "pause_resumed": "✅ Notifications reprises !",
        "pause_resumed_formal": "✅ Notifications reprises !",
        "social_profile_updated": "Profil mis à jour",
        "social_link_removed": "Lien supprimé",
        "social_profile_not_configured": "Profil social non configuré",
        "social_profile_empty": "Profil social vide. Ajoute des liens vers tes réseaux ou une bio.",
        "social_networks_label": "<b>Réseaux sociaux :</b>",
        "about_me_label": "<b>À propos :</b>",
        "interests_label": "<b>Centres d'intérêt :</b>",
        "profile_not_found": "Profil introuvable",
        "user_not_found": "Utilisateur introuvable",
        "enter_social_link": "Envoie le lien de ton profil sur les réseaux sociaux :",
        "enter_social_link_formal": "Envoyez le lien de votre profil sur les réseaux sociaux :",
        "enter_bio": "Parle-moi un peu de toi (passions, intérêts) :",
        "enter_bio_formal": "Parlez-moi un peu de vous (passions, intérêts) :",
        "interests_detected": "✨ Intérêts détectés : {interests}",
        "feedback_prompt": "Écris ta suggestion ou ton idée :",
        "feedback_prompt_formal": "Écrivez votre suggestion ou votre idée :",
        "feedback_sent": "Merci pour votre retour! 💝",
        "feedback_category": "Catégorie : {category}",
        "help_title": "📋 Commandes disponibles :",
        "help_start": "/start - Recommencer",
        "help_help": "/help - Afficher l'aide",
        "help_settings": "/settings - Paramètres",
        "help_stats": "/stats - Statistiques",
        "help_privacy": "/privacy - Politique de confidentialité",
        "help_export": "/export_data - Exporter les données",
        "help_delete": "/delete_data - Supprimer les données",
        "privacy_title": "🔒 Politique de confidentialité",
        "privacy_text": "Nous prenons votre vie privée au sérieux.\n\n📌 Quelles données nous stockons :\n• Vos réponses aux questions du bot\n• Paramètres (fuseau horaire, langue, intervalle)\n• Informations de base de votre profil Telegram\n\n🔐 Comment nous utilisons les données :\n• Seulement pour personnaliser votre expérience\n• Pour rappeler les bons moments\n• Les données ne sont pas partagées avec des tiers\n\n🗑 Vos droits :\n• /export_data - exporter toutes les données\n• /delete_data - supprimer toutes les données",
        "export_confirm": "Exporter toutes tes données ?",
        "export_confirm_formal": "Exporter toutes vos données ?",
        "export_success": "Données exportées",
        "delete_confirm": "⚠️ Attention ! Cette action supprimera TOUTES tes données de façon irréversible. Continuer ?",
        "delete_confirm_formal": "⚠️ Attention ! Cette action supprimera TOUTES vos données de façon irréversible. Continuer ?",
        "delete_success": "Toutes les données ont été supprimées. Au revoir! 👋",
        "delete_data_title": "⚠️ <b>Suppression des données</b>",
        "delete_data_confirm": "Es-tu sûr de vouloir supprimer TOUTES tes données de la base du bot ?",
        "delete_data_confirm_formal": "Êtes-vous sûr de vouloir supprimer TOUTES vos données de la base du bot ?",
        "delete_data_warning": "Cette action supprimera de la base du bot :",
        "delete_data_warning_formal": "Cette action supprimera de la base du bot :",
        "delete_data_moments": "• Tous tes moments",
        "delete_data_moments_formal": "• Tous vos moments",
        "delete_data_conversations": "• L'historique des dialogues",
        "delete_data_stats": "• Les statistiques",
        "delete_data_settings": "• Les paramètres",
        "delete_data_irreversible": "⚠️ <b>Cette action est irréversible !</b>",
        "delete_data_chat_note": "ℹ️ <i>Note : L'historique du chat sur ton appareil restera. Seules les données de la base du bot seront supprimées.</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>Note : L'historique du chat sur votre appareil restera. Seules les données de la base du bot seront supprimées.</i>",
        "timezone_select_region": "Choisis une région :",
        "timezone_select_region_formal": "Choisissez une région :",
        "select_start_hour": "Choisis le début des heures actives :",
        "select_start_hour_formal": "Choisissez le début des heures actives :",
        "select_end_hour": "Choisis la fin des heures actives :",
        "select_end_hour_formal": "Choisissez la fin des heures actives :",
        "current_settings": "⚙️ Paramètres actuels :\n\n🕐 Heures actives : {start_hour}:00 - {end_hour}:00\n⏰ Intervalle : {interval}\n🌍 Fuseau horaire : {timezone}\n🗣 Adresse : {address}\n🚻 Genre : {gender}\n🔔 Notifications : {notifications}\n🌐 Langue : {language}",
        "settings_title": "⚙️ <b>Paramètres</b>",
        "active_hours_title": "🕐 <b>Heures actives</b>",
        "interval_title": "⏰ <b>Intervalle entre les questions</b>",
        "address_form_title": "🗣 <b>Forme d'adresse</b>",
        "gender_title": "🚻 <b>Genre</b>",
        "language_title": "🌐 <b>Langue de l'interface</b>",
        "timezone_title": "🌍 <b>Fuseau horaire</b>",
        "social_profile_title": "👤 <b>Profil social</b>",
        "select_active_hours_start": "Choisis l'heure de début de la période active :",
        "select_active_hours_end": "Maintenant choisis l'heure de fin :",
        "start_hour_set": "🕐 Début : {hour}:00",
        "how_often_ask": "À quelle fréquence devrais-je te demander ce qui va bien ?",
        "how_would_you_like": "Comment préfères-tu ?",
        "current_value": "Actuel : {value}",
        "select_gender_prompt": "Choisis le genre pour une adresse correcte :",
        "select_language_prompt": "Choisis la langue de l'interface :",
        "select_timezone_prompt": "Choisis ta région :",
        "select_timezone_city": "Choisis ton fuseau horaire :",
        "gender_male_value": "masculin",
        "gender_female_value": "féminin",
        "gender_unknown": "non spécifié",
        "address_formal_value": "en « vous »",
        "address_informal_value": "en « tu »",
        "notifications_on": "activées",
        "notifications_off": "désactivées",
        "notifications_toggled_on": "🔔 Notifications activées",
        "notifications_toggled_off": "🔔 Notifications désactivées",
        "settings.active_hours_value": "🕐 Heures actives : {start} - {end}",
        "settings.interval_value": "⏰ Intervalle : toutes les {interval} h.",
        "settings.timezone_value": "🌍 Fuseau horaire : {timezone}",
        "settings.formality_value": "🗣 Adresse : {formality}",
        "settings.notifications_value": "🔔 Notifications : {status}",
        "every_n_hours": "toutes les {hours} h.",
        "interval_set_confirm": "✅ Intervalle défini : toutes les {hours} h.",
        "timezone_invalid": "❌ Erreur : fuseau horaire invalide",
        "timezone_set_confirm": "✅ Fuseau horaire défini : {timezone}",
        "settings_reset_title": "✅ <b>Paramètres réinitialisés!</b>",
        "settings_reset_error": "😔 Échec de la réinitialisation des paramètres. Essaie plus tard.",
        "social_add_prompt": "🔗 <b>Ajouter un réseau social</b>\n\nEnvoie le lien de ta page sur les réseaux sociaux.\n\nSupportés :\n• Instagram\n• Facebook\n• Twitter/X\n• LinkedIn\n• VKontakte\n• Canal Telegram\n• YouTube\n• TikTok\n\nEnvoie /cancel pour annuler.",
        "social_bio_prompt": "📝 <b>Édition de la biographie</b>\n\nÉcris un peu sur toi, tes passions et tes intérêts.\nCela m'aidera à mieux te comprendre et à rendre notre communication plus personnelle.\n\nEnvoie /cancel pour annuler.",
        "social_parsing": "🔍 Analyse du profil...",
        "social_interests_found": "✅ <b>Intérêts détectés!</b>\n\nTes intérêts : {interests}\n\nCette information sera utilisée pour personnaliser notre communication.",
        "social_interests_failed": "❌ Impossible de détecter les intérêts.\n\nAjoute plus d'informations à ton profil : liens vers les réseaux sociaux ou biographie.",
        "social_no_links": "Tu n'as pas de réseaux sociaux ajoutés.",
        "social_remove_title": "🗑 <b>Supprimer le lien</b>\n\nChoisis un réseau social à supprimer :",
        "moments_title": "📖 <b>Tes bons moments</b>",
        "moments_empty": "📖 Tu n'as pas encore de moments enregistrés.\nQuand viendra le temps de la question, partage quelque chose de bien ! 🌟",
        "random_moment_header": "🎲 <b>Moment bon aléatoire</b>",
        "moment_not_found": "😔 Moment non trouvé.",
        "moment_delete_title": "🗑️ <b>Supprimer le moment ?</b>",
        "moment_delete_warning": "⚠️ Cette action est irréversible !",
        "moment_deleted_confirm": "✅ Moment supprimé.",
        "moment_delete_error": "😔 Impossible de supprimer le moment.",
        "no_moments_period": "📖 Pas de moments {period}.",
        "moments_period_title": "📖 <b>Moments {period}</b>",
        "period_today": "aujourd'hui",
        "period_week": "cette semaine",
        "period_month": "ce mois-ci",
        "moments_pagination_next": "Page suivante",
        "moments_pagination_prev": "Page précédente",
        "dialog_intro": "💬 <b>Mode dialogue</b>\n\nJe suis prêt à t'écouter. Dis-moi ce que tu as sur le cœur. J'essaierai d'aider avec un regard extérieur, mais souviens-toi — toutes les décisions te reviennent. 💝\n\nPour sortir du mode dialogue, appuie sur le bouton ci-dessous.",
        "dialog_exit_confirm": "Retour au mode normal. Comment puis-je t'aider ? 😊",
        "main_menu_prompt": "Comment puis-je t'aider ? 😊",
        "data_deleted": "✅ Toutes tes données ont été supprimées.\n\nSi tu souhaites revenir — écris simplement /start 💝",
        "data_delete_error": "😔 Une erreur est survenue lors de la suppression. Essaie plus tard.",
        "delete_cancelled": "👍 Suppression annulée. Tes données sont en sécurité !",
        "question_skipped": "👍 D'accord, nous allons sauter cette question. À bientôt ! 😊",
        "summary_title": "📊 <b>Résumé des moments</b>",
        "summary_generating_weekly": "⏳ Préparation du résumé hebdomadaire...",
        "summary_generating_monthly": "⏳ Préparation du résumé mensuel...",
        "summary_not_enough_weekly": "📅 Pas assez de moments pour un résumé hebdomadaire.\n\nQuand tu auras plus d'enregistrements, je pourrai créer un joli aperçu ! 🌟",
        "summary_not_enough_monthly": "🗓 Pas assez de moments pour un résumé mensuel.\n\nQuand tu auras plus d'enregistrements, je pourrai créer un joli aperçu ! 🌟",
        "stats_empty": "📊 Statistiques non disponibles pour le moment.\nCommence à répondre aux questions, et ton progrès apparaîtra ici ! ✨",
        "question_1_informal": "Qu'est-ce qui s'est bien passé aujourd'hui ? 🌟",
        "question_2_informal": "Dis-moi, qu'est-ce qui t'a rendu heureux(se) ? ✨",
        "question_3_informal": "Quoi de plaisant aujourd'hui ? 😊",
        "question_4_informal": "Quel moment d'aujourd'hui était spécial ? 💫",
        "question_5_informal": "Qu'est-ce qui t'a inspiré aujourd'hui ? 🌈",
        "question_6_informal": "Raconte une petite joie du jour ! 💝",
        "question_7_informal": "Quoi de bien as-tu remarqué aujourd'hui ? 🌻",
        "question_8_informal": "Pourquoi as-tu souri aujourd'hui ? 😄",
        "question_1_formal": "Qu'est-ce qui s'est bien passé aujourd'hui ? 🌟",
        "question_2_formal": "Dites-moi, qu'est-ce qui vous a rendu heureux(se) ? ✨",
        "question_3_formal": "Quoi de plaisant aujourd'hui ? 😊",
        "question_4_formal": "Quel moment d'aujourd'hui était spécial ? 💫",
        "question_5_formal": "Qu'est-ce qui vous a inspiré aujourd'hui ? 🌈",
        "question_6_formal": "Racontez une petite joie du jour ! 💝",
        "question_7_formal": "Quoi de bien avez-vous remarqué aujourd'hui ? 🌻",
        "question_8_formal": "Pourquoi avez-vous souri aujourd'hui ? 😄",
        "please_start_first": "Veuillez d'abord démarrer le bot avec la commande /start",
    },
    "de": {
        "saved": "Gespeichert!",
        "error": "Fehler",
        "success": "Erfolgreich!",
        "cancelled": "Abgebrochen",
        "loading": "Lädt...",
        "active_hours_set": "Aktive Stunden festgelegt: {start} - {end}",
        "interval_set": "Benachrichtigungsintervall: {interval}",
        "timezone_set": "Zeitzone festgelegt: {timezone}",
        "notifications_enabled": "🔔 Benachrichtigungen aktiviert",
        "notifications_disabled": "🔕 Benachrichtigungen deaktiviert",
        "settings_reset": "Einstellungen auf die Standardwerte zurückgesetzt",
        "language_changed": "Sprache auf Russisch geändert",
        "address_changed_informal": "Ich werde dich mit «du» ansprechen",
        "address_changed_formal": "Ich werde Sie mit «Sie» ansprechen",
        "gender_set_male": "Geschlecht festgelegt: männlich",
        "gender_set_female": "Geschlecht festgelegt: weiblich",
        "no_moments": "Du hast noch keine gespeicherten Momente. Erzähl mir, was heute Schönes passiert ist!",
        "no_moments_formal": "Sie haben noch keine gespeicherten Momente. Erzählen Sie mir, was heute Schönes passiert ist!",
        "moment_deleted": "Moment gelöscht",
        "moments_count": "Gefundene Momente: {count}",
        "random_moment_title": "🎲 Zufälliger schöner Moment:",
        "stats_title": "📊 Deine Statistik",
        "stats_title_formal": "📊 Ihre Statistik",
        "stats_total_moments": "Insgesamt Momente: {count}",
        "stats_current_streak": "Aktuelle Serie: {days} Tage",
        "stats_longest_streak": "Beste Serie: {days} Tage",
        "stats_response_rate": "Antwortquote: {rate}%",
        "stats_not_available": "Statistik derzeit nicht verfügbar",
        "dialog_started": "💬 Dialogmodus. Ich höre dir zu. Schreib «aus» oder drücke die Taste, um zu beenden.",
        "dialog_started_formal": "💬 Dialogmodus. Ich höre Ihnen zu. Schreiben Sie «aus» oder drücken Sie die Taste, um zu beenden.",
        "dialog_ended": "Dialog beendet. Ich bringe dich ins Hauptmenü zurück.",
        "pause_title": "⏸ <b>Bot pausieren</b>",
        "pause_title_formal": "⏸ <b>Bot pausieren</b>",
        "pause_select_period": "Für wie lange soll ich das Senden von Nachrichten pausieren?",
        "pause_select_period_formal": "Für wie lange soll ich das Senden von Nachrichten pausieren?",
        "pause_day": "📅 Für 1 Tag",
        "pause_week": "📅 Für 1 Woche",
        "pause_two_weeks": "📅 Für 2 Wochen",
        "pause_cancel": "⬅️ Abbrechen",
        "pause_confirmed": "✅ Bot pausiert bis {date}. Ich werde dir bis dahin keine Nachrichten senden. Wenn du mir schreibst, werden die Benachrichtigungen automatisch fortgesetzt.",
        "pause_confirmed_formal": "✅ Bot pausiert bis {date}. Ich werde Ihnen bis dahin keine Nachrichten senden. Wenn Sie mir schreiben, werden die Benachrichtigungen automatisch fortgesetzt.",
        "pause_resumed": "✅ Benachrichtigungen fortgesetzt!",
        "pause_resumed_formal": "✅ Benachrichtigungen fortgesetzt!",
        "social_profile_updated": "Profil aktualisiert",
        "social_link_removed": "Link entfernt",
        "social_profile_not_configured": "Soziales Profil nicht eingerichtet",
        "social_profile_empty": "Soziales Profil leer. Links zu sozialen Netzwerken oder Biografie hinzufügen.",
        "social_networks_label": "<b>Soziale Netzwerke:</b>",
        "about_me_label": "<b>Über mich:</b>",
        "interests_label": "<b>Interessen:</b>",
        "profile_not_found": "Profil nicht gefunden",
        "user_not_found": "Benutzer nicht gefunden",
        "enter_social_link": "Schick mir den Link zu deinem Profil in sozialen Netzwerken:",
        "enter_social_link_formal": "Schicken Sie mir den Link zu Ihrem Profil in sozialen Netzwerken:",
        "enter_bio": "Erzähl ein wenig über dich (Hobbys, Interessen):",
        "enter_bio_formal": "Erzählen Sie ein wenig über sich (Hobbys, Interessen):",
        "interests_detected": "✨ Interessen erkannt: {interests}",
        "feedback_prompt": "Schreib mir deinen Vorschlag oder deine Idee:",
        "feedback_prompt_formal": "Schreiben Sie Ihren Vorschlag oder Ihre Idee:",
        "feedback_sent": "Danke für dein Feedback! 💝",
        "feedback_category": "Kategorie: {category}",
        "help_title": "📋 Verfügbare Befehle:",
        "help_start": "/start - Neu starten",
        "help_help": "/help - Hilfe anzeigen",
        "help_settings": "/settings - Einstellungen",
        "help_stats": "/stats - Statistik",
        "help_privacy": "/privacy - Datenschutzrichtlinie",
        "help_export": "/export_data - Daten exportieren",
        "help_delete": "/delete_data - Daten löschen",
        "privacy_title": "🔒 Datenschutzrichtlinie",
        "privacy_text": "Wir nehmen Ihre Privatsphäre ernst.\n\n📌 Welche Daten wir speichern:\n• Ihre Antworten auf die Fragen des Bots\n• Einstellungen (Zeitzone, Sprache, Intervall)\n• Grundlegende Informationen aus dem Telegram-Profil\n\n🔐 Wie wir Daten verwenden:\n• Nur zur Personalisierung Ihres Erlebnisses\n• Um an schöne Momente zu erinnern\n• Daten werden nicht an Dritte weitergegeben\n\n🗑 Ihre Rechte:\n• /export_data - alle Daten exportieren\n• /delete_data - alle Daten löschen",
        "export_confirm": "Alle deine Daten exportieren?",
        "export_confirm_formal": "Alle Ihre Daten exportieren?",
        "export_success": "Daten exportiert",
        "delete_confirm": "⚠️ Achtung! Diese Aktion löscht ALLE deine Daten unwiderruflich. Fortfahren?",
        "delete_confirm_formal": "⚠️ Achtung! Diese Aktion löscht ALLE Ihre Daten unwiderruflich. Fortfahren?",
        "delete_success": "Alle Daten gelöscht. Auf Wiedersehen! 👋",
        "delete_data_title": "⚠️ <b>Datenlöschung</b>",
        "delete_data_confirm": "Bist du sicher, dass du ALLE deine Daten aus der Bot-Datenbank löschen möchtest?",
        "delete_data_confirm_formal": "Sind Sie sicher, dass Sie ALLE Ihre Daten aus der Bot-Datenbank löschen möchten?",
        "delete_data_warning": "Diese Aktion löscht aus der Bot-Datenbank:",
        "delete_data_warning_formal": "Diese Aktion löscht aus der Bot-Datenbank:",
        "delete_data_moments": "• Alle deine Momente",
        "delete_data_moments_formal": "• Alle Ihre Momente",
        "delete_data_conversations": "• Den Dialogverlauf",
        "delete_data_stats": "• Statistiken",
        "delete_data_settings": "• Einstellungen",
        "delete_data_irreversible": "⚠️ <b>Diese Aktion ist unwiderruflich!</b>",
        "delete_data_chat_note": "ℹ️ <i>Hinweis: Der Chatverlauf auf deinem Gerät bleibt. Nur Daten aus der Bot-Datenbank werden gelöscht.</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>Hinweis: Der Chatverlauf auf Ihrem Gerät bleibt. Nur Daten aus der Bot-Datenbank werden gelöscht.</i>",
        "timezone_select_region": "Wähle eine Region:",
        "timezone_select_region_formal": "Wählen Sie eine Region:",
        "select_start_hour": "Wähle den Beginn der aktiven Stunden:",
        "select_start_hour_formal": "Wählen Sie den Beginn der aktiven Stunden:",
        "select_end_hour": "Wähle das Ende der aktiven Stunden:",
        "select_end_hour_formal": "Wählen Sie das Ende der aktiven Stunden:",
        "current_settings": "⚙️ Aktuelle Einstellungen:\n\n🕐 Aktive Stunden: {start_hour}:00 - {end_hour}:00\n⏰ Intervall: {interval}\n🌍 Zeitzone: {timezone}\n🗣 Ansprache: {address}\n🚻 Geschlecht: {gender}\n🔔 Benachrichtigungen: {notifications}\n🌐 Sprache: {language}",
        "settings_title": "⚙️ <b>Einstellungen</b>",
        "active_hours_title": "🕐 <b>Aktive Stunden</b>",
        "interval_title": "⏰ <b>Intervall zwischen Fragen</b>",
        "address_form_title": "🗣 <b>Ansprache</b>",
        "gender_title": "🚻 <b>Geschlecht</b>",
        "language_title": "🌐 <b>Sprache der Benutzeroberfläche</b>",
        "timezone_title": "🌍 <b>Zeitzone</b>",
        "social_profile_title": "👤 <b>Soziales Profil</b>",
        "select_active_hours_start": "Wähle die Startzeit des aktiven Zeitraums:",
        "select_active_hours_end": "Wähle jetzt die Endzeit:",
        "start_hour_set": "🕐 Beginn: {hour}:00",
        "how_often_ask": "Wie oft soll ich nach dem Guten fragen?",
        "how_would_you_like": "Wie wäre es dir lieber?",
        "current_value": "Aktuell: {value}",
        "select_gender_prompt": "Wähle das Geschlecht für die richtige Ansprache:",
        "select_language_prompt": "Wähle die Sprache der Benutzeroberfläche:",
        "select_timezone_prompt": "Wähle deine Region:",
        "select_timezone_city": "Wähle deine Zeitzone:",
        "gender_male_value": "männlich",
        "gender_female_value": "weiblich",
        "gender_unknown": "nicht angegeben",
        "address_formal_value": "mit «Sie»",
        "address_informal_value": "mit «du»",
        "notifications_on": "aktiviert",
        "notifications_off": "deaktiviert",
        "notifications_toggled_on": "🔔 Benachrichtigungen aktiviert",
        "notifications_toggled_off": "🔔 Benachrichtigungen deaktiviert",
        "settings.active_hours_value": "🕐 Aktive Stunden: {start} - {end}",
        "settings.interval_value": "⏰ Intervall: alle {interval} Std.",
        "settings.timezone_value": "🌍 Zeitzone: {timezone}",
        "settings.formality_value": "🗣 Ansprache: {formality}",
        "settings.notifications_value": "🔔 Benachrichtigungen: {status}",
        "every_n_hours": "alle {hours} Std.",
        "interval_set_confirm": "✅ Intervall festgelegt: alle {hours} Std.",
        "timezone_invalid": "❌ Fehler: ungültige Zeitzone",
        "timezone_set_confirm": "✅ Zeitzone festgelegt: {timezone}",
        "settings_reset_title": "✅ <b>Einstellungen zurückgesetzt!</b>",
        "settings_reset_error": "😔 Einstellungen konnten nicht zurückgesetzt werden. Versuch es später erneut.",
        "social_add_prompt": "🔗 <b>Soziale Netzwerke hinzufügen</b>\n\nSchick mir den Link zu deiner Seite in sozialen Netzwerken.\n\nUnterstützt:\n• Instagram\n• Facebook\n• Twitter/X\n• LinkedIn\n• VKontakte\n• Telegram-Kanal\n• YouTube\n• TikTok\n\nSchick /cancel um abzubrechen.",
        "social_bio_prompt": "📝 <b>Biografie bearbeiten</b>\n\nSchreib ein wenig über dich, deine Hobbys und Interessen.\nDas hilft mir, dich besser zu verstehen und unser Gespräch persönlicher zu gestalten.\n\nSchick /cancel um abzubrechen.",
        "social_parsing": "🔍 Analysiere Profil...",
        "social_interests_found": "✅ <b>Interessen erkannt!</b>\n\nDeine Interessen: {interests}\n\nDiese Informationen werden zur Personalisierung unseres Gesprächs verwendet.",
        "social_interests_failed": "❌ Interessen konnten nicht erkannt werden.\n\nFüge mehr Informationen in deinem Profil hinzu: Links zu sozialen Netzwerken oder eine Biografie.",
        "social_no_links": "Du hast keine hinzugefügten sozialen Netzwerke.",
        "social_remove_title": "🗑 <b>Link entfernen</b>\n\nWähle das soziale Netzwerk zum Entfernen:",
        "moments_title": "📖 <b>Deine schönen Momente</b>",
        "moments_empty": "📖 Du hast noch keine gespeicherten Momente.\nWenn die Zeit für die Frage kommt, teile etwas Schönes! 🌟",
        "random_moment_header": "🎲 <b>Zufälliger schöner Moment</b>",
        "moment_not_found": "😔 Moment nicht gefunden.",
        "moment_delete_title": "🗑️ <b>Moment löschen?</b>",
        "moment_delete_warning": "⚠️ Diese Aktion ist unwiderruflich!",
        "moment_deleted_confirm": "✅ Moment gelöscht.",
        "moment_delete_error": "😔 Moment konnte nicht gelöscht werden.",
        "no_moments_period": "📖 Keine Momente {period}.",
        "moments_period_title": "📖 <b>Momente {period}</b>",
        "period_today": "heute",
        "period_week": "in der Woche",
        "period_month": "im Monat",
        "moments_pagination_next": "Nächste Seite",
        "moments_pagination_prev": "Vorherige Seite",
        "dialog_intro": "💬 <b>Dialogmodus</b>\n\nIch bin bereit, dir zuzuhören. Erzähl mir, was dich beschäftigt. Ich werde versuchen, dir eine Außenperspektive zu geben, aber denk daran — alle Entscheidungen triffst du selbst. 💝\n\nUm den Dialogmodus zu verlassen, drücke die Taste unten.",
        "dialog_exit_confirm": "Wir sind zurück im normalen Modus. Wie kann ich helfen? 😊",
        "main_menu_prompt": "Wie kann ich helfen? 😊",
        "data_deleted": "✅ Alle deine Daten wurden gelöscht.\n\nWenn du zurückkommen möchtest — schreib einfach /start 💝",
        "data_delete_error": "😔 Es gab einen Fehler beim Löschen. Versuch es später erneut.",
        "delete_cancelled": "👍 Löschung abgebrochen. Deine Daten sind sicher!",
        "question_skipped": "👍 Gut, wir überspringen diese Frage. Bis bald! 😊",
        "summary_title": "📊 <b>Zusammenfassung der Momente</b>",
        "summary_generating_weekly": "⏳ Bereite wöchentliche Zusammenfassung vor...",
        "summary_generating_monthly": "⏳ Bereite monatliche Zusammenfassung vor...",
        "summary_not_enough_weekly": "📅 Nicht genügend Momente für eine wöchentliche Zusammenfassung.\n\nWenn du mehr Einträge hast, kann ich eine schöne Übersicht erstellen! 🌟",
        "summary_not_enough_monthly": "🗓 Nicht genügend Momente für eine monatliche Zusammenfassung.\n\nWenn du mehr Einträge hast, kann ich eine schöne Übersicht erstellen! 🌟",
        "stats_empty": "📊 Statistik derzeit nicht verfügbar.\nBeginne, auf die Fragen zu antworten, und hier wird dein Fortschritt erscheinen! ✨",
        "question_1_informal": "Was war heute schön? 🌟",
        "question_2_informal": "Erzähl mal, was hat dich gefreut? ✨",
        "question_3_informal": "Was Angenehmes ist heute passiert? 😊",
        "question_4_informal": "Welcher Moment heute war besonders? 💫",
        "question_5_informal": "Was hat dich heute inspiriert? 🌈",
        "question_6_informal": "Erzähl von einer kleinen Freude heute! 💝",
        "question_7_informal": "Was Schönes hast du heute bemerkt? 🌻",
        "question_8_informal": "Worum hast du heute gelacht? 😄",
        "question_1_formal": "Was war heute schön? 🌟",
        "question_2_formal": "Erzählen Sie, was Sie gefreut hat? ✨",
        "question_3_formal": "Was Angenehmes ist heute passiert? 😊",
        "question_4_formal": "Welcher Moment heute war besonders? 💫",
        "question_5_formal": "Was hat Sie heute inspiriert? 🌈",
        "question_6_formal": "Erzählen Sie von einer kleinen Freude heute! 💝",
        "question_7_formal": "Was Schönes haben Sie heute bemerkt? 🌻",
        "question_8_formal": "Worum haben Sie heute gelacht? 😄",
        "please_start_first": "Bitte starte zuerst den Bot mit dem Befehl /start",
    },
    "es": {
        "saved": "¡Guardado!",
        "error": "Error",
        "success": "¡Exitoso!",
        "cancelled": "Cancelado",
        "loading": "Cargando...",
        "active_hours_set": "Horas activas establecidas: {start} - {end}",
        "interval_set": "Intervalo de notificaciones: {interval}",
        "timezone_set": "Zona horaria establecida: {timezone}",
        "notifications_enabled": "🔔 Notificaciones habilitadas",
        "notifications_disabled": "🔕 Notificaciones deshabilitadas",
        "settings_reset": "Configuraciones restablecidas a los valores predeterminados",
        "language_changed": "Idioma cambiado a ruso",
        "address_changed_informal": "Voy a dirigirme a ti de «tú»",
        "address_changed_formal": "Voy a dirigirme a usted de «usted»",
        "gender_set_male": "Género establecido: masculino",
        "gender_set_female": "Género establecido: femenino",
        "no_moments": "No tienes momentos guardados por ahora. ¡Cuéntame qué bueno pasó hoy!",
        "no_moments_formal": "No tiene momentos guardados por ahora. ¡Cuéntenos qué bueno pasó hoy!",
        "moment_deleted": "Momento eliminado",
        "moments_count": "Momentos encontrados: {count}",
        "random_moment_title": "🎲 Momento alegre aleatorio:",
        "stats_title": "📊 Tu estadística",
        "stats_title_formal": "📊 Su estadística",
        "stats_total_moments": "Total de momentos: {count}",
        "stats_current_streak": "Racha actual: {days} días.",
        "stats_longest_streak": "Mejor racha: {days} días.",
        "stats_response_rate": "Porcentaje de respuestas: {rate}%",
        "stats_not_available": "Estadísticas no disponibles por ahora",
        "dialog_started": "💬 Modo de diálogo. Te escucho. Escribe «salir» o presiona el botón para salir.",
        "dialog_started_formal": "💬 Modo de diálogo. Lo escucho. Escriba «salir» o presione el botón para salir.",
        "dialog_ended": "Diálogo terminado. Regresando al menú principal.",
        "pause_title": "⏸ <b>Pausar bot</b>",
        "pause_title_formal": "⏸ <b>Pausar bot</b>",
        "pause_select_period": "¿Por cuánto tiempo deseas pausar el envío de mensajes?",
        "pause_select_period_formal": "¿Por cuánto tiempo desea pausar el envío de mensajes?",
        "pause_day": "📅 Por 1 día",
        "pause_week": "📅 Por 1 semana",
        "pause_two_weeks": "📅 Por 2 semanas",
        "pause_cancel": "⬅️ Cancelar",
        "pause_confirmed": "✅ Bot pausado hasta {date}. No te enviaré mensajes hasta entonces. Si me escribes, las notificaciones se reanudarán automáticamente.",
        "pause_confirmed_formal": "✅ Bot pausado hasta {date}. No le enviaré mensajes hasta entonces. Si me escribe, las notificaciones se reanudarán automáticamente.",
        "pause_resumed": "✅ ¡Notificaciones reanudadas!",
        "pause_resumed_formal": "✅ ¡Notificaciones reanudadas!",
        "social_profile_updated": "Perfil actualizado",
        "social_link_removed": "Enlace eliminado",
        "social_profile_not_configured": "Perfil social no configurado",
        "social_profile_empty": "Perfil social vacío. Añade enlaces a redes sociales o biografía.",
        "social_networks_label": "<b>Redes sociales:</b>",
        "about_me_label": "<b>Sobre mí:</b>",
        "interests_label": "<b>Intereses:</b>",
        "profile_not_found": "Perfil no encontrado",
        "user_not_found": "Usuario no encontrado",
        "enter_social_link": "Envía el enlace a tu perfil en la red social:",
        "enter_social_link_formal": "Envíe el enlace a su perfil en la red social:",
        "enter_bio": "Cuéntame un poco sobre ti (aficiones, intereses):",
        "enter_bio_formal": "Cuéntenos un poco sobre usted (aficiones, intereses):",
        "interests_detected": "✨ Intereses detectados: {interests}",
        "feedback_prompt": "Escribe tu sugerencia o idea:",
        "feedback_prompt_formal": "Escriba su sugerencia o idea:",
        "feedback_sent": "¡Gracias por tu retroalimentación! 💝",
        "feedback_category": "Categoría: {category}",
        "help_title": "📋 Comandos disponibles:",
        "help_start": "/start - Comenzar de nuevo",
        "help_help": "/help - Mostrar ayuda",
        "help_settings": "/settings - Configuraciones",
        "help_stats": "/stats - Estadísticas",
        "help_privacy": "/privacy - Política de privacidad",
        "help_export": "/export_data - Exportar datos",
        "help_delete": "/delete_data - Eliminar datos",
        "privacy_title": "🔒 Política de privacidad",
        "privacy_text": "Tomamos en serio tu privacidad.\n\n📌 Qué datos almacenamos:\n• Tus respuestas a las preguntas del bot\n• Configuraciones (zona horaria, idioma, intervalo)\n• Información básica de tu perfil de Telegram\n\n🔐 Cómo usamos los datos:\n• Solo para personalizar tu experiencia\n• Para recordarte momentos buenos\n• Los datos no se comparten con terceros\n\n🗑 Tus derechos:\n• /export_data - exportar todos los datos\n• /delete_data - eliminar todos los datos",
        "export_confirm": "¿Exportar todos tus datos?",
        "export_confirm_formal": "¿Exportar todos sus datos?",
        "export_success": "Datos exportados",
        "delete_confirm": "⚠️ ¡Atención! Esta acción eliminará TODOS tus datos de forma irreversible. ¿Continuar?",
        "delete_confirm_formal": "⚠️ ¡Atención! Esta acción eliminará TODOS sus datos de forma irreversible. ¿Continuar?",
        "delete_success": "Todos los datos eliminados. ¡Adiós! 👋",
        "delete_data_title": "⚠️ <b>Eliminación de datos</b>",
        "delete_data_confirm": "¿Estás seguro de que quieres eliminar TODOS tus datos de la base de datos del bot?",
        "delete_data_confirm_formal": "¿Está seguro de que quiere eliminar TODOS sus datos de la base de datos del bot?",
        "delete_data_warning": "Esta acción eliminará de la base de datos del bot:",
        "delete_data_warning_formal": "Esta acción eliminará de la base de datos del bot:",
        "delete_data_moments": "• Todos tus momentos",
        "delete_data_moments_formal": "• Todos sus momentos",
        "delete_data_conversations": "• El historial de conversaciones",
        "delete_data_stats": "• Estadísticas",
        "delete_data_settings": "• Configuraciones",
        "delete_data_irreversible": "⚠️ <b>¡Esta acción es irreversible!</b>",
        "delete_data_chat_note": "ℹ️ <i>Nota: El historial del chat en tu dispositivo se mantendrá. Solo se eliminan los datos de la base del bot.</i>",
        "delete_data_chat_note_formal": "ℹ️ <i>Nota: El historial del chat en su dispositivo se mantendrá. Solo se eliminan los datos de la base del bot.</i>",
        "timezone_select_region": "Elige una región:",
        "timezone_select_region_formal": "Seleccione una región:",
        "select_start_hour": "Elige el inicio de las horas activas:",
        "select_start_hour_formal": "Seleccione el inicio de las horas activas:",
        "select_end_hour": "Elige el final de las horas activas:",
        "select_end_hour_formal": "Seleccione el final de las horas activas:",
        "current_settings": "⚙️ Configuraciones actuales:\n\n🕐 Horas activas: {start_hour}:00 - {end_hour}:00\n⏰ Intervalo: {interval}\n🌍 Zona horaria: {timezone}\n🗣 Tratamiento: {address}\n🚻 Género: {gender}\n🔔 Notificaciones: {notifications}\n🌐 Idioma: {language}",
        "settings_title": "⚙️ <b>Configuraciones</b>",
        "active_hours_title": "🕐 <b>Horas activas</b>",
        "interval_title": "⏰ <b>Intervalo entre preguntas</b>",
        "address_form_title": "🗣 <b>Forma de tratamiento</b>",
        "gender_title": "🚻 <b>Género</b>",
        "language_title": "🌐 <b>Idioma de la interfaz</b>",
        "timezone_title": "🌍 <b>Zona horaria</b>",
        "social_profile_title": "👤 <b>Perfil social</b>",
        "select_active_hours_start": "Elige la hora de inicio del período activo:",
        "select_active_hours_end": "Ahora elige la hora de finalización:",
        "start_hour_set": "🕐 Inicio: {hour}:00",
        "how_often_ask": "¿Con qué frecuencia debo preguntar sobre lo bueno?",
        "how_would_you_like": "¿Cómo te gustaría?",
        "current_value": "Actual: {value}",
        "select_gender_prompt": "Elige el género para un tratamiento correcto:",
        "select_language_prompt": "Elige el idioma de la interfaz:",
        "select_timezone_prompt": "Elige tu región:",
        "select_timezone_city": "Elige tu zona horaria:",
        "gender_male_value": "masculino",
        "gender_female_value": "femenino",
        "gender_unknown": "no especificado",
        "address_formal_value": "de «usted»",
        "address_informal_value": "de «tú»",
        "notifications_on": "habilitadas",
        "notifications_off": "deshabilitadas",
        "notifications_toggled_on": "🔔 Notificaciones habilitadas",
        "notifications_toggled_off": "🔔 Notificaciones deshabilitadas",
        "settings.active_hours_value": "🕐 Horas activas: {start} - {end}",
        "settings.interval_value": "⏰ Intervalo: cada {interval} h.",
        "settings.timezone_value": "🌍 Zona horaria: {timezone}",
        "settings.formality_value": "🗣 Tratamiento: {formality}",
        "settings.notifications_value": "🔔 Notificaciones: {status}",
        "every_n_hours": "cada {hours} h.",
        "interval_set_confirm": "✅ Intervalo establecido: cada {hours} h.",
        "timezone_invalid": "❌ Error: zona horaria incorrecta",
        "timezone_set_confirm": "✅ Zona horaria establecida: {timezone}",
        "settings_reset_title": "✅ <b>¡Configuraciones restablecidas!</b>",
        "settings_reset_error": "😔 No se pudo restablecer la configuración. Intenta más tarde.",
        "social_add_prompt": "🔗 <b>Agregar red social</b>\n\nEnvía el enlace a tu página en la red social.\n\nSoportados:\n• Instagram\n• Facebook\n• Twitter/X\n• LinkedIn\n• VKontakte\n• Canal de Telegram\n• YouTube\n• TikTok\n\nEnvía /cancel para cancelar.",
        "social_bio_prompt": "📝 <b>Edición de biografía</b>\n\nEscribe un poco sobre ti, tus aficiones e intereses.\nEsto me ayudará a entenderte mejor y hacer nuestra comunicación más personal.\n\nEnvía /cancel para cancelar.",
        "social_parsing": "🔍 Analizando perfil...",
        "social_interests_found": "✅ <b>¡Intereses detectados!</b>\n\nTus intereses: {interests}\n\nEsta información se utilizará para personalizar nuestra comunicación.",
        "social_interests_failed": "❌ No se pudieron detectar intereses.\n\nAgrega más información a tu perfil: enlaces a redes sociales o biografía.",
        "social_no_links": "No tienes redes sociales agregadas.",
        "social_remove_title": "🗑 <b>Eliminar enlace</b>\n\nElige la red social para eliminar:",
        "moments_title": "📖 <b>Tus buenos momentos</b>",
        "moments_empty": "📖 No tienes momentos guardados por ahora.\n¡Cuando llegue el momento de la pregunta, comparte algo bueno! 🌟",
        "random_moment_header": "🎲 <b>Momento bueno aleatorio</b>",
        "moment_not_found": "😔 Momento no encontrado.",
        "moment_delete_title": "🗑️ <b>¿Eliminar momento?</b>",
        "moment_delete_warning": "⚠️ ¡Esta acción es irreversible!",
        "moment_deleted_confirm": "✅ Momento eliminado.",
        "moment_delete_error": "😔 No se pudo eliminar el momento.",
        "no_moments_period": "📖 No hay momentos {period}.",
        "moments_period_title": "📖 <b>Momentos {period}</b>",
        "period_today": "hoy",
        "period_week": "esta semana",
        "period_month": "este mes",
        "moments_pagination_next": "Página siguiente",
        "moments_pagination_prev": "Página anterior",
        "dialog_intro": "💬 <b>Modo de diálogo</b>\n\nEstoy listo para escucharte. Cuéntame qué tienes en el corazón. Intentaré ayudarte con una perspectiva externa, pero recuerda: todas las decisiones las tomas tú. 💝\n\nPara salir del modo de diálogo, presiona el botón de abajo.",
        "dialog_exit_confirm": "Regresamos al modo normal. ¿En qué puedo ayudar? 😊",
        "main_menu_prompt": "¿En qué puedo ayudar? 😊",
        "data_deleted": "✅ Todos tus datos han sido eliminados.\n\nSi deseas regresar, simplemente escribe /start 💝",
        "data_delete_error": "😔 Ocurrió un error al eliminar. Intenta más tarde.",
        "delete_cancelled": "👍 Eliminación cancelada. ¡Tus datos están a salvo!",
        "question_skipped": "👍 Bien, saltaremos esta pregunta. ¡Hasta pronto! 😊",
        "summary_title": "📊 <b>Resumen de momentos</b>",
        "summary_generating_weekly": "⏳ Generando resumen semanal...",
        "summary_generating_monthly": "⏳ Generando resumen mensual...",
        "summary_not_enough_weekly": "📅 No hay suficientes momentos para un resumen semanal.\n\nCuando tengas más registros, podré crear una hermosa revisión. 🌟",
        "summary_not_enough_monthly": "🗓 No hay suficientes momentos para un resumen mensual.\n\nCuando tengas más registros, podré crear una hermosa revisión. 🌟",
        "stats_empty": "📊 Estadísticas no disponibles por ahora.\n¡Comienza a responder preguntas y aquí aparecerá tu progreso! ✨",
        "question_1_informal": "¿Qué bueno pasó hoy? 🌟",
        "question_2_informal": "Cuéntame, ¿qué te alegró? ✨",
        "question_3_informal": "¿Qué cosa agradable pasó hoy? 😊",
        "question_4_informal": "¿Qué momento de hoy fue especial? 💫",
        "question_5_informal": "¿Qué te inspiró hoy? 🌈",
        "question_6_informal": "¡Cuéntame una pequeña alegría del día! 💝",
        "question_7_informal": "¿Qué bueno notaste hoy? 🌻",
        "question_8_informal": "¿Por qué sonreíste hoy? 😄",
        "question_1_formal": "¿Qué bueno pasó hoy? 🌟",
        "question_2_formal": "Cuénteme, ¿qué le alegró? ✨",
        "question_3_formal": "¿Qué cosa agradable pasó hoy? 😊",
        "question_4_formal": "¿Qué momento de hoy fue especial? 💫",
        "question_5_formal": "¿Qué le inspiró hoy? 🌈",
        "question_6_formal": "¡Cuénteme una pequeña alegría del día! 💝",
        "question_7_formal": "¿Qué bueno notó hoy? 🌻",
        "question_8_formal": "¿Por qué sonrió hoy? 😄",
        "please_start_first": "Por favor, primero inicia el bot con el comando /start",
    },}


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


# Alias for shorter function name
t = get_system_message
