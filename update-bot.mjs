/**
 * Script to add topic extraction functionality to test-bot.mjs
 */

import { readFileSync, writeFileSync } from 'fs';

const filePath = 'C:/Projects/3hours/test-bot.mjs';
let content = readFileSync(filePath, 'utf8');

// 1. Add topicKeywords constant after MOMENT_CONTENT_LIMIT
const topicKeywordsCode = `

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
`;

// Insert after MOMENT_CONTENT_LIMIT line
const insertAfter = 'const MOMENT_CONTENT_LIMIT = 2000;  // Reasonable limit for moment content';
content = content.replace(insertAfter, insertAfter + topicKeywordsCode);

// 2. Modify addMoment function to include topics
const oldAddMoment = `function addMoment(userId, content) {
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
}`;

const newAddMoment = `function addMoment(userId, content) {
    if (!moments.has(userId)) {
        moments.set(userId, []);
    }
    const userMoments = moments.get(userId);
    const topics = extractTopics(content);
    userMoments.push({
        id: userMoments.length + 1,
        content: content,
        topics: topics,
        created_at: new Date()
    });
    // Save data immediately after adding a moment
    saveDataToFile();
    console.log(\`✅ Moment saved with topics: \${topics.join(', ')}\`);
    return userMoments[userMoments.length - 1];
}`;

content = content.replace(oldAddMoment, newAddMoment);

// 3. Update getMomentsKeyboard to add "View by Topics" button
const oldGetMomentsKeyboard = `function getMomentsKeyboard(userId, totalMoments) {
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
}`;

const newGetMomentsKeyboard = `function getMomentsKeyboard(userId, totalMoments) {
    const keyboard = {
        inline_keyboard: []
    };

    if (totalMoments > 0) {
        keyboard.inline_keyboard.push([
            { text: "🎲 Случайный момент", callback_data: "moments_random" }
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
}`;

content = content.replace(oldGetMomentsKeyboard, newGetMomentsKeyboard);

// 4. Add handler for moments_by_topics callback - find handleMomentsCallback and add handler
const oldMomentsCallbackEnd = `} else if (action === "moments_random") {
        if (userMoments.length === 0) {
            await answerCallback(callback.id, "У тебя пока нет моментов");
            return;
        }

        const randomMoment = userMoments[Math.floor(Math.random() * userMoments.length)];
        const relativeDate = formatRelativeDate(randomMoment.created_at, user.language_code);
        const fullDate = formatDate(randomMoment.created_at, user.language_code, true);

        await editMessage(chatId, messageId,
            "🎲 <b>Случайный момент</b>\\n\\n" +
            \`🌟 <i>\${relativeDate}</i>\\n\` +
            \`\${escapeHtml(randomMoment.content)}\\n\` +
            \`<code>\${fullDate}</code>\`,
            {
                inline_keyboard: [
                    [{ text: "🎲 Ещё один", callback_data: "moments_random" }],
                    [{ text: "📖 Все моменты", callback_data: "menu_moments" }],
                    [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
                ]
            }
        );
        console.log("✅ Random moment shown");
    }`;

const newMomentsCallbackEnd = `} else if (action === "moments_random") {
        if (userMoments.length === 0) {
            await answerCallback(callback.id, "У тебя пока нет моментов");
            return;
        }

        const randomMoment = userMoments[Math.floor(Math.random() * userMoments.length)];
        const relativeDate = formatRelativeDate(randomMoment.created_at, user.language_code);
        const fullDate = formatDate(randomMoment.created_at, user.language_code, true);

        await editMessage(chatId, messageId,
            "🎲 <b>Случайный момент</b>\\n\\n" +
            \`🌟 <i>\${relativeDate}</i>\\n\` +
            \`\${escapeHtml(randomMoment.content)}\\n\` +
            \`<code>\${fullDate}</code>\`,
            {
                inline_keyboard: [
                    [{ text: "🎲 Ещё один", callback_data: "moments_random" }],
                    [{ text: "📖 Все моменты", callback_data: "menu_moments" }],
                    [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
                ]
            }
        );
        console.log("✅ Random moment shown");
    } else if (action === "moments_by_topics") {
        if (userMoments.length === 0) {
            await answerCallback(callback.id, "У тебя пока нет моментов");
            return;
        }

        // Group moments by topics
        const groups = groupMomentsByTopics(userMoments);
        const topicIds = Object.keys(groups).sort((a, b) => groups[b].length - groups[a].length);

        let topicsText = "📂 <b>Моменты по темам</b>\\n\\n";
        const keyboard = { inline_keyboard: [] };

        for (const topicId of topicIds) {
            const count = groups[topicId].length;
            const topicName = getTopicName(topicId, user.language_code);
            topicsText += \`\${topicName}: \${count}\\n\`;
            keyboard.inline_keyboard.push([
                { text: \`\${topicName} (\${count})\`, callback_data: \`topic_\${topicId}\` }
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
        let momentsText = \`\${topicName}\\n\\n\`;

        // Show last 5 moments in this topic
        const recentMoments = topicMoments.slice(-5).reverse();
        for (const moment of recentMoments) {
            const relativeDate = formatRelativeDate(moment.created_at, user.language_code);
            const fullDate = formatDate(moment.created_at, user.language_code, true);
            momentsText += \`🌟 <i>\${relativeDate}</i>\\n\`;
            momentsText += \`\${escapeHtml(moment.content)}\\n\`;
            momentsText += \`<code>\${fullDate}</code>\\n\\n\`;
        }

        if (topicMoments.length > 5) {
            momentsText += \`\\n📚 Всего в теме: \${topicMoments.length}\`;
        }

        await editMessage(chatId, messageId, momentsText, {
            inline_keyboard: [
                [{ text: "📂 По темам", callback_data: "moments_by_topics" }],
                [{ text: "📖 Все моменты", callback_data: "menu_moments" }],
                [{ text: "⬅️ Главное меню", callback_data: "main_menu" }]
            ]
        });
        console.log(\`✅ Topic \${topicId} moments shown\`);
    }`;

content = content.replace(oldMomentsCallbackEnd, newMomentsCallbackEnd);

// Write the updated content
writeFileSync(filePath, content, 'utf8');
console.log('✅ test-bot.mjs updated with topic extraction and grouping functionality');
