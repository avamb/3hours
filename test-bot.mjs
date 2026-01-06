/**
 * MINDSETHAPPYBOT - Node.js Testing Implementation
 * Full implementation for testing bot features
 */

const BOT_TOKEN = '7805611571:AAF59MdS0N3By7mMq_O53Wo8LjYLwfXVrBY';
const BASE_URL = `https://api.telegram.org/bot${BOT_TOKEN}`;

// Welcome image URL (same as Python implementation)
const WELCOME_IMAGE_URL = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop";

// Telegram message limits
const TELEGRAM_MESSAGE_LIMIT = 4096;
const MOMENT_CONTENT_LIMIT = 2000;  // Reasonable limit for moment content

// File-based persistence
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const DATA_FILE = join(__dirname, 'bot-data.json');

// Simple in-memory user storage for testing
const users = new Map();

// In-memory moments storage for testing
const moments = new Map();

// User states for conversation flow (not persisted - session only)
const userStates = new Map();

/**
 * Load data from file on startup
 */
function loadDataFromFile() {
    try {
        if (existsSync(DATA_FILE)) {
            const data = JSON.parse(readFileSync(DATA_FILE, 'utf8'));

            // Load users
            if (data.users) {
                for (const [key, value] of Object.entries(data.users)) {
                    // Convert date strings back to Date objects
                    if (value.created_at) value.created_at = new Date(value.created_at);
                    users.set(parseInt(key), value);
                }
            }

            // Load moments
            if (data.moments) {
                for (const [key, value] of Object.entries(data.moments)) {
                    // Convert date strings back to Date objects
                    const momentsArray = value.map(m => ({
                        ...m,
                        created_at: new Date(m.created_at)
                    }));
                    moments.set(parseInt(key), momentsArray);
                }
            }

            console.log(`📁 Loaded data: ${users.size} users, ${[...moments.values()].flat().length} moments`);
        } else {
            console.log(`📁 No existing data file found, starting fresh`);
        }
    } catch (error) {
        console.error(`⚠️ Error loading data file: ${error.message}`);
    }
}

/**
 * Save data to file
 */
function saveDataToFile() {
    try {
        const data = {
            users: Object.fromEntries(users),
            moments: Object.fromEntries(moments),
            savedAt: new Date().toISOString()
        };
        writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
        console.log(`💾 Data saved: ${users.size} users, ${[...moments.values()].flat().length} moments`);
    } catch (error) {
        console.error(`⚠️ Error saving data file: ${error.message}`);
    }
}

/**
 * Auto-save data periodically (every 30 seconds)
 */
function startAutoSave() {
    setInterval(() => {
        if (users.size > 0 || moments.size > 0) {
            saveDataToFile();
        }
    }, 30000);
    console.log(`⏰ Auto-save enabled (every 30 seconds)`);
}

// Load data on startup
loadDataFromFile();

// Double-submit prevention: Track processing callbacks
const processingCallbacks = new Map();

// Double-submit prevention: Track processing user actions
const processingActions = new Map();

// Double-submit prevention timeout (ms)
const DOUBLE_SUBMIT_TIMEOUT = 2000;

/**
 * Check if a callback is currently being processed (double-submit prevention)
 * @param {string} callbackId - The callback query ID
 * @returns {boolean} True if already processing
 */
function isCallbackProcessing(callbackId) {
    return processingCallbacks.has(callbackId);
}

/**
 * Mark a callback as being processed
 * @param {string} callbackId - The callback query ID
 */
function markCallbackProcessing(callbackId) {
    processingCallbacks.set(callbackId, Date.now());
    // Auto-cleanup after timeout
    setTimeout(() => {
        processingCallbacks.delete(callbackId);
    }, DOUBLE_SUBMIT_TIMEOUT);
}

/**
 * Check if a user action is currently being processed (double-submit prevention)
 * @param {number} userId - The user ID
 * @param {string} action - The action type (e.g., 'save_moment', 'delete_data')
 * @returns {boolean} True if already processing
 */
function isUserActionProcessing(userId, action) {
    const key = `${userId}:${action}`;
    const lastTime = processingActions.get(key);
    if (lastTime && (Date.now() - lastTime) < DOUBLE_SUBMIT_TIMEOUT) {
        return true;
    }
    return false;
}

/**
 * Mark a user action as being processed
 * @param {number} userId - The user ID
 * @param {string} action - The action type
 */
function markUserActionProcessing(userId, action) {
    const key = `${userId}:${action}`;
    processingActions.set(key, Date.now());
    // Auto-cleanup after timeout
    setTimeout(() => {
        processingActions.delete(key);
    }, DOUBLE_SUBMIT_TIMEOUT);
}

/**
 * Clear a user action processing status
 * @param {number} userId - The user ID
 * @param {string} action - The action type
 */
function clearUserActionProcessing(userId, action) {
    const key = `${userId}:${action}`;
    processingActions.delete(key);
}

/**
 * Localized error messages
 */
const errorMessages = {
    ru: {
        generic: "Ой, что-то пошло не так 😔\nПопробуй ещё раз или напиши /start",
        network: "Не удалось подключиться к серверу 🌐\nПроверь интернет-соединение и попробуй снова",
        voice_recognition: "Не удалось распознать голосовое сообщение 🎤\nПопробуй записать ещё раз или напиши текстом",
        empty_input: "Сообщение пустое 📝\nПопробуй написать что-нибудь хорошее! 💝",
        not_found: "Ничего не найдено 🔍\nПопробуй другой запрос",
        action_failed: "Действие не выполнено 😕\nПопробуй ещё раз через несколько секунд",
        timeout: "Это заняло слишком много времени ⏳\nПопробуй ещё раз 🔄",
        invalid_time: "Время выбрано неверно ⏰\nПопробуй выбрать из предложенных вариантов 📋"
    },
    en: {
        generic: "Oops, something went wrong 😔\nTry again or send /start",
        network: "Could not connect to the server 🌐\nCheck your internet connection and try again",
        voice_recognition: "Could not recognize voice message 🎤\nTry recording again or type your message",
        empty_input: "Message is empty 📝\nTry writing something good! 💝",
        not_found: "Nothing found 🔍\nTry a different query",
        action_failed: "Action failed 😕\nTry again in a few seconds",
        timeout: "That took too long ⏳\nTry again please 🔄",
        invalid_time: "Time selected incorrectly ⏰\nTry selecting from the options provided 📋"
    },
    uk: {
        generic: "Ой, щось пішло не так 😔\nСпробуй ще раз або напиши /start",
        network: "Не вдалося підключитися до сервера 🌐\nПеревір інтернет-з'єднання і спробуй знову",
        voice_recognition: "Не вдалося розпізнати голосове повідомлення 🎤\nСпробуй записати ще раз або напиши текстом",
        empty_input: "Повідомлення порожнє 📝\nСпробуй написати щось хороше! 💝",
        not_found: "Нічого не знайдено 🔍\nСпробуй інший запит",
        action_failed: "Дію не виконано 😕\nСпробуй ще раз через кілька секунд",
        timeout: "Це зайняло надто багато часу ⏳\nСпробуй ще раз 🔄",
        invalid_time: "Час обрано неправильно ⏰\nСпробуй обрати з запропонованих варіантів 📋"
    }
};

/**
 * Escape HTML special characters to prevent XSS
 * Telegram uses HTML parse mode, so user content must be escaped
 * @param {string} text - Text to escape
 * @returns {string} HTML-escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Truncate text to specified length with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @param {string} suffix - Suffix to add when truncated (default: '...')
 * @returns {string} Truncated text
 */
function truncateText(text, maxLength, suffix = '...') {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * Split long message into multiple parts for Telegram
 * Tries to split at sentence boundaries when possible
 * @param {string} text - Text to split
 * @param {number} maxLength - Maximum length per part (default: TELEGRAM_MESSAGE_LIMIT)
 * @returns {string[]} Array of message parts
 */
function splitLongMessage(text, maxLength = TELEGRAM_MESSAGE_LIMIT) {
    if (!text) return [''];
    if (text.length <= maxLength) return [text];

    const parts = [];
    let remaining = text;

    while (remaining.length > 0) {
        if (remaining.length <= maxLength) {
            parts.push(remaining);
            break;
        }

        // Try to find a good split point (sentence end or paragraph)
        let splitPoint = maxLength;

        // Look for paragraph break
        const paragraphBreak = remaining.lastIndexOf('\n\n', maxLength);
        if (paragraphBreak > maxLength * 0.5) {
            splitPoint = paragraphBreak + 2;
        } else {
            // Look for sentence end
            const sentenceEnd = remaining.lastIndexOf('. ', maxLength);
            if (sentenceEnd > maxLength * 0.5) {
                splitPoint = sentenceEnd + 2;
            } else {
                // Look for any newline
                const newline = remaining.lastIndexOf('\n', maxLength);
                if (newline > maxLength * 0.5) {
                    splitPoint = newline + 1;
                } else {
                    // Look for space
                    const space = remaining.lastIndexOf(' ', maxLength);
                    if (space > maxLength * 0.5) {
                        splitPoint = space + 1;
                    }
                }
            }
        }

        parts.push(remaining.substring(0, splitPoint).trim());
        remaining = remaining.substring(splitPoint).trim();
    }

    return parts;
}

/**
 * Get localized error message
 * @param {string} errorType - Type of error (generic, network, voice_recognition, etc.)
 * @param {string} languageCode - User's language code
 * @returns {string} Localized error message
 */
function getErrorMessage(errorType, languageCode = 'ru') {
    const lang = errorMessages[languageCode] ? languageCode : 'ru';
    return errorMessages[lang][errorType] || errorMessages[lang].generic;
}

/**
 * Send error message to user
 * @param {number} chatId - Chat ID to send message to
 * @param {string} errorType - Type of error
 * @param {string} languageCode - User's language code
 */
async function sendErrorMessage(chatId, errorType, languageCode = 'ru') {
    const message = getErrorMessage(errorType, languageCode);
    await sendMessage(chatId, message, {
        inline_keyboard: [
            [{ text: "🔄 Попробовать снова", callback_data: "main_menu" }],
            [{ text: "❓ Помощь", callback_data: "help" }]
        ]
    });
    console.log(`⚠️ Error message sent: ${errorType} (${languageCode})`);
}

/**
 * Format date according to user's locale
 * @param {Date} date - The date to format
 * @param {string} languageCode - User's language code (ru, en, uk)
 * @param {boolean} includeTime - Whether to include time
 * @returns {string} Formatted date string
 */
function formatDate(date, languageCode = 'ru', includeTime = false) {
    const locale = languageCode === 'uk' ? 'uk-UA' :
                   languageCode === 'en' ? 'en-US' : 'ru-RU';

    const options = {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    };

    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }

    return date.toLocaleDateString(locale, options);
}

/**
 * Format relative date (today, yesterday, etc.)
 * @param {Date} date - The date to format
 * @param {string} languageCode - User's language code
 * @returns {string} Relative date string
 */
function formatRelativeDate(date, languageCode = 'ru') {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const dateDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const diffDays = Math.floor((today - dateDay) / (1000 * 60 * 60 * 24));

    const texts = {
        ru: { today: 'Сегодня', yesterday: 'Вчера', daysAgo: 'дн. назад' },
        en: { today: 'Today', yesterday: 'Yesterday', daysAgo: 'days ago' },
        uk: { today: 'Сьогодні', yesterday: 'Вчора', daysAgo: 'дн. тому' }
    };

    const t = texts[languageCode] || texts.ru;

    if (diffDays === 0) return t.today;
    if (diffDays === 1) return t.yesterday;
    if (diffDays < 7) return `${diffDays} ${t.daysAgo}`;

    return formatDate(date, languageCode, false);
}

/**
 * Add a moment to user's history
 */
function addMoment(userId, content) {
    if (!moments.has(userId)) {
        moments.set(userId, []);
    }
    const userMoments = moments.get(userId);
    userMoments.push({
        id: userMoments.length + 1,
        content: content,
        created_at: new Date()
    });
    // Save data immediately after adding a moment
    saveDataToFile();
    return userMoments[userMoments.length - 1];
}

/**
 * Get user's moments
 */
function getUserMoments(userId) {
    return moments.get(userId) || [];
}

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
        // Save data when new user is created
        saveDataToFile();
    }
    return users.get(userId);
}

/**
 * Get localized welcome text based on user's language
 */
function getLocalizedWelcomeText(firstName, languageCode) {
    const safeName = escapeHtml(firstName);
    if (languageCode && languageCode.startsWith("en")) {
        return (
            `Hello, ${safeName}! 👋\n\n` +
            "I'm your assistant for developing positive thinking. " +
            "Every day I will ask you about good things, " +
            "so that we can notice the joyful moments of life together. ✨\n\n" +
            "Let's begin! How would you prefer to communicate?"
        );
    } else if (languageCode && languageCode.startsWith("uk")) {
        return (
            `Привіт, ${safeName}! 👋\n\n` +
            "Я — твій помічник для розвитку позитивного мислення. " +
            "Щодня я буду запитувати тебе про хороше, " +
            "щоб разом помічати радісні моменти життя. ✨\n\n" +
            "Давай почнемо! Як тобі зручніше спілкуватися?"
        );
    } else {
        // Default to Russian
        return (
            `Привет, ${safeName}! 👋\n\n` +
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
    const safeName = escapeHtml(firstName);
    if (languageCode && languageCode.startsWith("en")) {
        return `Welcome back, ${safeName}! 💝\n\nGood to see you again. How can I help?`;
    } else if (languageCode && languageCode.startsWith("uk")) {
        return `З поверненням, ${safeName}! 💝\n\nРадий знову тебе бачити. Чим можу допомогти?`;
    } else {
        return `С возвращением, ${safeName}! 💝\n\nРад снова тебя видеть. Чем могу помочь?`;
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

    // Handle very long messages by splitting them
    if (text.length > TELEGRAM_MESSAGE_LIMIT) {
        console.log(`⚠️ Message too long (${text.length} chars), splitting into parts`);
        const parts = splitLongMessage(text, TELEGRAM_MESSAGE_LIMIT - 100); // Leave room for formatting
        let lastResult = null;

        for (let i = 0; i < parts.length; i++) {
            const isLastPart = i === parts.length - 1;
            const body = {
                chat_id: chatId,
                text: parts[i],
                parse_mode: parseMode
            };
            // Only add keyboard to last message
            if (isLastPart && replyMarkup) {
                body.reply_markup = replyMarkup;
            }
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            lastResult = await response.json();

            // Small delay between messages to avoid rate limiting
            if (!isLastPart) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }
        console.log(`✅ Message split into ${parts.length} parts`);
        return lastResult;
    }

    // Normal message sending
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
 * Handle deep link parameters
 * Deep link format: https://t.me/MindSetHappyBot?start=ACTION
 * Supported actions:
 * - moments: Open moments list
 * - stats: Open statistics
 * - settings: Open settings
 * - talk: Start free dialog
 * - add: Add a new moment
 * - share_REF: Handle sharing/referral (future use)
 *
 * @param {number} chatId - Chat ID
 * @param {object} user - User object
 * @param {string} param - Deep link parameter
 * @returns {boolean} True if deep link was handled
 */
async function handleDeepLink(chatId, user, param) {
    console.log(`Processing deep link: ${param}`);

    // Normalize parameter (lowercase, trim)
    const action = param.toLowerCase().trim();

    switch (action) {
        case 'moments':
            console.log("Deep link action: Opening moments list");
            await handleMomentsCommand({ chat: { id: chatId }, from: { id: user.telegram_id } });
            return true;

        case 'stats':
        case 'statistics':
            console.log("Deep link action: Opening statistics");
            await handleStatsCommand({ chat: { id: chatId }, from: { id: user.telegram_id } });
            return true;

        case 'settings':
            console.log("Deep link action: Opening settings");
            await handleSettingsCommand({ chat: { id: chatId }, from: { id: user.telegram_id } });
            return true;

        case 'talk':
        case 'dialog':
            console.log("Deep link action: Starting free dialog");
            await sendMessage(chatId,
                "💬 <b>Режим диалога</b>\n\n" +
                "Я готов выслушать тебя. Расскажи, что у тебя на душе. " +
                "Я постараюсь помочь взглядом со стороны, " +
                "но помни — все решения принимаешь ты сам. 💝\n\n" +
                "Чтобы выйти из режима диалога, напиши /start",
                getMainMenuKeyboard()
            );
            return true;

        case 'add':
        case 'moment':
            console.log("Deep link action: Adding new moment");
            // Set user state to "adding moment"
            userStates.set(user.telegram_id, { state: 'adding_moment' });
            await sendMessage(chatId,
                "✨ <b>Добавление момента</b>\n\n" +
                "Расскажи, что хорошего произошло? " +
                "Просто напиши сообщение, и я сохраню его.\n\n" +
                "💡 Можно отправить текст или голосовое сообщение.",
                {
                    inline_keyboard: [
                        [{ text: "❌ Отмена", callback_data: "moments_cancel" }]
                    ]
                }
            );
            return true;

        case 'privacy':
            console.log("Deep link action: Opening privacy policy");
            await handlePrivacyCommand({ chat: { id: chatId }, from: { id: user.telegram_id } });
            return true;

        case 'help':
            console.log("Deep link action: Opening help");
            await handleHelpCommand({ chat: { id: chatId }, from: { id: user.telegram_id } });
            return true;

        default:
            // Check for share/referral links
            if (action.startsWith('share_') || action.startsWith('ref_')) {
                const refCode = action.split('_')[1];
                console.log(`Deep link action: Referral code ${refCode}`);
                // For now, just acknowledge and continue to normal start
                await sendMessage(chatId,
                    `🎁 Спасибо за переход по ссылке! Добро пожаловать! 💝`,
                    getMainMenuKeyboard()
                );
                return true;
            }

            console.log(`Unknown deep link action: ${action}`);
            return false; // Not handled, continue with normal start flow
    }
}

/**
 * Handle /start command
 */
async function handleStartCommand(message, deepLinkParam = null) {
    const chatId = message.chat.id;
    const telegramUser = message.from;
    const user = getOrCreateUser(telegramUser);

    console.log(`\n=== Processing /start command ===`);
    console.log(`User: ${user.first_name} (ID: ${user.telegram_id})`);
    console.log(`Language: ${user.language_code}`);
    console.log(`Onboarding completed: ${user.onboarding_completed}`);
    if (deepLinkParam) {
        console.log(`Deep link parameter: ${deepLinkParam}`);
    }

    // Handle deep link actions
    if (deepLinkParam && user.onboarding_completed) {
        const handled = await handleDeepLink(chatId, user, deepLinkParam);
        if (handled) {
            return; // Deep link was handled, don't show normal start flow
        }
    }

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
 * Handle /delete_data command (GDPR compliance)
 */
async function handleDeleteDataCommand(message) {
    const chatId = message.chat.id;
    const user = getOrCreateUser(message.from);

    const deleteText = (
        "🗑️ <b>Удаление данных</b>\n\n" +
        "Ты собираешься удалить все свои данные:\n" +
        "• Все сохранённые моменты\n" +
        "• Историю диалогов\n" +
        "• Настройки\n\n" +
        "⚠️ <b>Это действие необратимо!</b>\n\n" +
        "Уверен, что хочешь удалить все данные?"
    );

    await sendMessage(chatId, deleteText, {
        inline_keyboard: [
            [{ text: "✅ Да, удалить всё", callback_data: "delete_confirm" }],
            [{ text: "❌ Нет, отменить", callback_data: "main_menu" }]
        ]
    });
    console.log("✅ Delete data confirmation requested");
}

/**
 * Handle delete confirmation callback
 */
async function handleDeleteConfirmCallback(callback) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);

    // Double-submit prevention: Check if already deleting
    if (isUserActionProcessing(user.telegram_id, 'delete_data')) {
        console.log(`⚠️ Double-submit prevented: delete_data for user ${user.telegram_id}`);
        await answerCallback(callback.id, "⏳ Подожди...");
        return;
    }
    markUserActionProcessing(user.telegram_id, 'delete_data');

    // Delete user data
    moments.delete(user.telegram_id);
    users.delete(user.telegram_id);
    userStates.delete(user.telegram_id);
    // Save data after deletion
    saveDataToFile();

    const successText = (
        "✅ <b>Данные удалены!</b>\n\n" +
        "Все твои данные были полностью удалены:\n" +
        "• Моменты ✓\n" +
        "• История диалогов ✓\n" +
        "• Настройки ✓\n\n" +
        "Если захочешь вернуться, просто напиши /start 💝"
    );

    await editMessage(chatId, messageId, successText, {
        inline_keyboard: [
            [{ text: "🔄 Начать заново", callback_data: "restart" }]
        ]
    });
    await answerCallback(callback.id, "✅ Данные удалены");
    console.log(`✅ All data deleted for user ${user.telegram_id}`);
}

/**
 * Handle /export_data command (GDPR compliance)
 */
async function handleExportDataCommand(message) {
    const chatId = message.chat.id;
    const user = getOrCreateUser(message.from);
    const userMoments = getUserMoments(user.telegram_id);

    // Build export data
    let exportText = "📦 <b>Твои данные</b>\n\n";
    exportText += "<b>Профиль:</b>\n";
    exportText += `• Имя: ${escapeHtml(user.first_name)}\n`;
    exportText += `• Язык: ${user.language_code}\n`;
    exportText += `• Обращение: ${user.formal_address ? 'на «вы»' : 'на «ты»'}\n`;
    exportText += `• Активные часы: ${user.active_hours_start} - ${user.active_hours_end}\n`;
    exportText += `• Интервал: ${user.notification_interval_hours} ч.\n`;
    exportText += `• Уведомления: ${user.notifications_enabled ? 'вкл' : 'выкл'}\n`;
    exportText += `• Регистрация: ${formatDate(user.created_at, user.language_code)}\n\n`;

    exportText += `<b>Моменты (${userMoments.length}):</b>\n`;

    if (userMoments.length === 0) {
        exportText += "Пока нет сохранённых моментов.\n";
    } else {
        for (const moment of userMoments.slice(-10)) {
            const date = formatDate(moment.created_at, user.language_code, true);
            exportText += `\n📅 ${date}\n${escapeHtml(moment.content)}\n`;
        }
        if (userMoments.length > 10) {
            exportText += `\n... и ещё ${userMoments.length - 10} моментов`;
        }
    }

    exportText += "\n\n✅ <b>Экспорт завершён!</b>";

    await sendMessage(chatId, exportText);
    console.log(`✅ Data exported for user ${user.telegram_id}`);
}

/**
 * Handle /stats command
 */
async function handleStatsCommand(message) {
    const chatId = message.chat.id;
    const user = getOrCreateUser(message.from);
    const userMoments = getUserMoments(user.telegram_id);

    // Calculate stats
    const totalMoments = userMoments.length;
    const registrationDate = formatDate(user.created_at, user.language_code, false);

    // Find first and last moment dates
    let firstMomentDate = null;
    let lastMomentDate = null;

    if (totalMoments > 0) {
        firstMomentDate = formatDate(userMoments[0].created_at, user.language_code, false);
        lastMomentDate = formatRelativeDate(userMoments[userMoments.length - 1].created_at, user.language_code);
    }

    // Build stats text
    let statsText = "📊 <b>Твоя статистика</b>\n\n";
    statsText += `🌟 Всего моментов: ${totalMoments}\n`;
    statsText += "🔥 Текущий стрик: 0 дн.\n";
    statsText += "🏆 Лучший стрик: 0 дн.\n";
    statsText += "✉️ Отправлено вопросов: 0\n";
    statsText += "✅ Отвечено: 0\n\n";

    statsText += "📅 <b>Даты</b>\n";
    statsText += `📝 Регистрация: ${registrationDate}\n`;

    if (firstMomentDate) {
        statsText += `🌱 Первый момент: ${firstMomentDate}\n`;
        statsText += `✨ Последний момент: ${lastMomentDate}\n`;
    }

    await sendMessage(chatId, statsText, getStatsKeyboard());
    console.log("✅ Stats message sent");
}

/**
 * Get statistics keyboard
 */
function getStatsKeyboard() {
    return {
        inline_keyboard: [
            [{ text: "📅 За неделю", callback_data: "stats_week" }],
            [{ text: "📆 За месяц", callback_data: "stats_month" }],
            [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
        ]
    };
}

/**
 * Handle /moments command
 */
async function handleMomentsCommand(message) {
    const chatId = message.chat.id;
    const user = getOrCreateUser(message.from);
    const userMoments = getUserMoments(user.telegram_id);

    if (userMoments.length === 0) {
        const emptyText = (
            "📖 У тебя пока нет сохранённых моментов.\n" +
            "Когда придёт время вопроса, поделись чем-то хорошим! 🌟"
        );
        await sendMessage(chatId, emptyText, getMomentsKeyboard(user.telegram_id, 0));
        console.log("✅ Moments message sent (empty)");
        return;
    }

    // Show last 5 moments with dates
    const recentMoments = userMoments.slice(-5).reverse();
    let momentsText = "📖 <b>Твои радостные моменты</b>\n\n";

    for (const moment of recentMoments) {
        const relativeDate = formatRelativeDate(moment.created_at, user.language_code);
        const fullDate = formatDate(moment.created_at, user.language_code, true);
        momentsText += `🌟 <i>${relativeDate}</i>\n`;
        momentsText += `${escapeHtml(moment.content)}\n`;
        momentsText += `<code>${fullDate}</code>\n\n`;
    }

    if (userMoments.length > 5) {
        momentsText += `\n📚 Всего моментов: ${userMoments.length}`;
    }

    await sendMessage(chatId, momentsText, getMomentsKeyboard(user.telegram_id, userMoments.length));
    console.log(`✅ Moments message sent (${userMoments.length} moments)`);
}

/**
 * Get moments keyboard with navigation
 */
function getMomentsKeyboard(userId, totalMoments) {
    const keyboard = {
        inline_keyboard: []
    };

    if (totalMoments > 0) {
        keyboard.inline_keyboard.push([
            { text: "🎲 Случайный момент", callback_data: "moments_random" }
        ]);
    }

    keyboard.inline_keyboard.push([
        { text: "➕ Добавить момент", callback_data: "moments_add" }
    ]);

    keyboard.inline_keyboard.push([
        { text: "⬅️ Главное меню", callback_data: "main_menu" }
    ]);

    return keyboard;
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
    saveDataToFile(); // Persist settings change

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
            saveDataToFile(); // Persist settings change
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
            saveDataToFile(); // Persist settings change
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
    saveDataToFile(); // Persist settings change
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
    saveDataToFile(); // Persist settings change
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
    saveDataToFile(); // Persist settings change
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
    saveDataToFile(); // Persist settings change
    console.log(`✅ Address form changed to: ${formal ? 'formal (вы)' : 'informal (ты)'}`);

    // Show updated settings
    await showSettings(chatId, messageId, user);
    await answerCallback(callback.id, formal ? "✅ Теперь на «вы»" : "✅ Теперь на «ты»");
}

/**
 * Handle moments-related callbacks
 */
async function handleMomentsCallback(callback, action) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);
    const userMoments = getUserMoments(user.telegram_id);

    if (action === "moments_add") {
        // Set user state to "adding moment"
        userStates.set(user.telegram_id, { state: 'adding_moment' });

        await editMessage(chatId, messageId,
            "✨ <b>Добавление момента</b>\n\n" +
            "Расскажи, что хорошего произошло? " +
            "Просто напиши сообщение, и я сохраню его.\n\n" +
            "💡 Можно отправить текст или голосовое сообщение.",
            {
                inline_keyboard: [
                    [{ text: "❌ Отмена", callback_data: "moments_cancel" }]
                ]
            }
        );
        console.log("✅ Prompted user to add moment");
    } else if (action === "moments_cancel") {
        // Clear user state
        userStates.delete(user.telegram_id);

        // Return to moments view
        await handleMomentsCommand({ chat: { id: chatId }, from: callback.from });
    } else if (action === "moments_random") {
        if (userMoments.length === 0) {
            await answerCallback(callback.id, "У тебя пока нет моментов");
            return;
        }

        const randomMoment = userMoments[Math.floor(Math.random() * userMoments.length)];
        const relativeDate = formatRelativeDate(randomMoment.created_at, user.language_code);
        const fullDate = formatDate(randomMoment.created_at, user.language_code, true);

        await editMessage(chatId, messageId,
            "🎲 <b>Случайный момент</b>\n\n" +
            `🌟 <i>${relativeDate}</i>\n` +
            `${escapeHtml(randomMoment.content)}\n` +
            `<code>${fullDate}</code>`,
            {
                inline_keyboard: [
                    [{ text: "🎲 Ещё один", callback_data: "moments_random" }],
                    [{ text: "📖 Все моменты", callback_data: "menu_moments" }],
                    [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
                ]
            }
        );
        console.log("✅ Random moment shown");
    }

    await answerCallback(callback.id);
}

/**
 * Handle text message (potentially a new moment)
 */
async function handleTextMessage(message) {
    const chatId = message.chat.id;
    const user = getOrCreateUser(message.from);
    let text = message.text;

    // Check if user is in "adding moment" state
    const state = userStates.get(user.telegram_id);

    if (state && state.state === 'adding_moment') {
        // Double-submit prevention: Check if already saving a moment
        if (isUserActionProcessing(user.telegram_id, 'save_moment')) {
            console.log(`⚠️ Double-submit prevented: save_moment for user ${user.telegram_id}`);
            return true; // Return true to indicate message was handled (ignored duplicate)
        }
        markUserActionProcessing(user.telegram_id, 'save_moment');

        // Handle very long messages - truncate to reasonable limit
        let wasTruncated = false;
        if (text.length > MOMENT_CONTENT_LIMIT) {
            console.log(`⚠️ Message too long (${text.length} chars), truncating to ${MOMENT_CONTENT_LIMIT}`);
            text = truncateText(text, MOMENT_CONTENT_LIMIT, '...');
            wasTruncated = true;
        }

        // Save the moment (with potentially truncated text)
        const newMoment = addMoment(user.telegram_id, text);
        userStates.delete(user.telegram_id);

        const savedDate = formatDate(newMoment.created_at, user.language_code, true);

        // Build response message
        let responseText = "✨ <b>Момент сохранён!</b>\n\n" +
            `🌟 ${escapeHtml(text)}\n\n` +
            `📅 ${savedDate}\n\n`;

        if (wasTruncated) {
            responseText += "⚠️ <i>Сообщение было сокращено до допустимой длины.</i>\n\n";
        }

        responseText += "Спасибо, что делишься хорошим! 💝";

        await sendMessage(chatId, responseText,
            getMomentsKeyboard(user.telegram_id, getUserMoments(user.telegram_id).length)
        );
        console.log(`✅ Moment saved for user ${user.telegram_id}: "${text.substring(0, 30)}..."${wasTruncated ? ' (truncated)' : ''}`);
        return true;
    }

    return false; // Message was not handled as a moment
}

/**
 * Process a single update with error handling
 */
async function processUpdate(update) {
    try {
        if (update.message && update.message.text) {
            const text = update.message.text;
            const chatId = update.message.chat.id;
            const user = getOrCreateUser(update.message.from);

            try {
                if (text === '/start' || text.startsWith('/start ')) {
                    // Handle deep links: /start or /start PARAMETER
                    const deepLinkParam = text.startsWith('/start ') ? text.substring(7).trim() : null;
                    await handleStartCommand(update.message, deepLinkParam);
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
                } else if (text === '/delete_data') {
                    await handleDeleteDataCommand(update.message);
                } else if (text === '/export_data') {
                    await handleExportDataCommand(update.message);
                } else {
                    // Try to handle as a moment or general message
                    const handled = await handleTextMessage(update.message);
                    if (!handled) {
                        console.log(`Received message: ${text}`);
                    }
                }
            } catch (handlerError) {
                console.error(`Handler error for "${text}":`, handlerError.message);
                await sendErrorMessage(chatId, 'generic', user.language_code);
            }
        } else if (update.callback_query) {
        const callbackData = update.callback_query.data;
        const callbackId = update.callback_query.id;
        console.log(`Received callback: ${callbackData}`);

        // Double-submit prevention for callbacks
        if (isCallbackProcessing(callbackId)) {
            console.log(`⚠️ Double-submit prevented: callback ${callbackId} already processing`);
            await answerCallback(callbackId, "⏳ Подожди...");
            return;
        }
        markCallbackProcessing(callbackId);

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
        } else if (callbackData.startsWith("moments_")) {
            await handleMomentsCallback(update.callback_query, callbackData);
        } else if (callbackData.startsWith("stats_")) {
            await handleStatsFilterCallback(update.callback_query, callbackData);
        } else if (callbackData === "help") {
            // Handle help button from error messages
            const chatId = update.callback_query.message.chat.id;
            await handleHelpCommand({ chat: { id: chatId }, from: update.callback_query.from });
            await answerCallback(update.callback_query.id);
        } else if (callbackData === "delete_confirm") {
            await handleDeleteConfirmCallback(update.callback_query);
        } else if (callbackData === "restart") {
            // Handle restart after delete
            const chatId = update.callback_query.message.chat.id;
            await handleStartCommand({ chat: { id: chatId }, from: update.callback_query.from });
            await answerCallback(update.callback_query.id);
        } else {
            await answerCallback(update.callback_query.id);
        }
    }
    } catch (error) {
        console.error("Error processing update:", error.message);
        // Try to send error message if we have chat info
        try {
            const chatId = update.message?.chat?.id || update.callback_query?.message?.chat?.id;
            const user = update.message?.from || update.callback_query?.from;
            if (chatId && user) {
                const userObj = getOrCreateUser(user);
                await sendErrorMessage(chatId, 'generic', userObj.language_code);
            }
        } catch (errorSendError) {
            console.error("Failed to send error message:", errorSendError.message);
        }
    }
}

/**
 * Handle stats filter callbacks
 */
async function handleStatsFilterCallback(callback, action) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);
    const userMoments = getUserMoments(user.telegram_id);

    const now = new Date();
    let periodName = "";
    let periodMoments = [];

    if (action === "stats_week") {
        periodName = "за неделю";
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        periodMoments = userMoments.filter(m => m.created_at >= weekAgo);
    } else if (action === "stats_month") {
        periodName = "за месяц";
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        periodMoments = userMoments.filter(m => m.created_at >= monthAgo);
    }

    const startDate = action === "stats_week" ?
        formatDate(new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000), user.language_code) :
        formatDate(new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000), user.language_code);
    const endDate = formatDate(now, user.language_code);

    let statsText = `📊 <b>Статистика ${periodName}</b>\n`;
    statsText += `📅 ${startDate} — ${endDate}\n\n`;
    statsText += `🌟 Моментов: ${periodMoments.length}\n`;

    await editMessage(chatId, messageId, statsText, {
        inline_keyboard: [
            [{ text: "📊 Общая статистика", callback_data: "menu_stats" }],
            [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
        ]
    });

    await answerCallback(callback.id);
    console.log(`✅ Stats filtered: ${periodName} (${periodMoments.length} moments)`);
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

    // Start auto-save for persistence
    startAutoSave();

    // Save data on graceful shutdown
    process.on('SIGINT', () => {
        console.log('\n⏹️ Shutting down...');
        saveDataToFile();
        process.exit(0);
    });
    process.on('SIGTERM', () => {
        console.log('\n⏹️ Terminating...');
        saveDataToFile();
        process.exit(0);
    });

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
