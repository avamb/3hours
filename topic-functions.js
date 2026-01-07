/**
 * Topic keywords mapping - maps keywords to topic categories
 * Supports Russian, English, and Ukrainian
 */
const topicKeywords = {
    'family': {
        emoji: '👨‍👩‍👧‍👦',
        name: { ru: 'Семья', en: 'Family', uk: 'Сімя' },
        keywords: ['семь', 'мама', 'папа', 'родител', 'брат', 'сестр', 'дочь', 'сын', 'ребен', 'дет', 'муж', 'жен', 'бабушк', 'дедушк', 'внук', 'родственник',
                   'family', 'mother', 'father', 'parent', 'brother', 'sister', 'daughter', 'son', 'child', 'husband', 'wife', 'grandma', 'grandpa',
                   'сімя', 'мати', 'батько', 'брат', 'сестра', 'дочка', 'син', 'дитина', 'чоловік', 'дружина']
    },
    'friends': {
        emoji: '👫',
        name: { ru: 'Друзья', en: 'Friends', uk: 'Друзі' },
        keywords: ['друг', 'подруг', 'друзь', 'компани', 'встреч', 'вечеринк', 'посиделк', 'общен',
                   'friend', 'buddy', 'pal', 'meeting', 'party', 'hangout',
                   'друг', 'подруга', 'товариш', 'зустріч', 'вечірка']
    },
    'work': {
        emoji: '💼',
        name: { ru: 'Работа', en: 'Work', uk: 'Робота' },
        keywords: ['работ', 'проект', 'коллег', 'босс', 'начальник', 'карьер', 'офис', 'зарплат', 'повыш', 'успех', 'задач', 'достижен',
                   'work', 'project', 'colleague', 'boss', 'career', 'office', 'salary', 'promotion', 'success', 'achievement', 'task',
                   'робот', 'проект', 'колега', 'бос', 'карєра', 'офіс', 'зарплата', 'підвищення', 'успіх']
    },
    'health': {
        emoji: '🏃',
        name: { ru: 'Здоровье', en: 'Health', uk: 'Здоровя' },
        keywords: ['здоров', 'спорт', 'тренировк', 'бег', 'йог', 'фитнес', 'зарядк', 'прогулк', 'сон', 'отдых', 'врач', 'медицин',
                   'health', 'sport', 'training', 'run', 'yoga', 'fitness', 'exercise', 'walk', 'sleep', 'rest', 'doctor',
                   'здоров', 'спорт', 'тренування', 'біг', 'йога', 'фітнес', 'зарядка', 'прогулянка', 'сон', 'відпочинок']
    },
    'food': {
        emoji: '🍕',
        name: { ru: 'Еда', en: 'Food', uk: 'Їжа' },
        keywords: ['еда', 'ед', 'обед', 'ужин', 'завтрак', 'ресторан', 'кафе', 'готов', 'вкусн', 'торт', 'пирог', 'рецепт',
                   'food', 'eat', 'lunch', 'dinner', 'breakfast', 'restaurant', 'cafe', 'cook', 'delicious', 'cake', 'recipe',
                   'їжа', 'їсти', 'обід', 'вечеря', 'сніданок', 'ресторан', 'кафе', 'готувати', 'смачн', 'торт']
    },
    'nature': {
        emoji: '🌿',
        name: { ru: 'Природа', en: 'Nature', uk: 'Природа' },
        keywords: ['природ', 'парк', 'лес', 'гор', 'мор', 'озер', 'река', 'цвет', 'сад', 'погод', 'солнц', 'закат', 'рассвет',
                   'nature', 'park', 'forest', 'mountain', 'sea', 'lake', 'river', 'flower', 'garden', 'weather', 'sun', 'sunset', 'sunrise',
                   'природа', 'парк', 'ліс', 'гори', 'море', 'озеро', 'річка', 'квіти', 'сад', 'погода', 'сонце', 'захід']
    },
    'travel': {
        emoji: '✈️',
        name: { ru: 'Путешествия', en: 'Travel', uk: 'Подорожі' },
        keywords: ['путешеств', 'поездк', 'отпуск', 'турист', 'город', 'стран', 'самолет', 'поезд', 'отель', 'экскурс',
                   'travel', 'trip', 'vacation', 'tourist', 'city', 'country', 'airplane', 'train', 'hotel', 'excursion',
                   'подорож', 'поїздка', 'відпустка', 'турист', 'місто', 'країна', 'літак', 'потяг', 'готель']
    },
    'hobby': {
        emoji: '🎨',
        name: { ru: 'Хобби', en: 'Hobby', uk: 'Хобі' },
        keywords: ['хобби', 'увлечен', 'творч', 'рисов', 'музык', 'книг', 'чита', 'фильм', 'кино', 'игр', 'танц', 'фото', 'пет', 'песн',
                   'hobby', 'passion', 'creative', 'draw', 'music', 'book', 'read', 'movie', 'cinema', 'game', 'dance', 'photo', 'sing', 'song',
                   'хобі', 'захоплення', 'творч', 'малюв', 'музика', 'книга', 'читати', 'фільм', 'кіно', 'гра', 'танц', 'фото']
    },
    'pets': {
        emoji: '🐾',
        name: { ru: 'Питомцы', en: 'Pets', uk: 'Улюбленці' },
        keywords: ['питом', 'собак', 'кот', 'кош', 'пес', 'щенок', 'котенок', 'животн', 'хомяк', 'попугай', 'рыбк', 'черепах',
                   'pet', 'dog', 'cat', 'puppy', 'kitten', 'animal', 'hamster', 'parrot', 'fish', 'turtle',
                   'улюбленець', 'собака', 'кіт', 'кішка', 'пес', 'цуценя', 'кошеня', 'тварина', 'хомяк', 'папуга']
    },
    'shopping': {
        emoji: '🛍️',
        name: { ru: 'Покупки', en: 'Shopping', uk: 'Покупки' },
        keywords: ['покупк', 'магазин', 'шоппинг', 'купил', 'подарок', 'одежд', 'обув', 'скидк', 'распродаж',
                   'shopping', 'store', 'shop', 'buy', 'bought', 'gift', 'clothes', 'shoes', 'sale', 'discount',
                   'покупк', 'магазин', 'шопінг', 'купив', 'подарунок', 'одяг', 'взуття', 'знижк', 'розпродаж']
    },
    'learning': {
        emoji: '📚',
        name: { ru: 'Учёба', en: 'Learning', uk: 'Навчання' },
        keywords: ['учеб', 'учил', 'выучил', 'урок', 'школ', 'универс', 'курс', 'экзамен', 'знан', 'навык', 'обучен',
                   'learn', 'study', 'lesson', 'school', 'university', 'course', 'exam', 'knowledge', 'skill', 'education',
                   'навчан', 'вчит', 'вивчив', 'урок', 'школа', 'універ', 'курс', 'іспит', 'знання', 'навичка']
    },
    'celebration': {
        emoji: '🎉',
        name: { ru: 'Праздники', en: 'Celebrations', uk: 'Свята' },
        keywords: ['праздник', 'день рождения', 'юбилей', 'свадьб', 'годовщин', 'рождеств', 'новый год', 'пасх', 'торжеств',
                   'holiday', 'birthday', 'anniversary', 'wedding', 'christmas', 'new year', 'easter', 'celebration', 'party',
                   'свято', 'день народження', 'ювілей', 'весілля', 'річниця', 'різдво', 'новий рік', 'паска']
    },
    'other': {
        emoji: '✨',
        name: { ru: 'Разное', en: 'Other', uk: 'Інше' },
        keywords: []
    }
};

/**
 * Extract topics from moment content
 * @param {string} content - The moment content text
 * @returns {string[]} Array of topic IDs
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
 * @param {string} topicId - Topic ID
 * @param {string} languageCode - User's language code
 * @returns {string} Localized topic name with emoji
 */
function getTopicName(topicId, languageCode = 'ru') {
    const topic = topicKeywords[topicId];
    if (!topic) return '✨ Разное';
    const lang = topic.name[languageCode] ? languageCode : 'ru';
    return topic.emoji + ' ' + topic.name[lang];
}

/**
 * Group moments by topics
 * @param {Array} userMoments - Array of moment objects
 * @returns {Object} Object with topic IDs as keys and arrays of moments as values
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

module.exports = { topicKeywords, extractTopics, getTopicName, groupMomentsByTopics };
