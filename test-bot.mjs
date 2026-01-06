/**
 * MINDSETHAPPYBOT - Node.js Testing Implementation
 * Full implementation for testing bot features
 */

const BOT_TOKEN = '7805611571:AAF59MdS0N3By7mMq_O53Wo8LjYLwfXVrBY';
const BASE_URL = `https://api.telegram.org/bot${BOT_TOKEN}`;

// Welcome image URL (same as Python implementation)
const WELCOME_IMAGE_URL = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop";

// Simple in-memory user storage for testing
const users = new Map();

/**
 * Get or create user from Telegram data
 */
function getOrCreateUser(telegramUser) {
    const userId = telegramUser.id;
    if (!users.has(userId)) {
        users.set(userId, {
            telegram_id: userId,
            first_name: telegramUser.first_name || "друг",
            language_code: telegramUser.language_code || "ru",
            formal_address: false,
            onboarding_completed: false,
            notifications_enabled: true,
            active_hours_start: "09:00",
            active_hours_end: "21:00",
            notification_interval_hours: 3,
            created_at: new Date()
        });
    }
    return users.get(userId);
}

/**
 * Get localized welcome text based on user's language
 */
function getLocalizedWelcomeText(firstName, languageCode) {
    if (languageCode && languageCode.startsWith("en")) {
        return (
            `Hello, ${firstName}! 👋\n\n` +
            "I'm your assistant for developing positive thinking. " +
            "Every day I will ask you about good things, " +
            "so that we can notice the joyful moments of life together. ✨\n\n" +
            "Let's begin! How would you prefer to communicate?"
        );
    } else if (languageCode && languageCode.startsWith("uk")) {
        return (
            `Привіт, ${firstName}! 👋\n\n` +
            "Я — твій помічник для розвитку позитивного мислення. " +
            "Щодня я буду запитувати тебе про хороше, " +
            "щоб разом помічати радісні моменти життя. ✨\n\n" +
            "Давай почнемо! Як тобі зручніше спілкуватися?"
        );
    } else {
        // Default to Russian
        return (
            `Привет, ${firstName}! 👋\n\n` +
            "Я — твой помощник для развития позитивного мышления. " +
            "Каждый день я буду спрашивать тебя о хорошем, " +
            "чтобы вместе замечать радостные моменты жизни. ✨\n\n" +
            "Давай начнём! Как тебе удобнее общаться?"
        );
    }
}

/**
 * Get welcome back text
 */
function getLocalizedWelcomeBackText(firstName, languageCode) {
    if (languageCode && languageCode.startsWith("en")) {
        return `Welcome back, ${firstName}! 💝\n\nGood to see you again. How can I help?`;
    } else if (languageCode && languageCode.startsWith("uk")) {
        return `З поверненням, ${firstName}! 💝\n\nРадий знову тебе бачити. Чим можу допомогти?`;
    } else {
        return `С возвращением, ${firstName}! 💝\n\nРад снова тебя видеть. Чем могу помочь?`;
    }
}

/**
 * Send a photo message
 */
async function sendPhoto(chatId, photoUrl, caption = "") {
    const url = `${BASE_URL}/sendPhoto`;
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            chat_id: chatId,
            photo: photoUrl,
            caption: caption
        })
    });
    return await response.json();
}

/**
 * Send a text message with optional inline/reply keyboard
 */
async function sendMessage(chatId, text, replyMarkup = null, parseMode = 'HTML') {
    const url = `${BASE_URL}/sendMessage`;
    const body = {
        chat_id: chatId,
        text: text,
        parse_mode: parseMode
    };
    if (replyMarkup) {
        body.reply_markup = replyMarkup;
    }
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return await response.json();
}

/**
 * Edit an existing message
 */
async function editMessage(chatId, messageId, text, replyMarkup = null) {
    const url = `${BASE_URL}/editMessageText`;
    const body = {
        chat_id: chatId,
        message_id: messageId,
        text: text,
        parse_mode: 'HTML'
    };
    if (replyMarkup) {
        body.reply_markup = replyMarkup;
    }
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return await response.json();
}

/**
 * Answer callback query
 */
async function answerCallback(callbackQueryId, text = "") {
    const url = `${BASE_URL}/answerCallbackQuery`;
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            callback_query_id: callbackQueryId,
            text: text
        })
    });
    return await response.json();
}

// Keyboard generators
function getOnboardingKeyboard() {
    return {
        inline_keyboard: [
            [
                { text: "На «ты» 😊", callback_data: "address_informal" },
                { text: "На «вы» 🤝", callback_data: "address_formal" }
            ]
        ]
    };
}

function getMainMenuInline() {
    return {
        inline_keyboard: [
            [
                { text: "📖 Мои моменты", callback_data: "menu_moments" },
                { text: "📊 Статистика", callback_data: "menu_stats" }
            ],
            [
                { text: "⚙️ Настройки", callback_data: "menu_settings" },
                { text: "💬 Поговорить", callback_data: "menu_talk" }
            ]
        ]
    };
}

function getMainMenuKeyboard() {
    return {
        keyboard: [
            [{ text: "📖 Мои моменты" }, { text: "📊 Статистика" }],
            [{ text: "⚙️ Настройки" }, { text: "💬 Поговорить" }]
        ],
        resize_keyboard: true,
        is_persistent: true
    };
}

function getSettingsKeyboard() {
    return {
        inline_keyboard: [
            [{ text: "🕐 Активные часы", callback_data: "settings_hours" }],
            [{ text: "⏰ Интервал", callback_data: "settings_interval" }],
            [{ text: "🗣 Форма обращения", callback_data: "settings_address" }],
            [{ text: "🔔 Уведомления", callback_data: "settings_notifications" }],
            [{ text: "🌍 Язык", callback_data: "settings_language" }],
            [{ text: "🔄 Сбросить настройки", callback_data: "settings_reset" }],
            [{ text: "⬅️ Назад", callback_data: "main_menu" }]
        ]
    };
}

function getHoursStartKeyboard() {
    return {
        inline_keyboard: [
            [
                { text: "06:00", callback_data: "hours_start_06" },
                { text: "07:00", callback_data: "hours_start_07" },
                { text: "08:00", callback_data: "hours_start_08" }
            ],
            [
                { text: "09:00", callback_data: "hours_start_09" },
                { text: "10:00", callback_data: "hours_start_10" },
                { text: "11:00", callback_data: "hours_start_11" }
            ],
            [
                { text: "12:00", callback_data: "hours_start_12" }
            ],
            [{ text: "⬅️ Назад", callback_data: "settings_back" }]
        ]
    };
}

function getHoursEndKeyboard() {
    return {
        inline_keyboard: [
            [
                { text: "18:00", callback_data: "hours_end_18" },
                { text: "19:00", callback_data: "hours_end_19" },
                { text: "20:00", callback_data: "hours_end_20" }
            ],
            [
                { text: "21:00", callback_data: "hours_end_21" },
                { text: "22:00", callback_data: "hours_end_22" },
                { text: "23:00", callback_data: "hours_end_23" }
            ],
            [{ text: "⬅️ Назад", callback_data: "settings_back" }]
        ]
    };
}

function getIntervalKeyboard() {
    return {
        inline_keyboard: [
            [
                { text: "2 часа", callback_data: "interval_2" },
                { text: "3 часа", callback_data: "interval_3" },
                { text: "4 часа", callback_data: "interval_4" }
            ],
            [
                { text: "6 часов", callback_data: "interval_6" },
                { text: "8 часов", callback_data: "interval_8" },
                { text: "12 часов", callback_data: "interval_12" }
            ],
            [{ text: "⬅️ Назад", callback_data: "settings_back" }]
        ]
    };
}

function getLanguageKeyboard() {
    return {
        inline_keyboard: [
            [{ text: "🇷🇺 Русский", callback_data: "lang_ru" }],
            [{ text: "🇬🇧 English", callback_data: "lang_en" }],
            [{ text: "🇺🇦 Українська", callback_data: "lang_uk" }],
            [{ text: "⬅️ Назад", callback_data: "settings_back" }]
        ]
    };
}

/**
 * Get updates from Telegram
 */
async function getUpdates(offset = null) {
    let url = `${BASE_URL}/getUpdates?timeout=30`;
    if (offset) {
        url += `&offset=${offset}`;
    }
    const response = await fetch(url);
    return await response.json();
}

/**
 * Handle /start command
 */
async function handleStartCommand(message) {
    const chatId = message.chat.id;
    const telegramUser = message.from;
    const user = getOrCreateUser(telegramUser);

    console.log(`\n=== Processing /start command ===`);
    console.log(`User: ${user.first_name} (ID: ${user.telegram_id})`);
    console.log(`Language: ${user.language_code}`);
    console.log(`Onboarding completed: ${user.onboarding_completed}`);

    if (!user.onboarding_completed) {
        // New user - send welcome image first
        console.log("Sending welcome image...");
        const photoResult = await sendPhoto(chatId, WELCOME_IMAGE_URL);
        if (photoResult.ok) {
            console.log("✅ Welcome image sent successfully");
        } else {
            console.log("⚠️ Could not send welcome image:", photoResult.description);
        }

        // Send welcome message with inline keyboard
        const welcomeText = getLocalizedWelcomeText(user.first_name, user.language_code);
        console.log("Sending welcome message with address selection...");
        const msgResult = await sendMessage(chatId, welcomeText, getOnboardingKeyboard());
        if (msgResult.ok) {
            console.log("✅ Welcome message sent successfully");
            console.log("✅ Address form selection (ты/вы) keyboard shown");
        } else {
            console.log("❌ Failed to send welcome message:", msgResult.description);
        }
    } else {
        // Existing user - welcome back
        const welcomeBackText = getLocalizedWelcomeBackText(user.first_name, user.language_code);
        console.log("Sending welcome back message...");
        const msgResult = await sendMessage(chatId, welcomeBackText, getMainMenuKeyboard());
        if (msgResult.ok) {
            console.log("✅ Welcome back message sent successfully");
        }
    }
}

/**
 * Handle /help command
 */
async function handleHelpCommand(message) {
    const chatId = message.chat.id;
    const helpText = (
        "📚 <b>Команды бота</b>\n\n" +
        "/start - Начать заново\n" +
        "/help - Показать эту справку\n" +
        "/moments - Просмотреть историю моментов\n" +
        "/stats - Посмотреть статистику\n" +
        "/settings - Настройки\n" +
        "/talk - Начать свободный диалог\n" +
        "/privacy - Политика конфиденциальности\n" +
        "/export_data - Экспортировать свои данные\n" +
        "/delete_data - Удалить все свои данные\n\n" +
        "💡 <b>Как это работает</b>\n" +
        "Каждые несколько часов я спрошу тебя: «Что хорошего произошло?» " +
        "Ты можешь ответить текстом или голосовым сообщением. " +
        "Я сохраню твои радостные моменты и напомню о них, " +
        "когда будет нужна поддержка. 🌟"
    );
    await sendMessage(chatId, helpText, getMainMenuKeyboard());
    console.log("✅ Help message sent");
}

/**
 * Handle /settings command
 */
async function handleSettingsCommand(message) {
    const chatId = message.chat.id;
    const user = getOrCreateUser(message.from);

    const languageNames = {
        'ru': 'Русский',
        'en': 'English',
        'uk': 'Українська'
    };
    const settingsText = (
        "⚙️ <b>Настройки</b>\n\n" +
        `🕐 Активные часы: ${user.active_hours_start} - ${user.active_hours_end}\n` +
        `⏰ Интервал: каждые ${user.notification_interval_hours} ч.\n` +
        `🗣 Обращение: ${user.formal_address ? 'на «вы»' : 'на «ты»'}\n` +
        `🔔 Уведомления: ${user.notifications_enabled ? 'включены' : 'выключены'}\n` +
        `🌍 Язык: ${languageNames[user.language_code] || user.language_code}\n`
    );
    await sendMessage(chatId, settingsText, getSettingsKeyboard());
    console.log("✅ Settings message sent");
}

/**
 * Handle /privacy command
 */
async function handlePrivacyCommand(message) {
    const chatId = message.chat.id;
    const privacyText = (
        "🔒 <b>Политика конфиденциальности</b>\n\n" +
        "Я храню твои данные только для того, чтобы делать наше общение " +
        "более персональным и полезным для тебя.\n\n" +
        "<b>Что я сохраняю:</b>\n" +
        "• Твои ответы о хороших моментах\n" +
        "• Историю наших диалогов\n" +
        "• Настройки (часы, интервал, язык)\n\n" +
        "<b>Как использую:</b>\n" +
        "• Только для персонализации нашего общения\n" +
        "• Чтобы напоминать тебе о прошлых радостях\n" +
        "• Данные НЕ передаются третьим лицам\n\n" +
        "<b>Твои права:</b>\n" +
        "• /export_data — скачать все свои данные\n" +
        "• /delete_data — полностью удалить всё\n\n" +
        "Вопросы? Напиши мне в свободном диалоге! 💝"
    );
    await sendMessage(chatId, privacyText);
    console.log("✅ Privacy policy sent");
}

/**
 * Handle /stats command
 */
async function handleStatsCommand(message) {
    const chatId = message.chat.id;
    const user = getOrCreateUser(message.from);

    // Simple stats for testing
    const statsText = (
        "📊 <b>Твоя статистика</b>\n\n" +
        "🌟 Всего моментов: 0\n" +
        "🔥 Текущий стрик: 0 дн.\n" +
        "🏆 Лучший стрик: 0 дн.\n" +
        "✉️ Отправлено вопросов: 0\n" +
        "✅ Отвечено: 0\n"
    );
    await sendMessage(chatId, statsText);
    console.log("✅ Stats message sent");
}

/**
 * Handle /moments command
 */
async function handleMomentsCommand(message) {
    const chatId = message.chat.id;
    const momentsText = (
        "📖 У тебя пока нет сохранённых моментов.\n" +
        "Когда придёт время вопроса, поделись чем-то хорошим! 🌟"
    );
    await sendMessage(chatId, momentsText);
    console.log("✅ Moments message sent");
}

/**
 * Handle address selection callbacks
 */
async function handleAddressCallback(callback, formal) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);

    user.formal_address = formal;
    user.onboarding_completed = true;

    console.log(`\n=== Processing address selection ===`);
    console.log(`User: ${user.first_name} selected ${formal ? 'formal (вы)' : 'informal (ты)'}`);

    let onboardingCompleteText;
    if (formal) {
        onboardingCompleteText = (
            "Хорошо! Буду обращаться на «вы» 😊\n\n" +
            "Теперь немного о том, как это работает:\n\n" +
            "• Каждые несколько часов я спрошу: «Что хорошего произошло?»\n" +
            "• Вы можете ответить текстом или голосовым сообщением\n" +
            "• Я сохраню Ваши моменты и напомню о них, когда понадобится поддержка\n\n" +
            "🔒 Ваши данные в безопасности и используются только для нашего общения.\n" +
            "Подробнее: /privacy"
        );
    } else {
        onboardingCompleteText = (
            "Отлично! Буду обращаться на «ты» 😊\n\n" +
            "Теперь немного о том, как это работает:\n\n" +
            "• Каждые несколько часов я спрошу: «Что хорошего произошло?»\n" +
            "• Ты можешь ответить текстом или голосовым сообщением\n" +
            "• Я сохраню твои моменты и напомню о них, когда понадобится поддержка\n\n" +
            "🔒 Твои данные в безопасности и используются только для нашего общения.\n" +
            "Подробнее: /privacy"
        );
    }

    // Edit the original message to show onboarding complete info
    const editResult = await editMessage(chatId, messageId, onboardingCompleteText, getMainMenuInline());

    if (editResult.ok) {
        console.log("✅ Privacy policy / bot explanation shown");
        console.log("✅ Main menu keyboard shown");
        console.log("✅ Onboarding marked as completed");
        console.log(`✅ User saved: formal_address=${user.formal_address}, onboarding_completed=${user.onboarding_completed}`);
    } else {
        console.log("❌ Failed to edit message:", editResult.description);
    }

    await answerCallback(callback.id);
}

/**
 * Handle main menu callbacks
 */
async function handleMainMenuCallback(callback, action) {
    const chatId = callback.message.chat.id;
    const user = getOrCreateUser(callback.from);

    console.log(`\n=== Processing menu action: ${action} ===`);

    switch (action) {
        case "menu_moments":
            await sendMessage(chatId,
                "📖 У тебя пока нет сохранённых моментов.\n" +
                "Когда придёт время вопроса, поделись чем-то хорошим! 🌟"
            );
            break;
        case "menu_stats":
            await sendMessage(chatId,
                "📊 <b>Твоя статистика</b>\n\n" +
                "🌟 Всего моментов: 0\n" +
                "🔥 Текущий стрик: 0 дн.\n" +
                "🏆 Лучший стрик: 0 дн.\n"
            );
            break;
        case "menu_settings":
            await handleSettingsCommand({ chat: { id: chatId }, from: callback.from });
            break;
        case "menu_talk":
            await sendMessage(chatId,
                "💬 <b>Режим диалога</b>\n\n" +
                "Я готов выслушать тебя. Расскажи, что у тебя на душе. " +
                "Я постараюсь помочь взглядом со стороны, " +
                "но помни — все решения принимаешь ты сам. 💝\n\n" +
                "Чтобы выйти из режима диалога, напиши /start"
            );
            break;
    }

    await answerCallback(callback.id);
}

/**
 * Handle settings menu callbacks
 */
async function handleSettingsCallback(callback, action) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);

    console.log(`\n=== Processing settings action: ${action} ===`);

    switch (action) {
        case "settings_hours":
            await editMessage(chatId, messageId,
                "🕐 <b>Начало активных часов</b>\n\n" +
                `Текущее значение: ${user.active_hours_start}\n\n` +
                "Выберите время начала:",
                getHoursStartKeyboard()
            );
            break;
        case "settings_interval":
            await editMessage(chatId, messageId,
                "⏰ <b>Интервал между вопросами</b>\n\n" +
                `Текущее значение: каждые ${user.notification_interval_hours} ч.\n\n` +
                "Выберите интервал:",
                getIntervalKeyboard()
            );
            break;
        case "settings_address":
            await editMessage(chatId, messageId,
                "🗣 <b>Форма обращения</b>\n\n" +
                `Текущее значение: ${user.formal_address ? 'на «вы»' : 'на «ты»'}\n\n` +
                "Выберите форму:",
                {
                    inline_keyboard: [
                        [{ text: "На «ты» 😊", callback_data: "address_change_informal" }],
                        [{ text: "На «вы» 🤝", callback_data: "address_change_formal" }],
                        [{ text: "⬅️ Назад", callback_data: "settings_back" }]
                    ]
                }
            );
            break;
        case "settings_notifications":
            user.notifications_enabled = !user.notifications_enabled;
            console.log(`✅ Notifications toggled to: ${user.notifications_enabled}`);
            // Show updated settings
            await showSettings(chatId, messageId, user);
            break;
        case "settings_language":
            await editMessage(chatId, messageId,
                "🌍 <b>Язык интерфейса</b>\n\n" +
                `Текущий язык: ${user.language_code}\n\n` +
                "Выберите язык:",
                getLanguageKeyboard()
            );
            break;
        case "settings_reset":
            user.active_hours_start = "09:00";
            user.active_hours_end = "21:00";
            user.notification_interval_hours = 3;
            user.notifications_enabled = true;
            console.log("✅ Settings reset to defaults");
            await showSettings(chatId, messageId, user);
            break;
        case "settings_back":
            await showSettings(chatId, messageId, user);
            break;
    }

    await answerCallback(callback.id);
}

/**
 * Helper function to show settings
 */
async function showSettings(chatId, messageId, user) {
    const languageNames = {
        'ru': 'Русский',
        'en': 'English',
        'uk': 'Українська'
    };
    const settingsText = (
        "⚙️ <b>Настройки</b>\n\n" +
        `🕐 Активные часы: ${user.active_hours_start} - ${user.active_hours_end}\n` +
        `⏰ Интервал: каждые ${user.notification_interval_hours} ч.\n` +
        `🗣 Обращение: ${user.formal_address ? 'на «вы»' : 'на «ты»'}\n` +
        `🔔 Уведомления: ${user.notifications_enabled ? 'включены' : 'выключены'}\n` +
        `🌍 Язык: ${languageNames[user.language_code] || user.language_code}\n`
    );
    await editMessage(chatId, messageId, settingsText, getSettingsKeyboard());
}

/**
 * Handle hours start selection
 */
async function handleHoursStartCallback(callback, action) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);

    const hour = action.replace("hours_start_", "");
    user.active_hours_start = `${hour}:00`;
    console.log(`✅ Active hours start set to: ${user.active_hours_start}`);

    // Now ask for end time
    await editMessage(chatId, messageId,
        "🕐 <b>Конец активных часов</b>\n\n" +
        `Начало: ${user.active_hours_start}\n\n` +
        "Выберите время окончания:",
        getHoursEndKeyboard()
    );

    await answerCallback(callback.id, "✅ Начало установлено");
}

/**
 * Handle hours end selection
 */
async function handleHoursEndCallback(callback, action) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);

    const hour = action.replace("hours_end_", "");
    user.active_hours_end = `${hour}:00`;
    console.log(`✅ Active hours end set to: ${user.active_hours_end}`);
    console.log(`✅ Active hours saved: ${user.active_hours_start} - ${user.active_hours_end}`);

    // Show updated settings
    await showSettings(chatId, messageId, user);
    await answerCallback(callback.id, "✅ Часы сохранены!");
}

/**
 * Handle interval selection
 */
async function handleIntervalCallback(callback, action) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);

    const interval = parseInt(action.replace("interval_", ""));
    user.notification_interval_hours = interval;
    console.log(`✅ Notification interval set to: ${interval} hours`);

    // Show updated settings
    await showSettings(chatId, messageId, user);
    await answerCallback(callback.id, "✅ Интервал сохранён!");
}

/**
 * Handle language selection
 */
async function handleLanguageCallback(callback, action) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);

    const lang = action.replace("lang_", "");
    user.language_code = lang;
    console.log(`✅ Language set to: ${lang}`);

    // Show updated settings
    await showSettings(chatId, messageId, user);
    await answerCallback(callback.id, "✅ Язык сохранён!");
}

/**
 * Handle address form change
 */
async function handleAddressChangeCallback(callback, formal) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);

    user.formal_address = formal;
    console.log(`✅ Address form changed to: ${formal ? 'formal (вы)' : 'informal (ты)'}`);

    // Show updated settings
    await showSettings(chatId, messageId, user);
    await answerCallback(callback.id, formal ? "✅ Теперь на «вы»" : "✅ Теперь на «ты»");
}

/**
 * Process a single update
 */
async function processUpdate(update) {
    if (update.message && update.message.text) {
        const text = update.message.text;

        if (text === '/start') {
            await handleStartCommand(update.message);
        } else if (text === '/help') {
            await handleHelpCommand(update.message);
        } else if (text === '/settings') {
            await handleSettingsCommand(update.message);
        } else if (text === '/privacy') {
            await handlePrivacyCommand(update.message);
        } else if (text === '/stats') {
            await handleStatsCommand(update.message);
        } else if (text === '/moments') {
            await handleMomentsCommand(update.message);
        } else {
            console.log(`Received message: ${text}`);
        }
    } else if (update.callback_query) {
        const callbackData = update.callback_query.data;
        console.log(`Received callback: ${callbackData}`);

        if (callbackData === "address_informal") {
            await handleAddressCallback(update.callback_query, false);
        } else if (callbackData === "address_formal") {
            await handleAddressCallback(update.callback_query, true);
        } else if (callbackData.startsWith("menu_")) {
            await handleMainMenuCallback(update.callback_query, callbackData);
        } else if (callbackData === "main_menu") {
            const chatId = update.callback_query.message.chat.id;
            await editMessage(chatId, update.callback_query.message.message_id,
                "Чем могу помочь? 😊", getMainMenuInline());
            await answerCallback(update.callback_query.id);
        } else if (callbackData.startsWith("settings_")) {
            await handleSettingsCallback(update.callback_query, callbackData);
        } else if (callbackData.startsWith("hours_start_")) {
            await handleHoursStartCallback(update.callback_query, callbackData);
        } else if (callbackData.startsWith("hours_end_")) {
            await handleHoursEndCallback(update.callback_query, callbackData);
        } else if (callbackData.startsWith("interval_")) {
            await handleIntervalCallback(update.callback_query, callbackData);
        } else if (callbackData.startsWith("lang_")) {
            await handleLanguageCallback(update.callback_query, callbackData);
        } else if (callbackData === "address_change_informal" || callbackData === "address_change_formal") {
            await handleAddressChangeCallback(update.callback_query, callbackData === "address_change_formal");
        } else {
            await answerCallback(update.callback_query.id);
        }
    }
}

/**
 * Main polling loop
 */
async function main() {
    console.log("🤖 MindSetHappyBot Test Server Starting...");
    console.log("Checking bot connection...");

    // Verify bot connection
    const meResponse = await fetch(`${BASE_URL}/getMe`);
    const meData = await meResponse.json();
    if (meData.ok) {
        console.log(`✅ Connected as @${meData.result.username}`);
    } else {
        console.error("❌ Failed to connect to bot:", meData);
        process.exit(1);
    }

    let offset = null;

    console.log("\n📡 Polling for updates...");
    console.log("Send /start to @MindSetHappyBot in Telegram to test\n");

    while (true) {
        try {
            const updates = await getUpdates(offset);

            if (updates.ok && updates.result.length > 0) {
                for (const update of updates.result) {
                    await processUpdate(update);
                    offset = update.update_id + 1;
                }
            }
        } catch (error) {
            console.error("Error polling updates:", error.message);
            // Wait before retrying
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
    }
}

// Run the bot
main().catch(console.error);
