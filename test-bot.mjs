/**
 * MINDSETHAPPYBOT - Node.js Testing Implementation
 * Full implementation for testing bot features
 */

const BOT_TOKEN = '7805611571:AAF59MdS0N3By7mMq_O53Wo8LjYLwfXVrBY';
const BASE_URL = `https://api.telegram.org/bot${BOT_TOKEN}`;
// OpenAI API configuration
const OPENAI_API_KEY = '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';
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';


// Welcome image URL (same as Python implementation)
const WELCOME_IMAGE_URL = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop";

// Telegram message limits
const TELEGRAM_MESSAGE_LIMIT = 4096;
const MOMENT_CONTENT_LIMIT = 2000;  // Reasonable limit for moment content

// Topic keywords mapping for categorizing moments
const topicKeywords = {
    'family': {
        emoji: '👨‍👩‍👧‍👦',
        name: { ru: 'Семья', en: 'Family', uk: 'Сімя' },
        keywords: ['семь', 'мама', 'папа', 'родител', 'брат', 'сестр', 'дочь', 'сын', 'ребен', 'дет', 'муж', 'жен', 'бабушк', 'дедушк', 'внук',
                   'family', 'mother', 'father', 'parent', 'brother', 'sister', 'daughter', 'son', 'child', 'husband', 'wife']
    },
    'friends': {
        emoji: '👫',
        name: { ru: 'Друзья', en: 'Friends', uk: 'Друзі' },
        keywords: ['друг', 'подруг', 'друзь', 'компани', 'встреч', 'вечеринк', 'посиделк', 'общен', 'friend', 'buddy', 'pal', 'meeting', 'party', 'hangout']
    },
    'work': {
        emoji: '💼',
        name: { ru: 'Работа', en: 'Work', uk: 'Робота' },
        keywords: ['работ', 'проект', 'коллег', 'босс', 'начальник', 'карьер', 'офис', 'зарплат', 'повыш', 'успех', 'задач', 'достижен',
                   'work', 'project', 'colleague', 'boss', 'career', 'office', 'salary', 'promotion', 'success', 'achievement']
    },
    'health': {
        emoji: '🏃',
        name: { ru: 'Здоровье', en: 'Health', uk: 'Здоровя' },
        keywords: ['здоров', 'спорт', 'тренировк', 'бег', 'йог', 'фитнес', 'зарядк', 'прогулк', 'сон', 'отдых', 'врач',
                   'health', 'sport', 'training', 'run', 'yoga', 'fitness', 'exercise', 'walk', 'sleep', 'rest']
    },
    'food': {
        emoji: '🍕',
        name: { ru: 'Еда', en: 'Food', uk: 'Їжа' },
        keywords: ['еда', 'обед', 'ужин', 'завтрак', 'ресторан', 'кафе', 'готов', 'вкусн', 'торт', 'пирог', 'рецепт',
                   'food', 'eat', 'lunch', 'dinner', 'breakfast', 'restaurant', 'cafe', 'cook', 'delicious', 'cake']
    },
    'nature': {
        emoji: '🌿',
        name: { ru: 'Природа', en: 'Nature', uk: 'Природа' },
        keywords: ['природ', 'парк', 'лес', 'гор', 'мор', 'озер', 'река', 'цвет', 'сад', 'погод', 'солнц', 'закат',
                   'nature', 'park', 'forest', 'mountain', 'sea', 'lake', 'river', 'flower', 'garden', 'weather', 'sun', 'sunset']
    },
    'travel': {
        emoji: '✈️',
        name: { ru: 'Путешествия', en: 'Travel', uk: 'Подорожі' },
        keywords: ['путешеств', 'поездк', 'отпуск', 'турист', 'город', 'стран', 'самолет', 'поезд', 'отель',
                   'travel', 'trip', 'vacation', 'tourist', 'city', 'country', 'airplane', 'train', 'hotel']
    },
    'hobby': {
        emoji: '🎨',
        name: { ru: 'Хобби', en: 'Hobby', uk: 'Хобі' },
        keywords: ['хобби', 'увлечен', 'творч', 'рисов', 'музык', 'книг', 'чита', 'фильм', 'кино', 'игр', 'танц', 'фото',
                   'hobby', 'passion', 'creative', 'draw', 'music', 'book', 'read', 'movie', 'cinema', 'game', 'dance', 'photo']
    },
    'pets': {
        emoji: '🐾',
        name: { ru: 'Питомцы', en: 'Pets', uk: 'Улюбленці' },
        keywords: ['питом', 'собак', 'кот', 'кош', 'пес', 'щенок', 'котенок', 'животн', 'хомяк', 'попугай',
                   'pet', 'dog', 'cat', 'puppy', 'kitten', 'animal', 'hamster', 'parrot']
    },
    'shopping': {
        emoji: '🛍️',
        name: { ru: 'Покупки', en: 'Shopping', uk: 'Покупки' },
        keywords: ['покупк', 'магазин', 'шоппинг', 'купил', 'подарок', 'одежд', 'обув', 'скидк',
                   'shopping', 'store', 'shop', 'buy', 'bought', 'gift', 'clothes', 'shoes', 'sale']
    },
    'learning': {
        emoji: '📚',
        name: { ru: 'Учёба', en: 'Learning', uk: 'Навчання' },
        keywords: ['учеб', 'учил', 'выучил', 'урок', 'школ', 'универс', 'курс', 'экзамен', 'знан', 'навык',
                   'learn', 'study', 'lesson', 'school', 'university', 'course', 'exam', 'knowledge', 'skill']
    },
    'celebration': {
        emoji: '🎉',
        name: { ru: 'Праздники', en: 'Celebrations', uk: 'Свята' },
        keywords: ['праздник', 'день рождения', 'юбилей', 'свадьб', 'годовщин', 'рождеств', 'новый год', 'пасх',
                   'holiday', 'birthday', 'anniversary', 'wedding', 'christmas', 'new year', 'easter', 'celebration']
    },
    'other': {
        emoji: '✨',
        name: { ru: 'Разное', en: 'Other', uk: 'Інше' },
        keywords: []
    }
};

// Question templates for variety - each language has multiple formulations
// Categories: main (daily questions), follow_up (after moment saved), return_inactive (for inactive users)
// No consecutive repetition allowed within each category
const questionTemplates = {
    ru: {
        main: {
            informal: [
                "Что хорошего произошло?",
                "Расскажи о чём-то приятном сегодня ✨",
                "Чему ты сегодня порадовался(ась)?",
                "Какой момент сегодня был особенным?",
                "Что тебя сегодня улыбнуло? 😊",
                "Поделись чем-то хорошим из сегодняшнего дня",
                "Что принесло тебе радость сегодня?",
                "Был ли сегодня момент, который хочется запомнить?",
                "О чём хорошем можешь рассказать?",
                "Что сегодня было здорово?"
            ],
            formal: [
                "Что хорошего произошло?",
                "Расскажите о чём-то приятном сегодня ✨",
                "Чему Вы сегодня порадовались?",
                "Какой момент сегодня был особенным?",
                "Что Вас сегодня улыбнуло? 😊",
                "Поделитесь чем-то хорошим из сегодняшнего дня",
                "Что принесло Вам радость сегодня?",
                "Был ли сегодня момент, который хочется запомнить?",
                "О чём хорошем можете рассказать?",
                "Что сегодня было здорово?"
            ]
        },
        follow_up: {
            informal: [
                "Отлично! Есть ещё что-то хорошее? 🌟",
                "Здорово! Хочешь добавить ещё один момент?",
                "Прекрасно! Может, вспомнишь что-то ещё?",
                "Замечательно! А что ещё порадовало?",
                "Супер! Есть что-то ещё на сегодня? ✨"
            ],
            formal: [
                "Отлично! Есть ещё что-то хорошее? 🌟",
                "Здорово! Хотите добавить ещё один момент?",
                "Прекрасно! Может, вспомните что-то ещё?",
                "Замечательно! А что ещё порадовало?",
                "Супер! Есть что-то ещё на сегодня? ✨"
            ]
        },
        return_inactive: {
            informal: [
                "Привет! Давно не виделись 👋 Как у тебя дела?",
                "С возвращением! 🌟 Расскажи, что хорошего произошло за это время?",
                "Рады тебя видеть снова! Что нового и приятного?",
                "Привет! ✨ Соскучились! Поделись чем-то хорошим?",
                "Ух ты, давно тебя не было! Как жизнь? Что радует?"
            ],
            formal: [
                "Здравствуйте! Давно не виделись 👋 Как Ваши дела?",
                "С возвращением! 🌟 Расскажите, что хорошего произошло за это время?",
                "Рады Вас видеть снова! Что нового и приятного?",
                "Здравствуйте! ✨ Мы скучали! Поделитесь чем-то хорошим?",
                "Давно Вас не было! Как жизнь? Что радует?"
            ]
        }
    },
    en: {
        main: {
            informal: [
                "What good happened today?",
                "Tell me about something nice today ✨",
                "What made you happy today?",
                "What moment was special today?",
                "What made you smile today? 😊",
                "Share something good from today",
                "What brought you joy today?",
                "Was there a moment worth remembering today?",
                "What's something good you can share?",
                "What was great today?"
            ],
            formal: [
                "What good happened today?",
                "Please tell me about something nice today ✨",
                "What made you happy today?",
                "What moment was special today?",
                "What made you smile today? 😊",
                "Please share something good from today",
                "What brought you joy today?",
                "Was there a moment worth remembering today?",
                "What's something good you can share?",
                "What was great today?"
            ]
        },
        follow_up: {
            informal: [
                "Great! Anything else good to share? 🌟",
                "Awesome! Want to add another moment?",
                "Wonderful! Remember anything else?",
                "Amazing! What else made you happy?",
                "Super! Anything more for today? ✨"
            ],
            formal: [
                "Great! Anything else good to share? 🌟",
                "Wonderful! Would you like to add another moment?",
                "Excellent! Do you remember anything else?",
                "Amazing! What else made you happy?",
                "Splendid! Anything more for today? ✨"
            ]
        },
        return_inactive: {
            informal: [
                "Hey! Long time no see 👋 How are you doing?",
                "Welcome back! 🌟 What good happened while you were away?",
                "Great to see you again! What's new and nice?",
                "Hi there! ✨ We missed you! Share something good?",
                "Wow, it's been a while! How's life? What's making you happy?"
            ],
            formal: [
                "Hello! It's been a while 👋 How are you doing?",
                "Welcome back! 🌟 What good happened while you were away?",
                "Great to see you again! What's new and nice?",
                "Hello! ✨ We missed you! Please share something good?",
                "It's been a while! How is life? What's making you happy?"
            ]
        }
    },
    uk: {
        main: {
            informal: [
                "Що хорошого сталось?",
                "Розкажи про щось приємне сьогодні ✨",
                "Чому ти сьогодні порадувався(лась)?",
                "Який момент сьогодні був особливим?",
                "Що тебе сьогодні засміяло? 😊",
                "Поділись чимось хорошим з сьогоднішнього дня",
                "Що принесло тобі радість сьогодні?",
                "Чи був сьогодні момент, який хочеться запам'ятати?",
                "Про що хороше можеш розповісти?",
                "Що сьогодні було класно?"
            ],
            formal: [
                "Що хорошого сталось?",
                "Розкажіть про щось приємне сьогодні ✨",
                "Чому Ви сьогодні порадувались?",
                "Який момент сьогодні був особливим?",
                "Що Вас сьогодні засміяло? 😊",
                "Поділіться чимось хорошим з сьогоднішнього дня",
                "Що принесло Вам радість сьогодні?",
                "Чи був сьогодні момент, який хочеться запам'ятати?",
                "Про що хороше можете розповісти?",
                "Що сьогодні було класно?"
            ]
        },
        follow_up: {
            informal: [
                "Чудово! Є ще щось хороше? 🌟",
                "Клас! Хочеш додати ще один момент?",
                "Прекрасно! Може, згадаєш щось ще?",
                "Чудово! А що ще порадувало?",
                "Супер! Є щось ще на сьогодні? ✨"
            ],
            formal: [
                "Чудово! Є ще щось хороше? 🌟",
                "Класно! Хочете додати ще один момент?",
                "Прекрасно! Може, згадаєте щось ще?",
                "Чудово! А що ще порадувало?",
                "Супер! Є щось ще на сьогодні? ✨"
            ]
        },
        return_inactive: {
            informal: [
                "Привіт! Давно не бачились 👋 Як у тебе справи?",
                "З поверненням! 🌟 Розкажи, що хорошого сталось за цей час?",
                "Раді тебе бачити знову! Що нового і приємного?",
                "Привіт! ✨ Скучили! Поділись чимось хорошим?",
                "Ого, давно тебе не було! Як життя? Що радує?"
            ],
            formal: [
                "Вітаю! Давно не бачились 👋 Як Ваші справи?",
                "З поверненням! 🌟 Розкажіть, що хорошого сталось за цей час?",
                "Раді Вас бачити знову! Що нового і приємного?",
                "Вітаю! ✨ Ми скучили! Поділіться чимось хорошим?",
                "Давно Вас не було! Як життя? Що радує?"
            ]
        }
    }
};

// Track last question shown to each user by category (to prevent repetition)
const lastUserQuestions = new Map();

/**
 * Get a random question for user that doesn't repeat consecutively
 * @param {object} user - User object with language_code and formal_address
 * @param {string} category - Question category: 'main', 'follow_up', or 'return_inactive'
 * @returns {string} A question formulation
 */
function getRandomQuestion(user, category = 'main') {
    const langCode = user.language_code?.startsWith('en') ? 'en' :
                     user.language_code?.startsWith('uk') ? 'uk' : 'ru';
    const addressType = user.formal_address ? 'formal' : 'informal';

    // Get templates for the specified category
    const templates = questionTemplates[langCode]?.[category]?.[addressType] ||
                      questionTemplates.ru.main.informal;

    // Create unique key for tracking per user per category
    const trackingKey = `${user.telegram_id}_${category}`;
    const lastQuestionIndex = lastUserQuestions.get(trackingKey);

    // Get a random index that's different from the last one
    let newIndex;
    if (templates.length === 1) {
        newIndex = 0;
    } else {
        do {
            newIndex = Math.floor(Math.random() * templates.length);
        } while (newIndex === lastQuestionIndex);
    }

    // Remember this question index for this category
    lastUserQuestions.set(trackingKey, newIndex);

    return templates[newIndex];
}

/**
 * Check if user has been inactive for a specified number of days
 * @param {object} user - User object
 * @param {number} days - Number of days to consider inactive
 * @returns {boolean} True if user is inactive
 */
function isUserInactive(user, days = 3) {
    if (!user.last_activity) return false;
    const lastActivity = new Date(user.last_activity);
    const daysSinceActivity = (Date.now() - lastActivity.getTime()) / (1000 * 60 * 60 * 24);
    return daysSinceActivity >= days;
}

/**
 * Get appropriate question for user based on their activity status
 * @param {object} user - User object
 * @returns {string} A question formulation
 */
function getQuestionForUser(user) {
    // Use return_inactive questions for users who haven't interacted for 3+ days
    if (isUserInactive(user, 3)) {
        return getRandomQuestion(user, 'return_inactive');
    }
    // Default to main questions
    return getRandomQuestion(user, 'main');
}

/**
 * Parse timezone offset from string
 * @param {string} timezone - Timezone string (e.g., "UTC", "+03:00", "-05:00", "Europe/Moscow")
 * @returns {number} Offset in minutes from UTC
 */
function parseTimezoneOffset(timezone) {
    if (!timezone || timezone === 'UTC' || timezone === 'Z') {
        return 0;
    }

    // Handle offset format: "+03:00", "-05:00", "+3", "-5"
    const offsetMatch = timezone.match(/^([+-])(\d{1,2}):?(\d{2})?$/);
    if (offsetMatch) {
        const sign = offsetMatch[1] === '+' ? 1 : -1;
        const hours = parseInt(offsetMatch[2]);
        const minutes = parseInt(offsetMatch[3] || '0');
        return sign * (hours * 60 + minutes);
    }

    // Handle named timezones (simplified mapping for common ones)
    const timezoneOffsets = {
        'Europe/Moscow': 180,      // UTC+3
        'Europe/Berlin': 60,       // UTC+1
        'Europe/London': 0,        // UTC
        'America/New_York': -300,  // UTC-5
        'America/Los_Angeles': -480, // UTC-8
        'Asia/Tokyo': 540,         // UTC+9
        'Asia/Dubai': 240,         // UTC+4
        'Australia/Sydney': 600    // UTC+10
    };

    return timezoneOffsets[timezone] || 0;
}

/**
 * Get current time in user's timezone
 * @param {object} user - User object with timezone field
 * @param {Date} [utcTime] - Optional UTC time (defaults to current time)
 * @returns {Date} Time adjusted to user's timezone
 */
function getUserLocalTime(user, utcTime = new Date()) {
    const offsetMinutes = parseTimezoneOffset(user.timezone || 'UTC');
    const userTime = new Date(utcTime.getTime() + offsetMinutes * 60 * 1000);
    return userTime;
}

/**
 * Check if current time is within user's active hours (timezone-aware)
 * @param {object} user - User object with active_hours_start, active_hours_end, and timezone
 * @param {Date} [checkTime] - Optional time to check (defaults to current time)
 * @returns {boolean} True if within active hours
 */
function isWithinActiveHours(user, checkTime = new Date()) {
    const startParts = user.active_hours_start.split(':').map(Number);
    const endParts = user.active_hours_end.split(':').map(Number);

    const startMinutes = startParts[0] * 60 + (startParts[1] || 0);
    const endMinutes = endParts[0] * 60 + (endParts[1] || 0);

    // Get user's local time
    const userLocalTime = getUserLocalTime(user, checkTime);
    const currentMinutes = userLocalTime.getUTCHours() * 60 + userLocalTime.getUTCMinutes();

    // Handle normal case (e.g., 09:00 - 21:00)
    if (startMinutes <= endMinutes) {
        return currentMinutes >= startMinutes && currentMinutes < endMinutes;
    }

    // Handle overnight case (e.g., 21:00 - 09:00) - though unusual for this app
    return currentMinutes >= startMinutes || currentMinutes < endMinutes;
}

/**
 * Format timezone for display in settings
 * @param {string} timezone - Timezone string (e.g., "UTC", "+03:00", "Europe/Moscow")
 * @returns {string} Human-readable timezone display
 */
function formatTimezoneDisplay(timezone) {
    if (!timezone || timezone === 'UTC' || timezone === 'Z') {
        return 'UTC (по умолчанию)';
    }

    // Handle offset format (e.g., "+03:00", "-05:00")
    const offsetMatch = timezone.match(/^([+-])(\d{1,2}):?(\d{2})?$/);
    if (offsetMatch) {
        const sign = offsetMatch[1];
        const hours = offsetMatch[2].padStart(2, '0');
        const minutes = offsetMatch[3] || '00';
        return `UTC${sign}${hours}:${minutes}`;
    }

    // Handle named timezones with display names
    const timezoneNames = {
        'Europe/Moscow': 'Москва (UTC+3)',
        'Europe/Kiev': 'Киев (UTC+2)',
        'Europe/London': 'Лондон (UTC+0)',
        'America/New_York': 'Нью-Йорк (UTC-5)',
        'America/Los_Angeles': 'Лос-Анджелес (UTC-8)',
        'Asia/Tokyo': 'Токио (UTC+9)'
    };

    return timezoneNames[timezone] || timezone;
}

/**
 * Check if a scheduled notification should be sent based on active hours
 * @param {object} user - User object
 * @param {Date} [checkTime] - Optional time to check
 * @returns {object} { shouldSend: boolean, reason: string }
 */
function shouldSendNotification(user, checkTime = new Date()) {
    // Check if notifications are enabled
    if (!user.notifications_enabled) {
        return { shouldSend: false, reason: 'Notifications disabled' };
    }

    // Check active hours
    if (!isWithinActiveHours(user, checkTime)) {
        return {
            shouldSend: false,
            reason: `Outside active hours (${user.active_hours_start} - ${user.active_hours_end})`
        };
    }

    return { shouldSend: true, reason: 'Within active hours' };
}

/**
 * Extract topics from moment content
 */
function extractTopics(content) {
    if (!content) return ['other'];
    const lowerContent = content.toLowerCase();
    const foundTopics = [];
    for (const [topicId, topicData] of Object.entries(topicKeywords)) {
        if (topicId === 'other') continue;
        for (const keyword of topicData.keywords) {
            if (lowerContent.includes(keyword.toLowerCase())) {
                if (!foundTopics.includes(topicId)) {
                    foundTopics.push(topicId);
                }
                break;
            }
        }
    }
    if (foundTopics.length === 0) {
        foundTopics.push('other');
    }
    return foundTopics;
}

/**
 * Get topic name in user's language
 */
function getTopicName(topicId, languageCode = 'ru') {
    const topic = topicKeywords[topicId];
    if (!topic) return '✨ Разное';
    const lang = topic.name[languageCode] ? languageCode : 'ru';
    return topic.emoji + ' ' + topic.name[lang];
}

/**
 * Group moments by topics
 */
function groupMomentsByTopics(userMoments) {
    const groups = {};
    for (const moment of userMoments) {
        const topics = moment.topics || ['other'];
        for (const topicId of topics) {
            if (!groups[topicId]) {
                groups[topicId] = [];
            }
            groups[topicId].push(moment);
        }
    }
    return groups;
}

/**
 * Calculate cosine similarity between two vectors
 * @param {Array} vecA - First vector
 * @param {Array} vecB - Second vector
 * @returns {number} Cosine similarity (between -1 and 1)
 */
function cosineSimilarity(vecA, vecB) {
    if (!vecA || !vecB || vecA.length !== vecB.length) return 0;

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < vecA.length; i++) {
        dotProduct += vecA[i] * vecB[i];
        normA += vecA[i] * vecA[i];
        normB += vecB[i] * vecB[i];
    }

    if (normA === 0 || normB === 0) return 0;
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

/**
 * Find semantically relevant moments using vector similarity and topic matching
 * Uses embeddings for accurate semantic search, falls back to keyword matching
 * @param {string} query - User's message or search query
 * @param {Array} userMoments - User's saved moments
 * @param {Array|null} queryEmbedding - Pre-computed embedding for query (optional)
 * @returns {Array} Relevant moments sorted by relevance score
 */
function findRelevantMoments(query, userMoments, queryEmbedding = null) {
    if (!userMoments || userMoments.length === 0) return [];

    // Check if we have embeddings available
    const hasEmbeddings = queryEmbedding && userMoments.some(m => m.embedding);

    // Score each moment
    const scoredMoments = userMoments.map(moment => {
        let score = 0;

        // Vector similarity (primary scoring if embeddings available)
        if (hasEmbeddings && moment.embedding && queryEmbedding) {
            const similarity = cosineSimilarity(queryEmbedding, moment.embedding);
            // Convert similarity (-1 to 1) to score (0 to 10)
            score = (similarity + 1) * 5;
        }

        // Topic-based scoring (fallback or boost)
        const queryTopics = extractTopics(query);
        const momentTopics = moment.topics || extractTopics(moment.content);

        for (const topic of queryTopics) {
            if (momentTopics.includes(topic)) {
                score += hasEmbeddings ? 1 : 2; // Smaller boost when using embeddings
            }
        }

        // Keyword matching (fallback or boost)
        const queryLower = query.toLowerCase();
        const contentLower = moment.content.toLowerCase();
        const queryWords = queryLower.split(/\s+/).filter(w => w.length > 3);

        for (const word of queryWords) {
            if (contentLower.includes(word)) {
                score += hasEmbeddings ? 0.5 : 1; // Smaller boost when using embeddings
            }
        }

        return { moment, score };
    });

    // Filter moments with score > 0 and sort by score
    return scoredMoments
        .filter(sm => sm.score > 0)
        .sort((a, b) => b.score - a.score)
        .map(sm => sm.moment);
}

/**
 * Find semantically relevant moments using vector search (async version)
 * Generates embedding for query and uses cosine similarity
 * @param {string} query - User's message or search query
 * @param {Array} userMoments - User's saved moments
 * @returns {Promise<Array>} Relevant moments sorted by relevance score
 */
async function findRelevantMomentsAsync(query, userMoments) {
    if (!userMoments || userMoments.length === 0) return [];

    // Check if any moments have embeddings
    const hasEmbeddings = userMoments.some(m => m.embedding);

    if (hasEmbeddings) {
        // Generate embedding for the query
        const queryEmbedding = await generateEmbedding(query);
        if (queryEmbedding) {
            return findRelevantMoments(query, userMoments, queryEmbedding);
        }
    }

    // Fall back to keyword-based matching
    return findRelevantMoments(query, userMoments);
}

/**
 * Generate a personalized dialog response using OpenAI GPT-4
 * Uses user's moment history to provide relevant context
 * @param {string} userMessage - User's message
 * @param {object} user - User object
 * @param {Array} userMoments - User's saved moments
 * @returns {string} AI-generated response
 */
async function generateDialogResponse(userMessage, user, userMoments) {
    try {
        // Build context from user's moments
        let historyContext = "";
        if (userMoments.length > 0) {
            // Get last 10 moments for context (most recent first)
            const recentMoments = userMoments.slice(-10).reverse();
            historyContext = "Последние радостные моменты пользователя:\n";
            for (const moment of recentMoments) {
                const date = new Date(moment.created_at).toLocaleDateString('ru-RU');
                historyContext += `- ${date}: ${moment.content}\n`;
            }
            historyContext += "\n";
        }

        // Build the system prompt
        const systemPrompt = `Ты — дружелюбный помощник для развития позитивного мышления.
Твоя задача — поддержать пользователя, помочь ему увидеть хорошее в жизни.

Правила:
1. Будь тёплым и эмпатичным
2. Давай советы как "взгляд со стороны"
3. Напоминай о прошлых радостных моментах из истории пользователя
4. Помогай находить позитив в текущей ситуации
5. Явно указывай, что все решения принимает сам пользователь
6. Используй форму обращения: ${user.formal_address ? 'на «вы»' : 'на «ты»'}
7. Отвечай на языке пользователя (${user.language_code === 'en' ? 'English' : user.language_code === 'uk' ? 'Українською' : 'Русский'})
8. Будь кратким, но содержательным (2-3 абзаца максимум)

${historyContext}
Имя пользователя: ${user.first_name}`;

        const response = await fetch(OPENAI_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${OPENAI_API_KEY}`
            },
            body: JSON.stringify({
                model: 'gpt-4o-mini',
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: userMessage }
                ],
                max_tokens: 500,
                temperature: 0.7
            })
        });

        if (!response.ok) {
            console.error(`OpenAI API error: ${response.status}`);
            return null;
        }

        const data = await response.json();
        if (data.choices && data.choices[0] && data.choices[0].message) {
            console.log("✅ AI dialog response generated");
            return data.choices[0].message.content;
        }

        return null;
    } catch (error) {
        console.error("Error generating dialog response:", error.message);
        return null;
    }
}

/**
 * Negative mood detection keywords
 */
const negativeMoodKeywords = [
    // Russian negative phrases
    'ничего хорошего', 'ничего не произошло', 'ничего', 'плохо', 'грустно', 'тоскливо',
    'депрессия', 'уныние', 'тяжело', 'сложно', 'трудно', 'устал', 'устала', 'выгорание',
    'не знаю', 'не могу', 'не хочу', 'всё плохо', 'все плохо', 'нет настроения',
    'пустота', 'одиноко', 'одинок', 'скучно', 'безнадежно', 'бессмысленно',
    // English negative phrases
    'nothing good', 'nothing happened', 'nothing', 'bad', 'sad', 'depressed',
    'tired', 'exhausted', 'burnout', 'lonely', 'empty', 'hopeless', 'meaningless',
    "can't", "don't know", "don't want"
];

/**
 * Detect if user's message indicates negative mood
 * @param {string} message - User's message
 * @returns {boolean} True if negative mood detected
 */
function detectNegativeMood(message) {
    if (!message) return false;
    const lowerMessage = message.toLowerCase().trim();

    // Check for short negative responses
    if (lowerMessage.length < 20 && ['нет', 'ничего', 'no', 'nothing', 'не'].includes(lowerMessage)) {
        return true;
    }

    // Check for negative keywords
    return negativeMoodKeywords.some(keyword => lowerMessage.includes(keyword.toLowerCase()));
}

/**
 * Generate supportive response for negative mood with past moments
 * @param {string} userMessage - User's message
 * @param {object} user - User object
 * @param {Array} userMoments - User's saved moments
 * @returns {string} Supportive response
 */
function generateNegativeMoodResponse(userMessage, user, userMoments) {
    const name = user.formal_address ? "Вы" : "ты";
    const nameLC = name.toLowerCase();

    // If user has moments, remind them of past good moments
    if (userMoments.length > 0) {
        // Try to find relevant moments first, fall back to random
        const relevantMoments = findRelevantMoments(userMessage, userMoments);
        const selectedMoment = relevantMoments.length > 0
            ? relevantMoments[0]
            : userMoments[Math.floor(Math.random() * userMoments.length)];

        const randomMoment = selectedMoment;
        const momentContent = randomMoment.content.length > 100
            ? randomMoment.content.substring(0, 100) + "..."
            : randomMoment.content;

        const responses = [
            `Я понимаю, что сейчас ${user.formal_address ? 'Вам' : 'тебе'} непросто. 💝\n\nНо помн${user.formal_address ? 'ите' : 'ишь'}, совсем недавно ${nameLC} ${user.formal_address ? 'писали' : 'писал(а)'}: "${momentContent}"\n\nХорошие моменты есть в ${user.formal_address ? 'Вашей' : 'твоей'} жизни, даже если сейчас их не видно. 🌟`,
            `Бывают трудные дни, это нормально. 💙\n\nНо среди ${user.formal_address ? 'Ваших' : 'твоих'} радостных моментов есть такой:\n"${momentContent}"\n\nМожет, это напоминание поможет ${user.formal_address ? 'Вам' : 'тебе'} почувствовать себя лучше? ✨`,
            `Я слышу ${nameLC}. Иногда хорошее сложно заметить. 🫂\n\nНо ${nameLC} же ${user.formal_address ? 'запомнили' : 'помнишь'} этот момент:\n"${momentContent}"\n\nТакие моменты доказывают, что радость возможна. Она вернётся. 💝`
        ];

        return responses[Math.floor(Math.random() * responses.length)];
    }

    // No moments yet - encourage without references
    const responses = [
        `Я понимаю, что сейчас ${user.formal_address ? 'Вам' : 'тебе'} непросто. 💝\n\nИногда хорошее сложно заметить. Но даже маленькие вещи имеют значение — вкусный кофе, улыбка прохожего, тёплое одеяло.\n\nМожет, попробу${user.formal_address ? 'ете' : 'ешь'} найти что-то такое? 🌟`,
        `Бывают трудные дни, и это нормально. 💙\n\n${user.formal_address ? 'Ваши' : 'Твои'} чувства важны. Но даже в такие дни можно найти маленький лучик света.\n\nЧто первое приходит в голову, когда ${user.formal_address ? 'думаете' : 'думаешь'} о чём-то хорошем? ✨`
    ];

    return responses[Math.floor(Math.random() * responses.length)];
}

/**
 * Generate a fallback response when OpenAI is unavailable
 * Uses user's moments to provide personalized support
 */
function generateFallbackDialogResponse(userMessage, user, userMoments) {
    // Check for negative mood first
    if (detectNegativeMood(userMessage)) {
        console.log("🔍 Negative mood detected, generating supportive response");
        return generateNegativeMoodResponse(userMessage, user, userMoments);
    }

    const name = user.formal_address ? "Вы" : "ты";

    // Check if user has moments to reference
    if (userMoments.length > 0) {
        const randomMoment = userMoments[Math.floor(Math.random() * userMoments.length)];
        const momentContent = randomMoment.content.length > 100
            ? randomMoment.content.substring(0, 100) + "..."
            : randomMoment.content;

        const responses = [
            `Я слышу ${name.toLowerCase()}. 💝 Помн${user.formal_address ? 'ите' : 'ишь'}, как ${name.toLowerCase()} ${user.formal_address ? 'писали' : 'писал(а)'}: "${momentContent}"? Такие моменты показывают, что в жизни много хорошего.`,
            `Спасибо, что ${user.formal_address ? 'поделились' : 'поделился(ась)'}. Кстати, среди ${user.formal_address ? 'Ваших' : 'твоих'} радостных моментов есть такой: "${momentContent}". Может, это поможет взглянуть на ситуацию иначе? 🌟`,
            `Я ${user.formal_address ? 'Вас' : 'тебя'} понимаю. У ${name.toLowerCase()} есть много хороших моментов — например, "${momentContent}". Давай${user.formal_address ? 'те' : ''} вместе найдём что-то хорошее и сейчас! ✨`
        ];

        return responses[Math.floor(Math.random() * responses.length)];
    }

    // Generic supportive response if no moments
    const responses = [
        `Я слышу ${name.toLowerCase()}. 💝 Хоть у нас пока нет сохранённых радостных моментов, я уверен, что они есть в ${user.formal_address ? 'Вашей' : 'твоей'} жизни. Расскажи${user.formal_address ? 'те' : ''} мне о чём-то хорошем, что произошло недавно?`,
        `Спасибо, что ${user.formal_address ? 'поделились' : 'поделился(ась)'}. Давай${user.formal_address ? 'те' : ''} попробуем найти что-то позитивное вместе. Что хорошего ${user.formal_address ? 'Вы видели' : 'ты видел(а)'} сегодня, пусть даже мелочь? 🌟`
    ];

    return responses[Math.floor(Math.random() * responses.length)];
}



// File-based persistence
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const DATA_FILE = join(__dirname, 'bot-data.json');

// Current schema version - increment when making schema changes
const SCHEMA_VERSION = 2;

// Migration definitions: version -> migration function
const migrations = {
    // Version 1 -> 2: Add timezone and scheduledJobs
    1: (data) => {
        console.log('📦 Running migration v1 -> v2: Adding timezone and scheduledJobs');

        // Add timezone field to all users
        if (data.users) {
            for (const userId of Object.keys(data.users)) {
                if (!data.users[userId].timezone) {
                    data.users[userId].timezone = 'UTC';
                }
            }
        }

        // Initialize scheduledJobs if not present
        if (!data.scheduledJobs) {
            data.scheduledJobs = {};
        }

        return data;
    },
    // Version 2 -> 3: Reserved for future migrations
    // 2: (data) => { ... }
};

/**
 * Run all necessary migrations to bring data to current schema version
 * @param {object} data - The loaded data object
 * @returns {object} The migrated data object
 */
function runMigrations(data) {
    const currentVersion = data.schemaVersion || 1;

    if (currentVersion >= SCHEMA_VERSION) {
        console.log(`📦 Schema is up to date (v${currentVersion})`);
        return data;
    }

    console.log(`📦 Schema migration needed: v${currentVersion} -> v${SCHEMA_VERSION}`);

    let migratedData = { ...data };

    for (let version = currentVersion; version < SCHEMA_VERSION; version++) {
        if (migrations[version]) {
            migratedData = migrations[version](migratedData);
            migratedData.schemaVersion = version + 1;
            console.log(`✅ Migration v${version} -> v${version + 1} completed`);
        }
    }

    return migratedData;
}

/**
 * Create a new empty database with the current schema
 * @returns {object} A new data object with the current schema
 */
function createEmptyDatabase() {
    return {
        schemaVersion: SCHEMA_VERSION,
        users: {},
        moments: {},
        scheduledJobs: {},
        createdAt: new Date().toISOString()
    };
}

/**
 * Verify database structure has all required tables (collections)
 * @param {object} data - The data object to verify
 * @returns {object} Verification results
 */
function verifyDatabaseStructure(data) {
    const requiredTables = ['users', 'moments', 'scheduledJobs'];
    const results = {
        valid: true,
        tables: {},
        schemaVersion: data.schemaVersion || 1
    };

    for (const table of requiredTables) {
        const exists = data[table] !== undefined;
        results.tables[table] = exists;
        if (!exists) {
            results.valid = false;
        }
    }

    return results;
}

// Simple in-memory user storage for testing
const users = new Map();

// In-memory moments storage for testing
const moments = new Map();

// Scheduled notification jobs (persisted)
const scheduledJobs = new Map();

// User states for conversation flow (not persisted - session only)
const userStates = new Map();

/**
 * Load data from file on startup
 */
function loadDataFromFile() {
    try {
        if (existsSync(DATA_FILE)) {
            let data = JSON.parse(readFileSync(DATA_FILE, 'utf8'));

            // Run migrations if needed
            const wasVersion = data.schemaVersion || 1;
            data = runMigrations(data);

            // Verify database structure
            const verification = verifyDatabaseStructure(data);
            if (!verification.valid) {
                console.warn(`⚠️ Database structure incomplete:`, verification.tables);
            }

            // If migrations were run, save the updated data
            if ((data.schemaVersion || 1) > wasVersion) {
                writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
                console.log(`💾 Migrated data saved to file`);
            }

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

            // Load scheduled jobs
            if (data.scheduledJobs) {
                for (const [key, value] of Object.entries(data.scheduledJobs)) {
                    // Convert date strings back to Date objects
                    scheduledJobs.set(parseInt(key), {
                        ...value,
                        scheduledAt: new Date(value.scheduledAt),
                        nextRunAt: new Date(value.nextRunAt)
                    });
                }
            }

            console.log(`📁 Loaded data: ${users.size} users, ${[...moments.values()].flat().length} moments, ${scheduledJobs.size} scheduled jobs (schema v${data.schemaVersion || 1})`);
        } else {
            // Create new database with current schema
            const newDb = createEmptyDatabase();
            writeFileSync(DATA_FILE, JSON.stringify(newDb, null, 2), 'utf8');
            console.log(`📁 Created new data file with schema v${SCHEMA_VERSION}`);
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
            schemaVersion: SCHEMA_VERSION,
            users: Object.fromEntries(users),
            moments: Object.fromEntries(moments),
            scheduledJobs: Object.fromEntries(scheduledJobs),
            savedAt: new Date().toISOString()
        };
        writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
        console.log(`💾 Data saved: ${users.size} users, ${[...moments.values()].flat().length} moments, ${scheduledJobs.size} jobs`);
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

/**
 * Schedule a notification job for a user
 * @param {number} userId - The user's Telegram ID
 * @param {Date} nextRunAt - When to send the notification
 * @param {string} jobType - Type of job ('question' for periodic questions)
 */
function scheduleNotificationJob(userId, nextRunAt, jobType = 'question') {
    const job = {
        userId: userId,
        jobType: jobType,
        scheduledAt: new Date(),
        nextRunAt: nextRunAt,
        status: 'scheduled'
    };
    scheduledJobs.set(userId, job);
    saveDataToFile();
    console.log(`📅 Scheduled ${jobType} job for user ${userId} at ${nextRunAt.toISOString()}`);
    return job;
}

/**
 * Get the next scheduled job for a user
 * @param {number} userId - The user's Telegram ID
 * @returns {object|null} The scheduled job or null
 */
function getScheduledJob(userId) {
    return scheduledJobs.get(userId) || null;
}

/**
 * Remove a scheduled job for a user
 * @param {number} userId - The user's Telegram ID
 */
function removeScheduledJob(userId) {
    if (scheduledJobs.has(userId)) {
        scheduledJobs.delete(userId);
        saveDataToFile();
        console.log(`🗑️ Removed scheduled job for user ${userId}`);
    }
}

/**
 * Calculate next notification time based on user settings
 * @param {object} user - User object with notification settings
 * @returns {Date} The next notification time
 */
function calculateNextNotificationTime(user) {
    const now = new Date();
    const intervalMs = (user.notification_interval_hours || 3) * 60 * 60 * 1000;
    let nextTime = new Date(now.getTime() + intervalMs);

    // Ensure notification is within active hours
    const userLocalNext = getUserLocalTime(user, nextTime);
    const startParts = user.active_hours_start.split(':').map(Number);
    const endParts = user.active_hours_end.split(':').map(Number);
    const startMinutes = startParts[0] * 60 + (startParts[1] || 0);
    const endMinutes = endParts[0] * 60 + (endParts[1] || 0);
    const nextMinutes = userLocalNext.getUTCHours() * 60 + userLocalNext.getUTCMinutes();

    // If outside active hours, schedule for start of next active period
    if (nextMinutes < startMinutes || nextMinutes >= endMinutes) {
        // Schedule for tomorrow's start time
        const offsetMinutes = parseTimezoneOffset(user.timezone || 'UTC');
        const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        tomorrow.setUTCHours(startParts[0], startParts[1] || 0, 0, 0);
        // Adjust from user's local time back to UTC
        nextTime = new Date(tomorrow.getTime() - offsetMinutes * 60 * 1000);
    }

    return nextTime;
}

/**
 * Send a scheduled question to a user
 * @param {object} user - User object
 */
async function sendScheduledQuestion(user) {
    if (!user.notifications_enabled || !user.onboarding_completed) {
        return;
    }

    if (!isWithinActiveHours(user)) {
        console.log(`⏰ User ${user.telegram_id} is outside active hours, skipping notification`);
        return;
    }

    // Increment questions sent counter
    if (!user.statistics) user.statistics = {};
    user.statistics.questions_sent = (user.statistics.questions_sent || 0) + 1;

    // Set user state to awaiting moment
    userStates.set(user.telegram_id, { state: 'adding_moment', question_asked_at: new Date() });

    // Get appropriate question based on user's activity status
    // Uses return_inactive category if user hasn't interacted for 3+ days
    const question = getQuestionForUser(user);

    try {
        await sendMessage(user.telegram_id, question);
        console.log(`📤 Sent scheduled question to user ${user.telegram_id}`);

        // Schedule next notification
        const nextTime = calculateNextNotificationTime(user);
        scheduleNotificationJob(user.telegram_id, nextTime, 'question');
    } catch (error) {
        console.error(`❌ Failed to send scheduled question to user ${user.telegram_id}:`, error.message);
    }
}

/**
 * Check and execute due scheduled jobs
 */
async function checkScheduledJobs() {
    const now = new Date();

    for (const [userId, job] of scheduledJobs.entries()) {
        if (job.status === 'scheduled' && job.nextRunAt <= now) {
            const user = users.get(userId);
            if (user) {
                console.log(`⏰ Executing scheduled job for user ${userId}`);
                job.status = 'executing';
                await sendScheduledQuestion(user);
            } else {
                // User no longer exists, remove job
                removeScheduledJob(userId);
            }
        }
    }
}

/**
 * Start the job scheduler (checks every minute)
 */
function startJobScheduler() {
    // Check immediately on startup
    checkScheduledJobs();

    // Then check every minute
    setInterval(checkScheduledJobs, 60000);
    console.log(`⏰ Job scheduler started (checking every minute)`);
}

/**
 * Restore scheduled jobs on bot restart
 */
function restoreScheduledJobs() {
    const now = new Date();
    let restored = 0;
    let rescheduled = 0;

    for (const [userId, job] of scheduledJobs.entries()) {
        const user = users.get(userId);
        if (!user) {
            // User no longer exists, remove job
            scheduledJobs.delete(userId);
            continue;
        }

        // If job was missed (nextRunAt is in the past), reschedule
        if (job.nextRunAt <= now) {
            const nextTime = calculateNextNotificationTime(user);
            job.nextRunAt = nextTime;
            job.status = 'scheduled';
            rescheduled++;
        } else {
            restored++;
        }
    }

    if (restored > 0 || rescheduled > 0) {
        saveDataToFile();
        console.log(`📅 Jobs restored: ${restored} pending, ${rescheduled} rescheduled`);
    }
}

// Load data on startup
loadDataFromFile();

// Restore scheduled jobs after loading data
restoreScheduledJobs();

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
 * Calculate user's streak (consecutive days with at least one moment)
 * @param {Array} userMoments - Array of user's moments
 * @returns {Object} { currentStreak, bestStreak }
 */
function calculateStreak(userMoments) {
    if (!userMoments || userMoments.length === 0) {
        return { currentStreak: 0, bestStreak: 0 };
    }

    // Get unique days (as date strings) when moments were recorded
    const momentDays = new Set();
    for (const moment of userMoments) {
        const date = new Date(moment.created_at);
        const dayStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        momentDays.add(dayStr);
    }

    // Sort days
    const sortedDays = Array.from(momentDays).sort();

    if (sortedDays.length === 0) {
        return { currentStreak: 0, bestStreak: 0 };
    }

    // Calculate streaks
    let currentStreak = 0;
    let bestStreak = 0;
    let tempStreak = 1;

    // Get today's date string
    const today = new Date();
    const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

    // Get yesterday's date string
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = `${yesterday.getFullYear()}-${String(yesterday.getMonth() + 1).padStart(2, '0')}-${String(yesterday.getDate()).padStart(2, '0')}`;

    // Calculate best streak by going through all days
    for (let i = 1; i < sortedDays.length; i++) {
        const prevDate = new Date(sortedDays[i - 1]);
        const currDate = new Date(sortedDays[i]);

        // Check if consecutive days
        const diffMs = currDate - prevDate;
        const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 1) {
            tempStreak++;
        } else {
            if (tempStreak > bestStreak) {
                bestStreak = tempStreak;
            }
            tempStreak = 1;
        }
    }

    if (tempStreak > bestStreak) {
        bestStreak = tempStreak;
    }

    // Calculate current streak (must include today or yesterday)
    const lastDay = sortedDays[sortedDays.length - 1];

    if (lastDay === todayStr || lastDay === yesterdayStr) {
        // Count backwards from the last day
        currentStreak = 1;
        for (let i = sortedDays.length - 2; i >= 0; i--) {
            const currDate = new Date(sortedDays[i + 1]);
            const prevDate = new Date(sortedDays[i]);

            const diffMs = currDate - prevDate;
            const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

            if (diffDays === 1) {
                currentStreak++;
            } else {
                break;
            }
        }
    }

    return { currentStreak, bestStreak };
}

/**
 * Generate embedding for text using OpenAI API
 * @param {string} text - Text to generate embedding for
 * @returns {Array|null} Embedding array (1536 dimensions) or null on error
 */
async function generateEmbedding(text) {
    try {
        const response = await fetch('https://api.openai.com/v1/embeddings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${OPENAI_API_KEY}`
            },
            body: JSON.stringify({
                model: 'text-embedding-3-small',
                input: text
            })
        });

        if (!response.ok) {
            console.error(`Embedding API error: ${response.status}`);
            return null;
        }

        const data = await response.json();
        if (data.data && data.data[0] && data.data[0].embedding) {
            const embedding = data.data[0].embedding;
            console.log(`✅ Embedding generated: ${embedding.length} dimensions`);
            return embedding;
        }

        return null;
    } catch (error) {
        console.error("Error generating embedding:", error.message);
        return null;
    }
}

/**
 * Download file from Telegram servers
 * @param {string} fileId - Telegram file ID
 * @returns {Promise<Buffer|null>} File buffer or null on error
 */
async function downloadTelegramFile(fileId) {
    try {
        // Get file path from Telegram
        const fileInfoUrl = `${BASE_URL}/getFile?file_id=${fileId}`;
        const fileInfoResponse = await fetch(fileInfoUrl);
        const fileInfoData = await fileInfoResponse.json();

        if (!fileInfoData.ok || !fileInfoData.result.file_path) {
            console.error("Failed to get file info:", fileInfoData);
            return null;
        }

        // Download file
        const fileUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${fileInfoData.result.file_path}`;
        const fileResponse = await fetch(fileUrl);
        const fileBuffer = await fileResponse.buffer();

        console.log(`✅ Downloaded file: ${fileInfoData.result.file_path} (${fileBuffer.length} bytes)`);
        return fileBuffer;
    } catch (error) {
        console.error("Error downloading file:", error.message);
        return null;
    }
}

/**
 * Transcribe voice message using OpenAI Whisper API
 * @param {Buffer} audioBuffer - Audio file buffer
 * @returns {Promise<string|null>} Transcribed text or null on error
 */
async function transcribeVoice(audioBuffer) {
    if (!OPENAI_API_KEY) {
        console.error("OpenAI API key not configured for voice transcription");
        return null;
    }

    try {
        const FormData = (await import('form-data')).default;
        const formData = new FormData();
        formData.append('file', audioBuffer, {
            filename: 'voice.ogg',
            contentType: 'audio/ogg'
        });
        formData.append('model', 'whisper-1');
        formData.append('language', 'ru'); // Default to Russian

        const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${OPENAI_API_KEY}`,
                ...formData.getHeaders()
            },
            body: formData
        });

        const data = await response.json();

        if (data.text) {
            console.log(`✅ Voice transcribed: "${data.text.substring(0, 50)}..."`);
            return data.text;
        }

        console.error("Whisper API error:", data);
        return null;
    } catch (error) {
        console.error("Error transcribing voice:", error.message);
        return null;
    }
}

/**
 * Handle voice message - transcribe and save as moment
 * @param {object} message - Telegram message object with voice
 * @returns {Promise<boolean>} True if handled successfully
 */
async function handleVoiceMessage(message) {
    const chatId = message.chat.id;
    const user = getOrCreateUser(message.from);
    const voice = message.voice;
    const state = userStates.get(user.telegram_id);

    // Only handle voice if user is in "adding moment" state or has completed onboarding
    if (!user.onboarding_completed) {
        await sendMessage(chatId, "Сначала завершите настройку бота с помощью /start");
        return true;
    }

    // Show typing indicator while processing
    const loadingIndicator = startLoadingIndicator(chatId, 'typing');
    console.log(`🎤 Processing voice message for user ${user.telegram_id}, file_id: ${voice.file_id}`);

    try {
        // Download voice file
        const audioBuffer = await downloadTelegramFile(voice.file_id);
        if (!audioBuffer) {
            loadingIndicator.stop();
            await sendErrorMessage(chatId, 'voice_recognition', user.language_code);
            return true;
        }

        // Transcribe voice
        const transcribedText = await transcribeVoice(audioBuffer);
        if (!transcribedText || transcribedText.trim().length === 0) {
            loadingIndicator.stop();
            await sendErrorMessage(chatId, 'voice_recognition', user.language_code);
            return true;
        }

        // Generate embedding for the transcribed text
        const embedding = await generateEmbedding(transcribedText);

        // Save as moment with source_type 'voice' and store voice file ID
        const newMoment = addMoment(user.telegram_id, transcribedText, embedding, 'voice');
        newMoment.original_voice_file_id = voice.file_id;

        loadingIndicator.stop();

        // Track response time if user was asked a question
        if (state && state.question_asked_at) {
            const responseTimeMs = Date.now() - new Date(state.question_asked_at).getTime();
            trackResponseTime(user, responseTimeMs);
        }

        userStates.delete(user.telegram_id);

        const savedDate = formatDate(newMoment.created_at, user.language_code, true);

        // Show follow-up question
        const followUpQuestion = getRandomQuestion(user, 'follow_up');
        const responseText = `✨ <b>Голосовое сообщение сохранено!</b>\n\n` +
            `🎤 <i>"${escapeHtml(transcribedText)}"</i>\n\n` +
            `📅 ${savedDate}\n\n` +
            `${followUpQuestion}`;

        const momentsCount = getUserMoments(user.telegram_id).length;
        const keyboard = {
            inline_keyboard: [
                [{ text: "➕ Добавить ещё", callback_data: "moments_add" }],
                [{ text: `📚 Мои моменты (${momentsCount})`, callback_data: "moments_view" }]
            ]
        };

        await sendMessage(chatId, responseText, keyboard);
        console.log(`✅ Voice moment saved for user ${user.telegram_id}: "${transcribedText.substring(0, 30)}..."`);
        return true;
    } catch (error) {
        loadingIndicator.stop();
        console.error("Error handling voice message:", error.message);
        await sendErrorMessage(chatId, 'generic', user.language_code);
        return true;
    }
}

/**
 * Add a moment to user's history (with optional embedding)
 * @param {number} userId - User ID
 * @param {string} content - Moment content
 * @param {Array|null} embedding - Pre-generated embedding (optional)
 * @param {string} sourceType - Source type: 'text' or 'voice'
 * @returns {object} The new moment object
 */
function addMoment(userId, content, embedding = null, sourceType = 'text') {
    if (!moments.has(userId)) {
        moments.set(userId, []);
    }
    const userMoments = moments.get(userId);
    const topics = extractTopics(content);
    const newMoment = {
        id: userMoments.length + 1,
        content: content,
        topics: topics,
        embedding: embedding,
        source_type: sourceType, // 'text' or 'voice'
        created_at: new Date()
    };
    userMoments.push(newMoment);

    // Update user statistics when moment is created
    const user = users.get(userId);
    if (user) {
        if (!user.statistics) {
            user.statistics = {
                current_streak: 0,
                best_streak: 0,
                total_moments: 0,
                questions_sent: 0,
                questions_answered: 0,
                total_response_time_ms: 0,
                response_count: 0,
                average_response_time_seconds: 0
            };
        }

        // Increment total moments count
        user.statistics.total_moments = (user.statistics.total_moments || 0) + 1;

        // Update last_activity date
        user.last_activity = new Date();

        // Update streak calculation
        const streakData = calculateStreak(userMoments);
        user.statistics.current_streak = streakData.currentStreak;
        user.statistics.best_streak = Math.max(
            user.statistics.best_streak || 0,
            streakData.bestStreak
        );

        console.log(`📊 Updated stats for user ${userId}: total_moments=${user.statistics.total_moments}, streak=${user.statistics.current_streak}`);
    }

    // Save data immediately after adding a moment
    saveDataToFile();
    console.log(`✅ Moment saved with topics: ${topics.join(', ')}${embedding ? ', embedding: ' + embedding.length + ' dims' : ''}`);
    return newMoment;
}

/**
 * Delete a specific moment by ID
 * @param {number} userId - User ID
 * @param {number} momentId - Moment ID to delete
 * @returns {boolean} True if deleted, false if not found
 */
function deleteMoment(userId, momentId) {
    const userMoments = moments.get(userId);
    if (!userMoments) return false;

    const index = userMoments.findIndex(m => m.id === momentId);
    if (index === -1) return false;

    userMoments.splice(index, 1);
    saveDataToFile();
    console.log(`✅ Moment ${momentId} deleted for user ${userId}`);
    return true;
}

/**
 * Track response time for statistics
 * @param {object} user - User object
 * @param {number} responseTimeMs - Response time in milliseconds
 */
function trackResponseTime(user, responseTimeMs) {
    if (!user.statistics) {
        user.statistics = {};
    }

    // Initialize response time tracking if not exists
    if (!user.statistics.total_response_time_ms) {
        user.statistics.total_response_time_ms = 0;
    }
    if (!user.statistics.response_count) {
        user.statistics.response_count = 0;
    }

    // Add this response time to the totals
    user.statistics.total_response_time_ms += responseTimeMs;
    user.statistics.response_count += 1;

    // Calculate average (in seconds for display)
    user.statistics.average_response_time_seconds = Math.round(
        user.statistics.total_response_time_ms / user.statistics.response_count / 1000
    );

    // Save the updated user data
    saveDataToFile();
}

/**
 * Get average response time formatted for display
 * @param {object} user - User object
 * @returns {string} Formatted average response time
 */
function getFormattedResponseTime(user) {
    if (!user.statistics?.response_count || user.statistics.response_count === 0) {
        return null;
    }

    const avgSeconds = user.statistics.average_response_time_seconds || 0;

    if (avgSeconds < 60) {
        return `${avgSeconds} сек.`;
    } else if (avgSeconds < 3600) {
        const minutes = Math.floor(avgSeconds / 60);
        const seconds = avgSeconds % 60;
        return seconds > 0 ? `${minutes} мин. ${seconds} сек.` : `${minutes} мин.`;
    } else {
        const hours = Math.floor(avgSeconds / 3600);
        const minutes = Math.floor((avgSeconds % 3600) / 60);
        return minutes > 0 ? `${hours} ч. ${minutes} мин.` : `${hours} ч.`;
    }
}

/**
 * Get a specific moment by ID
 * @param {number} userId - User ID
 * @param {number} momentId - Moment ID
 * @returns {object|null} Moment object or null if not found
 */
function getMomentById(userId, momentId) {
    const userMoments = moments.get(userId);
    if (!userMoments) return null;
    return userMoments.find(m => m.id === momentId) || null;
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
            username: telegramUser.username || null,
            first_name: telegramUser.first_name || "друг",
            language_code: telegramUser.language_code || "ru",
            formal_address: false,
            onboarding_completed: false,
            notifications_enabled: true,
            active_hours_start: "09:00",
            active_hours_end: "21:00",
            notification_interval_hours: 3,
            timezone: "UTC", // User's timezone (e.g., "UTC", "Europe/Moscow", "+03:00")
            created_at: new Date(),
            // Initialize user statistics with default values
            statistics: {
                current_streak: 0,
                best_streak: 0,
                total_moments: 0,
                questions_sent: 0,
                questions_answered: 0,
                total_response_time_ms: 0,
                response_count: 0,
                average_response_time_seconds: 0
            }
        });
        console.log(`✅ Created new user ${userId} with initialized statistics`);
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
 * Send a document/file
 * Uses multipart/form-data to send file content directly
 */
async function sendDocument(chatId, content, filename, caption = "") {
    const url = `${BASE_URL}/sendDocument`;

    // Create a Blob from the content
    const blob = new Blob([content], { type: 'application/json' });

    // Create FormData
    const formData = new FormData();
    formData.append('chat_id', chatId.toString());
    formData.append('document', blob, filename);
    if (caption) {
        formData.append('caption', caption);
        formData.append('parse_mode', 'HTML');
    }

    const response = await fetch(url, {
        method: 'POST',
        body: formData
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

/**
 * Send chat action (typing indicator, etc.)
 * @param {number} chatId - The chat ID
 * @param {string} action - The action: 'typing', 'upload_voice', 'record_voice', 'upload_document', etc.
 */
async function sendChatAction(chatId, action = 'typing') {
    const url = `${BASE_URL}/sendChatAction`;
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            chat_id: chatId,
            action: action
        })
    });
    return await response.json();
}

/**
 * Show loading indicator and return a function to clear it
 * @param {number} chatId - The chat ID
 * @param {string} action - The chat action to show
 * @returns {object} Object with interval ID for clearing
 */
function startLoadingIndicator(chatId, action = 'typing') {
    // Send initial action
    sendChatAction(chatId, action);

    // Telegram chat actions expire after 5 seconds, so we repeat every 4 seconds
    const intervalId = setInterval(() => {
        sendChatAction(chatId, action);
    }, 4000);

    return {
        intervalId,
        stop: () => {
            clearInterval(intervalId);
            console.log(`⏹️ Stopped loading indicator for chat ${chatId}`);
        }
    };
}

/**
 * Show processing message and update it when done
 * @param {number} chatId - The chat ID
 * @param {string} processingMessage - Message to show during processing
 * @returns {Promise<object>} Message object with update function
 */
async function showProcessingMessage(chatId, processingMessage = "⏳ Обрабатываю...") {
    const result = await sendMessage(chatId, processingMessage);
    const messageId = result.result?.message_id;

    return {
        messageId,
        update: async (newText) => {
            if (messageId) {
                return await editMessage(chatId, messageId, newText);
            }
        },
        delete: async () => {
            if (messageId) {
                const url = `${BASE_URL}/deleteMessage`;
                await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chat_id: chatId,
                        message_id: messageId
                    })
                });
            }
        }
    };
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
            [{ text: "🌐 Часовой пояс", callback_data: "settings_timezone" }],
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

function getTimezoneKeyboard() {
    return {
        inline_keyboard: [
            [
                { text: "UTC", callback_data: "tz_UTC" },
                { text: "UTC+1", callback_data: "tz_+01:00" },
                { text: "UTC+2", callback_data: "tz_+02:00" }
            ],
            [
                { text: "UTC+3 (МСК)", callback_data: "tz_+03:00" },
                { text: "UTC+4", callback_data: "tz_+04:00" },
                { text: "UTC+5", callback_data: "tz_+05:00" }
            ],
            [
                { text: "UTC+6", callback_data: "tz_+06:00" },
                { text: "UTC+7", callback_data: "tz_+07:00" },
                { text: "UTC+8", callback_data: "tz_+08:00" }
            ],
            [
                { text: "UTC-5 (NY)", callback_data: "tz_-05:00" },
                { text: "UTC-8 (LA)", callback_data: "tz_-08:00" }
            ],
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
            // Set user state to "adding moment" with timestamp for response time tracking
            userStates.set(user.telegram_id, { state: 'adding_moment', question_asked_at: new Date() });
            const deepLinkQuestion = getRandomQuestion(user);
            await sendMessage(chatId,
                "✨ <b>Добавление момента</b>\n\n" +
                deepLinkQuestion + " " +
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

    // Build JSON export data (full data for file)
    const exportData = {
        export_date: new Date().toISOString(),
        format_version: "1.0",
        user: {
            telegram_id: user.telegram_id,
            first_name: user.first_name,
            language_code: user.language_code,
            formal_address: user.formal_address,
            active_hours_start: user.active_hours_start,
            active_hours_end: user.active_hours_end,
            notification_interval_hours: user.notification_interval_hours,
            notifications_enabled: user.notifications_enabled,
            onboarding_completed: user.onboarding_completed,
            created_at: user.created_at
        },
        moments: userMoments.map(m => ({
            id: m.id,
            content: m.content,
            created_at: m.created_at
        })),
        statistics: {
            total_moments: userMoments.length,
            first_moment_date: userMoments.length > 0 ? userMoments[0].created_at : null,
            last_moment_date: userMoments.length > 0 ? userMoments[userMoments.length - 1].created_at : null
        }
    };

    // Send JSON file
    const jsonContent = JSON.stringify(exportData, null, 2);
    const filename = `mindsethappybot_data_${user.telegram_id}_${new Date().toISOString().split('T')[0]}.json`;

    try {
        await sendDocument(chatId, jsonContent, filename,
            "📦 <b>Твои данные в формате JSON</b>\n\nФайл содержит все твои данные в машиночитаемом формате."
        );
    } catch (err) {
        console.error("Failed to send document:", err.message);
        // Fall back to text message if document fails
    }

    // Build human-readable export text (summary)
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
    const { currentStreak, bestStreak } = calculateStreak(userMoments);

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
    statsText += `🔥 Текущий стрик: ${currentStreak} дн.\n`;
    statsText += `🏆 Лучший стрик: ${bestStreak} дн.\n`;
    const questionsSent = user.statistics?.questions_sent || 0;
    const questionsAnswered = user.statistics?.questions_answered || 0;
    statsText += `✉️ Отправлено вопросов: ${questionsSent}\n`;
    statsText += `✅ Отвечено: ${questionsAnswered}`;

    // Add percentage if questions were sent
    if (questionsSent > 0) {
        const answerPercentage = Math.round((questionsAnswered / questionsSent) * 100);
        statsText += ` (${answerPercentage}%)`;
    }
    statsText += "\n";

    // Add average response time if tracked
    const avgResponseTime = getFormattedResponseTime(user);
    if (avgResponseTime) {
        statsText += `⏱️ Среднее время ответа: ${avgResponseTime}\n`;
    }
    statsText += "\n";

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

// Page size for moments pagination
const MOMENTS_PAGE_SIZE = 5;

/**
 * Get moments keyboard with navigation
 * @param {number} userId - User ID
 * @param {number} totalMoments - Total number of moments
 * @param {number} [currentPage=0] - Current page (0-indexed)
 */
function getMomentsKeyboard(userId, totalMoments, currentPage = 0) {
    const keyboard = {
        inline_keyboard: []
    };

    const totalPages = Math.ceil(totalMoments / MOMENTS_PAGE_SIZE);

    if (totalMoments > 0) {
        // Pagination row (only if more than one page)
        if (totalPages > 1) {
            const paginationRow = [];
            if (currentPage > 0) {
                paginationRow.push({ text: "◀️ Назад", callback_data: `moments_page_${currentPage - 1}` });
            }
            paginationRow.push({ text: `📄 ${currentPage + 1}/${totalPages}`, callback_data: "moments_page_info" });
            if (currentPage < totalPages - 1) {
                paginationRow.push({ text: "Вперёд ▶️", callback_data: `moments_page_${currentPage + 1}` });
            }
            keyboard.inline_keyboard.push(paginationRow);
        }

        // Filter row
        keyboard.inline_keyboard.push([
            { text: "📅 Сегодня", callback_data: "moments_filter_today" },
            { text: "📅 Неделя", callback_data: "moments_filter_week" },
            { text: "📅 Месяц", callback_data: "moments_filter_month" }
        ]);
        keyboard.inline_keyboard.push([
            { text: "🔍 Поиск", callback_data: "moments_search" },
            { text: "🎲 Случайный", callback_data: "moments_random" }
        ]);
        keyboard.inline_keyboard.push([
            { text: "📂 По темам", callback_data: "moments_by_topics" }
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
 * Generate moments page text
 * @param {Array} userMoments - All user moments
 * @param {number} page - Page number (0-indexed)
 * @param {string} languageCode - User's language code
 * @returns {object} { text, momentsOnPage, totalPages }
 */
function generateMomentsPageText(userMoments, page, languageCode) {
    const totalMoments = userMoments.length;
    const totalPages = Math.ceil(totalMoments / MOMENTS_PAGE_SIZE);

    // Calculate slice indices for paginated moments (newest first)
    // We reverse, then slice by page
    const reversedMoments = [...userMoments].reverse();
    const startIdx = page * MOMENTS_PAGE_SIZE;
    const endIdx = startIdx + MOMENTS_PAGE_SIZE;
    const pageMoments = reversedMoments.slice(startIdx, endIdx);

    let momentsText = "📖 <b>Твои радостные моменты</b>\n\n";

    for (const moment of pageMoments) {
        const relativeDate = formatRelativeDate(moment.created_at, languageCode);
        const fullDate = formatDate(moment.created_at, languageCode, true);
        momentsText += `🌟 <i>${relativeDate}</i>\n`;
        momentsText += `${escapeHtml(moment.content)}\n`;
        momentsText += `<code>${fullDate}</code>\n\n`;
    }

    if (totalPages > 1) {
        momentsText += `\n📚 Страница ${page + 1} из ${totalPages} (всего: ${totalMoments})`;
    } else if (totalMoments > 0) {
        momentsText += `\n📚 Всего моментов: ${totalMoments}`;
    }

    return {
        text: momentsText,
        momentsOnPage: pageMoments.length,
        totalPages: totalPages
    };
}

/**
 * Filter moments by period
 * @param {Array} moments - All user moments
 * @param {string} period - 'today', 'week', or 'month'
 * @returns {Array} Filtered moments
 */
function filterMomentsByPeriod(moments, period) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    let cutoffDate;
    switch (period) {
        case 'today':
            cutoffDate = today;
            break;
        case 'week':
            cutoffDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
        case 'month':
            cutoffDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
            break;
        default:
            return moments;
    }

    return moments.filter(m => {
        const momentDate = new Date(m.created_at);
        return momentDate >= cutoffDate;
    });
}

/**
 * Search moments by text content
 * @param {Array} moments - All user moments
 * @param {string} query - Search query (case-insensitive)
 * @returns {Array} Matching moments
 */
function searchMoments(moments, query) {
    if (!query || query.trim().length === 0) {
        return [];
    }
    const lowerQuery = query.toLowerCase().trim();
    return moments.filter(m => {
        const content = (m.content || '').toLowerCase();
        return content.includes(lowerQuery);
    });
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

    // Schedule first notification for this user
    const nextNotificationTime = calculateNextNotificationTime(user);
    scheduleNotificationJob(user.telegram_id, nextNotificationTime, 'question');
    console.log(`📅 First notification scheduled for user ${user.telegram_id}`);

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
            // Set user state to dialog mode
            userStates.set(user.telegram_id, { state: 'free_dialog' });
            await sendMessage(chatId,
                "💬 <b>Режим диалога</b>\n\n" +
                "Я готов выслушать тебя. Расскажи, что у тебя на душе. " +
                "Я постараюсь помочь взглядом со стороны, " +
                "используя твою историю радостных моментов для поддержки. " +
                "Но помни — все решения принимаешь ты сам. 💝\n\n" +
                "Чтобы выйти из режима диалога, напиши /start",
                {
                    inline_keyboard: [
                        [{ text: "❌ Выйти из диалога", callback_data: "exit_dialog" }]
                    ]
                }
            );
            console.log(`✅ User ${user.telegram_id} entered free dialog mode`);
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
        case "settings_timezone":
            await editMessage(chatId, messageId,
                "🌐 <b>Часовой пояс</b>\n\n" +
                `Текущее значение: ${formatTimezoneDisplay(user.timezone || 'UTC')}\n\n` +
                "Выберите ваш часовой пояс:",
                getTimezoneKeyboard()
            );
            break;
        case "settings_reset":
            user.active_hours_start = "09:00";
            user.active_hours_end = "21:00";
            user.notification_interval_hours = 3;
            user.notifications_enabled = true;
            user.timezone = "UTC";
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
    const timezoneDisplay = formatTimezoneDisplay(user.timezone || 'UTC');
    const settingsText = (
        "⚙️ <b>Настройки</b>\n\n" +
        `🕐 Активные часы: ${user.active_hours_start} - ${user.active_hours_end}\n` +
        `⏰ Интервал: каждые ${user.notification_interval_hours} ч.\n` +
        `🌐 Часовой пояс: ${timezoneDisplay}\n` +
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
 * Handle timezone selection
 */
async function handleTimezoneCallback(callback, action) {
    const chatId = callback.message.chat.id;
    const messageId = callback.message.message_id;
    const user = getOrCreateUser(callback.from);

    const timezone = action.replace("tz_", "");
    user.timezone = timezone;
    saveDataToFile(); // Persist settings change
    console.log(`✅ Timezone set to: ${timezone}`);

    // Show updated settings
    await showSettings(chatId, messageId, user);
    await answerCallback(callback.id, "✅ Часовой пояс сохранён!");
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
        // Set user state to "adding moment" with timestamp for response time tracking
        userStates.set(user.telegram_id, { state: 'adding_moment', question_asked_at: new Date() });

        // Use varied question formulation
        const momentQuestion = getRandomQuestion(user);
        await editMessage(chatId, messageId,
            "✨ <b>Добавление момента</b>\n\n" +
            momentQuestion + " " +
            "Просто напиши сообщение, и я сохраню его.\n\n" +
            "💡 Можно отправить текст или голосовое сообщение.",
            {
                inline_keyboard: [
                    [{ text: "❌ Отмена", callback_data: "moments_cancel" }]
                ]
            }
        );
        console.log(`✅ Prompted user to add moment with question: "${momentQuestion}"`);
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
            `<code>${fullDate}</code>\n\n` +
            `<i>ID: ${randomMoment.id}</i>`,
            {
                inline_keyboard: [
                    [{ text: "🎲 Ещё один", callback_data: "moments_random" }],
                    [{ text: "🗑️ Удалить", callback_data: `moment_delete_confirm_${randomMoment.id}` }],
                    [{ text: "📖 Все моменты", callback_data: "menu_moments" }],
                    [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
                ]
            }
        );
        console.log(`✅ Random moment shown (ID: ${randomMoment.id})`);
    } else if (action === "moments_search") {
        // Set user state to "searching moments"
        userStates.set(user.telegram_id, { state: 'searching_moments' });

        await editMessage(chatId, messageId,
            "🔍 <b>Поиск по моментам</b>\n\n" +
            "Введи текст для поиска в своих моментах.\n\n" +
            "💡 Поиск не чувствителен к регистру.",
            {
                inline_keyboard: [
                    [{ text: "❌ Отмена", callback_data: "moments_search_cancel" }]
                ]
            }
        );
        console.log("✅ Search mode activated");
    } else if (action === "moments_search_cancel") {
        // Clear search state
        userStates.delete(user.telegram_id);

        // Return to moments view
        await handleMomentsCommand({ chat: { id: chatId }, from: callback.from });
    } else if (action.startsWith("moments_page_")) {
        // Handle pagination
        const pageStr = action.replace("moments_page_", "");

        // Handle "info" button (does nothing, just shows current page)
        if (pageStr === "info") {
            await answerCallback(callback.id);
            return;
        }

        const page = parseInt(pageStr);
        if (isNaN(page) || page < 0) {
            await answerCallback(callback.id, "Неверная страница");
            return;
        }

        const { text, totalPages } = generateMomentsPageText(userMoments, page, user.language_code);

        if (page >= totalPages) {
            await answerCallback(callback.id, "Это последняя страница");
            return;
        }

        await editMessage(chatId, messageId, text, getMomentsKeyboard(user.telegram_id, userMoments.length, page));
        console.log(`✅ Moments page ${page + 1}/${totalPages} shown`);
    } else if (action === "moments_by_topics") {
        if (userMoments.length === 0) {
            await answerCallback(callback.id, "У тебя пока нет моментов");
            return;
        }

        // Group moments by topics
        const groups = groupMomentsByTopics(userMoments);
        const topicIds = Object.keys(groups).sort((a, b) => groups[b].length - groups[a].length);

        let topicsText = "📂 <b>Моменты по темам</b>\n\n";
        const keyboard = { inline_keyboard: [] };

        for (const topicId of topicIds) {
            const count = groups[topicId].length;
            const topicName = getTopicName(topicId, user.language_code);
            topicsText += `${topicName}: ${count}\n`;
            keyboard.inline_keyboard.push([
                { text: `${topicName} (${count})`, callback_data: `topic_${topicId}` }
            ]);
        }

        keyboard.inline_keyboard.push([
            { text: "📖 Все моменты", callback_data: "menu_moments" }
        ]);
        keyboard.inline_keyboard.push([
            { text: "⬅️ Главное меню", callback_data: "main_menu" }
        ]);

        await editMessage(chatId, messageId, topicsText, keyboard);
        console.log("✅ Topics view shown");
    } else if (action.startsWith("topic_")) {
        const topicId = action.replace("topic_", "");
        const groups = groupMomentsByTopics(userMoments);
        const topicMoments = groups[topicId] || [];

        if (topicMoments.length === 0) {
            await answerCallback(callback.id, "Нет моментов в этой теме");
            return;
        }

        const topicName = getTopicName(topicId, user.language_code);
        let momentsText = `${topicName}\n\n`;

        // Show last 5 moments in this topic
        const recentMoments = topicMoments.slice(-5).reverse();
        for (const moment of recentMoments) {
            const relativeDate = formatRelativeDate(moment.created_at, user.language_code);
            const fullDate = formatDate(moment.created_at, user.language_code, true);
            momentsText += `🌟 <i>${relativeDate}</i>\n`;
            momentsText += `${escapeHtml(moment.content)}\n`;
            momentsText += `<code>${fullDate}</code>\n\n`;
        }

        if (topicMoments.length > 5) {
            momentsText += `\n📚 Всего в теме: ${topicMoments.length}`;
        }

        await editMessage(chatId, messageId, momentsText, {
            inline_keyboard: [
                [{ text: "📂 По темам", callback_data: "moments_by_topics" }],
                [{ text: "📖 Все моменты", callback_data: "menu_moments" }],
                [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
            ]
        });
        console.log(`✅ Topic ${topicId} moments shown`);
    } else if (action.startsWith("moments_filter_")) {
        // Handle period filter
        const period = action.replace("moments_filter_", "");
        const filteredMoments = filterMomentsByPeriod(userMoments, period);

        const periodLabels = {
            today: "Сегодня",
            week: "За неделю",
            month: "За месяц"
        };

        if (filteredMoments.length === 0) {
            await editMessage(chatId, messageId,
                `📖 <b>Моменты: ${periodLabels[period]}</b>\n\n` +
                "Нет моментов за выбранный период.",
                {
                    inline_keyboard: [
                        [
                            { text: "📅 Сегодня", callback_data: "moments_filter_today" },
                            { text: "📅 Неделя", callback_data: "moments_filter_week" },
                            { text: "📅 Месяц", callback_data: "moments_filter_month" }
                        ],
                        [{ text: "📖 Все моменты", callback_data: "menu_moments" }],
                        [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
                    ]
                }
            );
            console.log(`✅ Filter ${period}: no moments`);
            return;
        }

        // Show filtered moments (last 5, newest first)
        const recentFiltered = filteredMoments.slice(-5).reverse();
        let momentsText = `📖 <b>Моменты: ${periodLabels[period]}</b>\n\n`;

        for (const moment of recentFiltered) {
            const relativeDate = formatRelativeDate(moment.created_at, user.language_code);
            const fullDate = formatDate(moment.created_at, user.language_code, true);
            momentsText += `🌟 <i>${relativeDate}</i>\n`;
            momentsText += `${escapeHtml(moment.content)}\n`;
            momentsText += `<code>${fullDate}</code>\n\n`;
        }

        if (filteredMoments.length > 5) {
            momentsText += `\n📚 Показано ${recentFiltered.length} из ${filteredMoments.length}`;
        }

        await editMessage(chatId, messageId, momentsText, {
            inline_keyboard: [
                [
                    { text: "📅 Сегодня", callback_data: "moments_filter_today" },
                    { text: "📅 Неделя", callback_data: "moments_filter_week" },
                    { text: "📅 Месяц", callback_data: "moments_filter_month" }
                ],
                [{ text: "📖 Все моменты", callback_data: "menu_moments" }],
                [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
            ]
        });
        console.log(`✅ Filter ${period}: ${filteredMoments.length} moments`);
    } else if (action.startsWith("moment_delete_confirm_")) {
        // Show delete confirmation dialog
        const momentId = parseInt(action.replace("moment_delete_confirm_", ""));
        const moment = getMomentById(user.telegram_id, momentId);

        if (!moment) {
            await answerCallback(callback.id, "Момент не найден");
            return;
        }

        const preview = moment.content.substring(0, 50) + (moment.content.length > 50 ? "..." : "");

        await editMessage(chatId, messageId,
            "🗑️ <b>Удаление момента</b>\n\n" +
            `Ты уверен, что хочешь удалить этот момент?\n\n` +
            `<i>\"${escapeHtml(preview)}\"</i>\n\n` +
            "⚠️ Это действие нельзя отменить.",
            {
                inline_keyboard: [
                    [
                        { text: "✅ Да, удалить", callback_data: `moment_delete_${momentId}` },
                        { text: "❌ Отмена", callback_data: "moments_random" }
                    ]
                ]
            }
        );
        console.log(`✅ Delete confirmation shown for moment ${momentId}`);
    } else if (action.startsWith("moment_delete_") && !action.includes("confirm")) {
        // Execute moment deletion
        const momentId = parseInt(action.replace("moment_delete_", ""));
        const success = deleteMoment(user.telegram_id, momentId);

        if (success) {
            await editMessage(chatId, messageId,
                "✅ <b>Момент удалён</b>\n\n" +
                "Момент был успешно удалён из твоей истории.",
                {
                    inline_keyboard: [
                        [{ text: "📖 Мои моменты", callback_data: "menu_moments" }],
                        [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
                    ]
                }
            );
            console.log(`✅ Moment ${momentId} deleted successfully`);
        } else {
            await editMessage(chatId, messageId,
                "❌ <b>Ошибка</b>\n\n" +
                "Не удалось удалить момент. Возможно, он уже был удалён.",
                {
                    inline_keyboard: [
                        [{ text: "📖 Мои моменты", callback_data: "menu_moments" }],
                        [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
                    ]
                }
            );
            console.log(`❌ Failed to delete moment ${momentId}`);
        }
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

    // Check if user is in "adding moment" state or "free dialog" mode
    const state = userStates.get(user.telegram_id);

    // Handle free dialog mode
    if (state && state.state === 'free_dialog') {
        console.log(`Processing dialog message from user ${user.telegram_id}`);

        // Show loading indicator during AI response generation
        const loadingIndicator = startLoadingIndicator(chatId, 'typing');
        console.log(`⏳ Started loading indicator for dialog response`);

        // Get user's moments for context
        const userMoments = getUserMoments(user.telegram_id);

        // Try to generate AI response
        let response = await generateDialogResponse(text, user, userMoments);

        // Stop loading indicator
        loadingIndicator.stop();

        // Fall back to template-based response if AI fails
        if (!response) {
            console.log("⚠️ AI response failed, using fallback");
            response = generateFallbackDialogResponse(text, user, userMoments);
        }

        await sendMessage(chatId, response, {
            inline_keyboard: [
                [{ text: "❌ Выйти из диалога", callback_data: "exit_dialog" }]
            ]
        });

        return true;
    }

    // Handle search mode
    if (state && state.state === 'searching_moments') {
        console.log(`Processing search query from user ${user.telegram_id}: "${text}"`);

        // Clear search state
        userStates.delete(user.telegram_id);

        const userMoments = getUserMoments(user.telegram_id);
        const searchResults = searchMoments(userMoments, text);

        if (searchResults.length === 0) {
            await sendMessage(chatId,
                `🔍 <b>Результаты поиска: "${escapeHtml(text)}"</b>\n\n` +
                "Ничего не найдено. Попробуй другой запрос.",
                {
                    inline_keyboard: [
                        [{ text: "🔍 Новый поиск", callback_data: "moments_search" }],
                        [{ text: "📖 Все моменты", callback_data: "menu_moments" }],
                        [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
                    ]
                }
            );
            console.log(`✅ Search "${text}": no results`);
            return true;
        }

        // Show search results (max 5)
        const displayResults = searchResults.slice(-5).reverse();
        let resultsText = `🔍 <b>Результаты поиска: "${escapeHtml(text)}"</b>\n\n`;
        resultsText += `Найдено: ${searchResults.length}\n\n`;

        for (const moment of displayResults) {
            const relativeDate = formatRelativeDate(moment.created_at, user.language_code);
            const fullDate = formatDate(moment.created_at, user.language_code, true);
            resultsText += `🌟 <i>${relativeDate}</i>\n`;
            resultsText += `${escapeHtml(moment.content)}\n`;
            resultsText += `<code>${fullDate}</code>\n\n`;
        }

        if (searchResults.length > 5) {
            resultsText += `\n📚 Показано ${displayResults.length} из ${searchResults.length}`;
        }

        await sendMessage(chatId, resultsText, {
            inline_keyboard: [
                [{ text: "🔍 Новый поиск", callback_data: "moments_search" }],
                [{ text: "📖 Все моменты", callback_data: "menu_moments" }],
                [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
            ]
        });
        console.log(`✅ Search "${text}": ${searchResults.length} results`);
        return true;
    }

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

        // Calculate response time if question was asked at a known time
        let responseTimeMs = null;
        if (state.question_asked_at) {
            responseTimeMs = new Date() - new Date(state.question_asked_at);
            // Track response time in user statistics
            trackResponseTime(user, responseTimeMs);
            console.log(`⏱️ Response time: ${Math.round(responseTimeMs / 1000)}s`);
        }

        // Show loading indicator during embedding generation
        await sendChatAction(chatId, 'typing');
        console.log(`⏳ Started loading indicator for moment saving`);

        // Generate embedding for the moment
        const embedding = await generateEmbedding(text);

        // Save the moment (with potentially truncated text and embedding)
        const newMoment = addMoment(user.telegram_id, text, embedding);
        userStates.delete(user.telegram_id);

        const savedDate = formatDate(newMoment.created_at, user.language_code, true);

        // Build response message
        let responseText = "✨ <b>Момент сохранён!</b>\n\n" +
            `🌟 ${escapeHtml(text)}\n\n` +
            `📅 ${savedDate}\n\n`;

        if (wasTruncated) {
            responseText += "⚠️ <i>Сообщение было сокращено до допустимой длины.</i>\n\n";
        }

        // Add follow-up question to encourage adding more moments
        const followUpQuestion = getRandomQuestion(user, 'follow_up');
        responseText += `${followUpQuestion}`;

        // Provide keyboard with option to add another moment
        const momentsCount = getUserMoments(user.telegram_id).length;
        const keyboard = {
            inline_keyboard: [
                [{ text: "➕ Добавить ещё", callback_data: "moments_add" }],
                [{ text: `📚 Мои моменты (${momentsCount})`, callback_data: "moments_view" }],
                [{ text: "📊 Статистика", callback_data: "stats" }]
            ]
        };

        await sendMessage(chatId, responseText, keyboard);
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
        } else if (update.message && update.message.voice) {
            // Handle voice messages
            await handleVoiceMessage(update.message);
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
        } else if (callbackData.startsWith("tz_")) {
            await handleTimezoneCallback(update.callback_query, callbackData);
        } else if (callbackData === "address_change_informal" || callbackData === "address_change_formal") {
            await handleAddressChangeCallback(update.callback_query, callbackData === "address_change_formal");
        } else if (callbackData.startsWith("moments_")) {
            await handleMomentsCallback(update.callback_query, callbackData);
        } else if (callbackData === "exit_dialog") {
            // Exit free dialog mode
            userStates.delete(update.callback_query.from.id);
            await editMessage(
                update.callback_query.message.chat.id,
                update.callback_query.message.message_id,
                "✅ Вышли из режима диалога.\n\nИспользуй меню для навигации.",
                getMainMenuInline()
            );
            await answerCallback(update.callback_query.id, "Вышли из диалога");
            console.log("✅ User exited free dialog mode");
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

    // Start the job scheduler for notifications
    startJobScheduler();

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
