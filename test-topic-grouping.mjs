/**
 * Test script for topic extraction and grouping functionality
 * Tests Feature #75: Moments grouping by topics
 */

// Topic keywords mapping (same as in test-bot.mjs)
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

function getTopicName(topicId, languageCode = 'ru') {
    const topic = topicKeywords[topicId];
    if (!topic) return '✨ Разное';
    const lang = topic.name[languageCode] ? languageCode : 'ru';
    return topic.emoji + ' ' + topic.name[lang];
}

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

// Test data - moments with various topics
const testMoments = [
    { id: 1, content: "Сегодня гулял с семьей в парке, было очень здорово!", topics: null },
    { id: 2, content: "Встретился с друзьями, отлично провели время!", topics: null },
    { id: 3, content: "Закончил важный проект на работе, босс похвалил!", topics: null },
    { id: 4, content: "Пробежал 5 км на тренировке, чувствую себя отлично!", topics: null },
    { id: 5, content: "Приготовила вкусный ужин, всем понравилось!", topics: null },
    { id: 6, content: "Гуляла в парке, красивый закат!", topics: null },
    { id: 7, content: "Вернулись из отпуска, путешествие было чудесным!", topics: null },
    { id: 8, content: "Читала интересную книгу, не могла оторваться!", topics: null },
    { id: 9, content: "Моя собака научилась новому трюку!", topics: null },
    { id: 10, content: "Купила красивое платье на распродаже!", topics: null },
    { id: 11, content: "Сдала экзамен на отлично!", topics: null },
    { id: 12, content: "Отметили день рождения мамы!", topics: null },
    { id: 13, content: "Просто хороший день, ничего особенного", topics: null },
    { id: 14, content: "Had a great lunch with my friend at a new restaurant", topics: null },
    { id: 15, content: "Дети нарисовали мне открытку!", topics: null },
];

console.log("=== Feature #75: Moments Grouping by Topics - Test ===\n");

// Step 1: Extract topics for each moment
console.log("Step 1: Create moments with various topics");
console.log("-".repeat(50));

for (const moment of testMoments) {
    moment.topics = extractTopics(moment.content);
    console.log(`Moment ${moment.id}: "${moment.content.substring(0, 40)}..."`);
    console.log(`   Topics: ${moment.topics.map(t => getTopicName(t)).join(', ')}`);
}

// Step 2: Group moments by topic
console.log("\n\nStep 2: View moments grouped by topic");
console.log("-".repeat(50));

const groups = groupMomentsByTopics(testMoments);
const sortedTopics = Object.keys(groups).sort((a, b) => groups[b].length - groups[a].length);

for (const topicId of sortedTopics) {
    const topicMoments = groups[topicId];
    console.log(`\n${getTopicName(topicId)} (${topicMoments.length} moments):`);
    for (const moment of topicMoments) {
        console.log(`   - ${moment.content.substring(0, 50)}...`);
    }
}

// Step 3: Verify correct grouping
console.log("\n\nStep 3: Verify correct grouping");
console.log("-".repeat(50));

let allCorrect = true;
const expectedGroups = {
    1: ['family', 'nature'], // семьей, парке
    2: ['friends'],
    3: ['work'],
    4: ['health'],
    5: ['food'],
    6: ['nature'],
    7: ['travel'],
    8: ['hobby'],
    9: ['pets'],
    10: ['shopping'],
    11: ['learning'],
    12: ['celebration', 'family'], // день рождения, мамы
    13: ['other'],
    14: ['friends', 'food'], // friend, restaurant
    15: ['family', 'hobby'], // дети, рисовать -> family, hobby
};

for (const [id, expected] of Object.entries(expectedGroups)) {
    const moment = testMoments.find(m => m.id === parseInt(id));
    const actual = moment.topics;
    const hasExpected = expected.some(e => actual.includes(e));

    if (hasExpected) {
        console.log(`✅ Moment ${id}: Correctly assigned to ${actual.join(', ')}`);
    } else {
        console.log(`❌ Moment ${id}: Expected one of [${expected.join(', ')}], got [${actual.join(', ')}]`);
        allCorrect = false;
    }
}

// Step 4: Verify all moments appear in groups
console.log("\n\nStep 4: Verify all moments appear in groups");
console.log("-".repeat(50));

const momentsInGroups = new Set();
for (const topicMoments of Object.values(groups)) {
    for (const moment of topicMoments) {
        momentsInGroups.add(moment.id);
    }
}

const allMomentIds = new Set(testMoments.map(m => m.id));
const missingMoments = [...allMomentIds].filter(id => !momentsInGroups.has(id));

if (missingMoments.length === 0) {
    console.log(`✅ All ${testMoments.length} moments appear in groups`);
} else {
    console.log(`❌ Missing moments: ${missingMoments.join(', ')}`);
    allCorrect = false;
}

// Summary
console.log("\n\n=== Test Summary ===");
console.log("-".repeat(50));
console.log(`Total moments: ${testMoments.length}`);
console.log(`Total topic groups: ${Object.keys(groups).length}`);
console.log(`All moments accounted for: ${missingMoments.length === 0 ? 'YES' : 'NO'}`);
console.log(`\nResult: ${allCorrect ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);

// Topic distribution
console.log("\n\nTopic Distribution:");
for (const topicId of sortedTopics) {
    const count = groups[topicId].length;
    const bar = '█'.repeat(count);
    console.log(`${getTopicName(topicId).padEnd(25)} ${bar} ${count}`);
}
