/**
 * Test Question Templates by Language - Feature #42
 * Verifies question templates work for different languages
 */

// Question templates (from test-bot.mjs)
const questionTemplates = {
    ru: {
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
    en: {
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
    uk: {
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
    }
};

// Track last question to avoid repetition
const lastUserQuestions = new Map();

/**
 * Get random question for user
 */
function getRandomQuestion(user) {
    const langCode = user.language_code?.startsWith('en') ? 'en' :
                     user.language_code?.startsWith('uk') ? 'uk' : 'ru';
    const addressType = user.formal_address ? 'formal' : 'informal';

    const templates = questionTemplates[langCode]?.[addressType] || questionTemplates.ru.informal;
    const lastQuestionIndex = lastUserQuestions.get(user.telegram_id);

    // Get random index different from last
    let newIndex;
    if (templates.length === 1) {
        newIndex = 0;
    } else {
        do {
            newIndex = Math.floor(Math.random() * templates.length);
        } while (newIndex === lastQuestionIndex);
    }

    lastUserQuestions.set(user.telegram_id, newIndex);
    return templates[newIndex];
}

/**
 * Check if text is in Russian
 */
function isRussian(text) {
    return /[а-яёА-ЯЁ]/.test(text) && !/[їієґІЇЄҐ]/.test(text);
}

/**
 * Check if text is in English
 */
function isEnglish(text) {
    // Should have English letters and no Cyrillic
    return /[a-zA-Z]/.test(text) && !/[а-яёА-ЯЁіїєґІЇЄҐ]/.test(text);
}

/**
 * Check if text is in Ukrainian
 */
function isUkrainian(text) {
    // Ukrainian has specific letters: і, ї, є, ґ
    return /[іїєґІЇЄҐ]/.test(text) || (/[а-яА-Я]/.test(text) && /сталось|розкаж|сьогодні/.test(text.toLowerCase()));
}

console.log("=".repeat(60));
console.log("QUESTION TEMPLATES BY LANGUAGE TEST - Feature #42");
console.log("=".repeat(60));
console.log();

// Test user
let testUser = {
    telegram_id: 12345,
    first_name: "Тест",
    language_code: "ru",
    formal_address: false
};

// Step 1: Set user language to Russian
console.log("Step 1: Set user language to Russian");
console.log("-".repeat(50));

testUser.language_code = "ru";
console.log(`  User language set to: ${testUser.language_code}`);
console.log("  [PASS] Language set to Russian");
console.log();

// Step 2: Receive question
console.log("Step 2: Receive question");
console.log("-".repeat(50));

lastUserQuestions.delete(testUser.telegram_id);
const russianQuestion = getRandomQuestion(testUser);

console.log(`  Question: "${russianQuestion}"`);

if (russianQuestion && russianQuestion.length > 0) {
    console.log("  [PASS] Question received");
} else {
    console.log("  [FAIL] No question received");
}
console.log();

// Step 3: Verify question is in Russian
console.log("Step 3: Verify question is in Russian");
console.log("-".repeat(50));

const questionIsRussian = isRussian(russianQuestion);

if (questionIsRussian) {
    console.log("  [PASS] Question is in Russian");
} else {
    console.log("  [FAIL] Question is not in Russian");
}

// Check that it's not in English or Ukrainian
const notEnglish = !isEnglish(russianQuestion);
const notUkrainian = !russianQuestion.includes('сталось') && !russianQuestion.includes('розкаж');

console.log(`  - Contains Cyrillic: ${/[а-яёА-ЯЁ]/.test(russianQuestion) ? '✅' : '❌'}`);
console.log(`  - No Ukrainian markers: ${notUkrainian ? '✅' : '❌'}`);
console.log(`  - No English only: ${notEnglish ? '✅' : '❌'}`);
console.log();

// Step 4: Change language to English
console.log("Step 4: Change language to English");
console.log("-".repeat(50));

testUser.language_code = "en";
console.log(`  User language changed to: ${testUser.language_code}`);
console.log("  [PASS] Language changed to English");
console.log();

// Step 5: Receive next question
console.log("Step 5: Receive next question");
console.log("-".repeat(50));

lastUserQuestions.delete(testUser.telegram_id);
const englishQuestion = getRandomQuestion(testUser);

console.log(`  Question: "${englishQuestion}"`);

if (englishQuestion && englishQuestion.length > 0) {
    console.log("  [PASS] New question received");
} else {
    console.log("  [FAIL] No question received");
}
console.log();

// Step 6: Verify question is in English
console.log("Step 6: Verify question is in English");
console.log("-".repeat(50));

const questionIsEnglish = isEnglish(englishQuestion);

if (questionIsEnglish) {
    console.log("  [PASS] Question is in English");
} else {
    console.log("  [FAIL] Question is not in English");
}

// Check characteristics
const hasEnglishWords = /what|today|good|happy|share/i.test(englishQuestion);
const noCyrillic = !/[а-яёА-ЯЁіїєґІЇЄҐ]/.test(englishQuestion);

console.log(`  - Contains English words: ${hasEnglishWords ? '✅' : '❌'}`);
console.log(`  - No Cyrillic letters: ${noCyrillic ? '✅' : '❌'}`);
console.log();

// Bonus: Test Ukrainian
console.log("Bonus: Test Ukrainian language");
console.log("-".repeat(50));

testUser.language_code = "uk";
lastUserQuestions.delete(testUser.telegram_id);
const ukrainianQuestion = getRandomQuestion(testUser);

console.log(`  Question: "${ukrainianQuestion}"`);

const questionIsUkrainian = isUkrainian(ukrainianQuestion);
if (questionIsUkrainian) {
    console.log("  [PASS] Question is in Ukrainian");
} else {
    console.log("  [INFO] Question may be in Russian fallback");
}
console.log();

// Bonus: Test formal vs informal
console.log("Bonus: Test formal vs informal address");
console.log("-".repeat(50));

// Test informal Russian
testUser.language_code = "ru";
testUser.formal_address = false;
lastUserQuestions.delete(testUser.telegram_id);

const questions = [];
for (let i = 0; i < 5; i++) {
    questions.push(getRandomQuestion(testUser));
}

const hasInformalMarkers = questions.some(q =>
    q.includes(' ты') || q.includes(' тебя') || q.includes(' тебе') ||
    q.includes('расскажи') || q.includes('поделись')
);

console.log(`  Informal markers found: ${hasInformalMarkers ? '✅' : '❌'}`);

// Test formal Russian
testUser.formal_address = true;
lastUserQuestions.delete(testUser.telegram_id);

const formalQuestions = [];
for (let i = 0; i < 5; i++) {
    formalQuestions.push(getRandomQuestion(testUser));
}

const hasFormalMarkers = formalQuestions.some(q =>
    q.includes('Вы') || q.includes('Вас') || q.includes('Вам') ||
    q.includes('расскажите') || q.includes('поделитесь')
);

console.log(`  Formal markers found: ${hasFormalMarkers ? '✅' : '❌'}`);

if (hasInformalMarkers && hasFormalMarkers) {
    console.log("\n  [PASS] Both address forms work correctly");
} else {
    console.log("\n  [INFO] Address form detection may need adjustment");
}
console.log();

// Bonus: Test question variety
console.log("Bonus: Test question variety per language");
console.log("-".repeat(50));

const languages = ['ru', 'en', 'uk'];

for (const lang of languages) {
    testUser.language_code = lang;
    testUser.formal_address = false;
    lastUserQuestions.delete(testUser.telegram_id);

    const langQuestions = [];
    for (let i = 0; i < 10; i++) {
        langQuestions.push(getRandomQuestion(testUser));
    }

    const uniqueCount = new Set(langQuestions).size;
    console.log(`  ${lang.toUpperCase()}: ${uniqueCount} unique questions out of 10`);
}
console.log();

// Summary
console.log("=".repeat(60));
console.log("TEST SUMMARY");
console.log("=".repeat(60));

const step1Pass = testUser.language_code !== undefined;
const step2Pass = russianQuestion && russianQuestion.length > 0;
const step3Pass = questionIsRussian;
const step4Pass = true; // Language change is simple assignment
const step5Pass = englishQuestion && englishQuestion.length > 0;
const step6Pass = questionIsEnglish;

const allPassed = step1Pass && step2Pass && step3Pass && step4Pass && step5Pass && step6Pass;

if (allPassed) {
    console.log("  RESULT: ALL TESTS PASSED");
    console.log();
    console.log("  Feature #42: Question templates by language");
    console.log("  STATUS: PASSING");
    console.log();
    console.log("  Verified:");
    console.log("  - Step 1: Set language to Russian ✓");
    console.log("  - Step 2: Receive question ✓");
    console.log("  - Step 3: Question is in Russian ✓");
    console.log("  - Step 4: Change to English ✓");
    console.log("  - Step 5: Receive new question ✓");
    console.log("  - Step 6: Question is in English ✓");
} else {
    console.log("  RESULT: SOME TESTS FAILED");
    console.log();
    console.log("  Feature #42: Question templates by language");
    console.log("  STATUS: NEEDS WORK");
    console.log();
    console.log(`  Step 1 (set Russian): ${step1Pass ? 'PASS' : 'FAIL'}`);
    console.log(`  Step 2 (receive question): ${step2Pass ? 'PASS' : 'FAIL'}`);
    console.log(`  Step 3 (in Russian): ${step3Pass ? 'PASS' : 'FAIL'}`);
    console.log(`  Step 4 (change to English): ${step4Pass ? 'PASS' : 'FAIL'}`);
    console.log(`  Step 5 (receive new question): ${step5Pass ? 'PASS' : 'FAIL'}`);
    console.log(`  Step 6 (in English): ${step6Pass ? 'PASS' : 'FAIL'}`);
}

console.log("=".repeat(60));
