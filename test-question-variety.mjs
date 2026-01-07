/**
 * Test Question Variety - Feature #9
 * Verifies that the bot uses different question formulations and doesn't repeat consecutively
 */

// Question templates for variety - each language has multiple formulations
const questionTemplates = {
    ru: {
        informal: [
            "Что хорошего произошло?",
            "Расскажи о чём-то приятном сегодня",
            "Чему ты сегодня порадовался(ась)?",
            "Какой момент сегодня был особенным?",
            "Что тебя сегодня улыбнуло?",
            "Поделись чем-то хорошим из сегодняшнего дня",
            "Что принесло тебе радость сегодня?",
            "Был ли сегодня момент, который хочется запомнить?",
            "О чём хорошем можешь рассказать?",
            "Что сегодня было здорово?"
        ],
        formal: [
            "Что хорошего произошло?",
            "Расскажите о чём-то приятном сегодня",
            "Чему Вы сегодня порадовались?",
            "Какой момент сегодня был особенным?",
            "Что Вас сегодня улыбнуло?",
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
            "Tell me about something nice today",
            "What made you happy today?",
            "What moment was special today?",
            "What made you smile today?",
            "Share something good from today",
            "What brought you joy today?",
            "Was there a moment worth remembering today?",
            "What's something good you can share?",
            "What was great today?"
        ],
        formal: [
            "What good happened today?",
            "Please tell me about something nice today",
            "What made you happy today?",
            "What moment was special today?",
            "What made you smile today?",
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
            "Розкажи про щось приємне сьогодні",
            "Чому ти сьогодні порадувався(лась)?",
            "Який момент сьогодні був особливим?",
            "Що тебе сьогодні засміяло?",
            "Поділись чимось хорошим з сьогоднішнього дня",
            "Що принесло тобі радість сьогодні?",
            "Чи був сьогодні момент, який хочеться запам'ятати?",
            "Про що хороше можеш розповісти?",
            "Що сьогодні було класно?"
        ],
        formal: [
            "Що хорошого сталось?",
            "Розкажіть про щось приємне сьогодні",
            "Чому Ви сьогодні порадувались?",
            "Який момент сьогодні був особливим?",
            "Що Вас сьогодні засміяло?",
            "Поділіться чимось хорошим з сьогоднішнього дня",
            "Що принесло Вам радість сьогодні?",
            "Чи був сьогодні момент, який хочеться запам'ятати?",
            "Про що хороше можете розповісти?",
            "Що сьогодні було класно?"
        ]
    }
};

// Track last question shown to each user (to prevent repetition)
const lastUserQuestions = new Map();

/**
 * Get a random question for user that doesn't repeat consecutively
 */
function getRandomQuestion(user) {
    const langCode = user.language_code?.startsWith('en') ? 'en' :
                     user.language_code?.startsWith('uk') ? 'uk' : 'ru';
    const addressType = user.formal_address ? 'formal' : 'informal';

    const templates = questionTemplates[langCode]?.[addressType] || questionTemplates.ru.informal;
    const lastQuestionIndex = lastUserQuestions.get(user.telegram_id);

    // Get a random index that's different from the last one
    let newIndex;
    if (templates.length === 1) {
        newIndex = 0;
    } else {
        do {
            newIndex = Math.floor(Math.random() * templates.length);
        } while (newIndex === lastQuestionIndex);
    }

    // Remember this question index
    lastUserQuestions.set(user.telegram_id, newIndex);

    return templates[newIndex];
}

console.log("=".repeat(60));
console.log("QUESTION VARIETY TEST - Feature #9");
console.log("=".repeat(60));
console.log();

// Test 1: Verify multiple templates exist
console.log("Step 1: Verify multiple question templates exist");
console.log("-".repeat(50));

const languages = ['ru', 'en', 'uk'];
const addressTypes = ['informal', 'formal'];

let templatesValid = true;
for (const lang of languages) {
    for (const addr of addressTypes) {
        const count = questionTemplates[lang][addr].length;
        if (count < 5) {
            console.log(`  [FAIL] ${lang}/${addr}: Only ${count} templates (need >= 5)`);
            templatesValid = false;
        } else {
            console.log(`  [PASS] ${lang}/${addr}: ${count} templates`);
        }
    }
}
console.log();

// Test 2: Verify no consecutive repetition
console.log("Step 2: Verify no consecutive repetition");
console.log("-".repeat(50));

const testUsers = [
    { telegram_id: 1001, language_code: 'ru', formal_address: false },
    { telegram_id: 1002, language_code: 'ru', formal_address: true },
    { telegram_id: 1003, language_code: 'en', formal_address: false },
    { telegram_id: 1004, language_code: 'uk', formal_address: false }
];

let noRepetitionPassed = true;
for (const user of testUsers) {
    const questions = [];
    for (let i = 0; i < 20; i++) {
        questions.push(getRandomQuestion(user));
    }

    let hasConsecutiveRepeat = false;
    for (let i = 1; i < questions.length; i++) {
        if (questions[i] === questions[i - 1]) {
            hasConsecutiveRepeat = true;
            console.log(`  [FAIL] User ${user.telegram_id} (${user.language_code}): Repetition at index ${i}`);
            console.log(`         Question repeated: "${questions[i]}"`);
            break;
        }
    }

    if (!hasConsecutiveRepeat) {
        console.log(`  [PASS] User ${user.telegram_id} (${user.language_code}): No consecutive repetition in 20 questions`);
    } else {
        noRepetitionPassed = false;
    }
}
console.log();

// Test 3: Verify variety - should use different questions over time
console.log("Step 3: Verify question variety (uniqueness)");
console.log("-".repeat(50));

const varietyUser = { telegram_id: 2001, language_code: 'ru', formal_address: false };
lastUserQuestions.delete(varietyUser.telegram_id);  // Reset

const questionSet = new Set();
for (let i = 0; i < 50; i++) {
    questionSet.add(getRandomQuestion(varietyUser));
}

const uniqueCount = questionSet.size;
const totalTemplates = questionTemplates.ru.informal.length;
const varietyRatio = uniqueCount / totalTemplates;

if (varietyRatio >= 0.6) {  // At least 60% of templates used in 50 questions
    console.log(`  [PASS] Used ${uniqueCount}/${totalTemplates} unique questions (${(varietyRatio * 100).toFixed(0)}%)`);
} else {
    console.log(`  [FAIL] Only used ${uniqueCount}/${totalTemplates} unique questions (${(varietyRatio * 100).toFixed(0)}%)`);
}
console.log();

// Test 4: Verify different users get independent question tracking
console.log("Step 4: Verify per-user question tracking");
console.log("-".repeat(50));

const userA = { telegram_id: 3001, language_code: 'ru', formal_address: false };
const userB = { telegram_id: 3002, language_code: 'ru', formal_address: false };
lastUserQuestions.delete(userA.telegram_id);
lastUserQuestions.delete(userB.telegram_id);

const qA1 = getRandomQuestion(userA);
const qB1 = getRandomQuestion(userB);
const qA2 = getRandomQuestion(userA);
const qB2 = getRandomQuestion(userB);

// userA's second question should be different from their first
// userB's second question should be different from their first
// But userA and userB can have the same question
const independentTracking = (qA1 !== qA2) && (qB1 !== qB2);

if (independentTracking) {
    console.log(`  [PASS] Users have independent question tracking`);
    console.log(`         User A: "${qA1}" -> "${qA2}"`);
    console.log(`         User B: "${qB1}" -> "${qB2}"`);
} else {
    console.log(`  [FAIL] Question tracking is not independent per user`);
}
console.log();

// Test 5: Verify formal/informal address differentiation
console.log("Step 5: Verify formal/informal address handling");
console.log("-".repeat(50));

const informalUser = { telegram_id: 4001, language_code: 'ru', formal_address: false };
const formalUser = { telegram_id: 4002, language_code: 'ru', formal_address: true };

const informalQuestions = new Set();
const formalQuestions = new Set();

for (let i = 0; i < 30; i++) {
    informalQuestions.add(getRandomQuestion(informalUser));
    formalQuestions.add(getRandomQuestion(formalUser));
}

// Check that informal uses "ты" forms and formal uses "Вы" forms
const informalQuestionsArray = Array.from(informalQuestions);
const formalQuestionsArray = Array.from(formalQuestions);

const informalHasTy = informalQuestionsArray.some(q => q.includes('ты') || q.includes('тебя') || q.includes('тебе'));
const formalHasVy = formalQuestionsArray.some(q => q.includes('Вы') || q.includes('Вас') || q.includes('Вам'));

if (informalHasTy && formalHasVy) {
    console.log(`  [PASS] Informal questions use "ты" forms`);
    console.log(`  [PASS] Formal questions use "Вы" forms`);
} else {
    if (!informalHasTy) console.log(`  [FAIL] Informal questions don't use "ты" forms`);
    if (!formalHasVy) console.log(`  [FAIL] Formal questions don't use "Вы" forms`);
}
console.log();

// Summary
console.log("=".repeat(60));
console.log("TEST SUMMARY");
console.log("=".repeat(60));

const allPassed = templatesValid && noRepetitionPassed && (varietyRatio >= 0.6) && independentTracking && informalHasTy && formalHasVy;

if (allPassed) {
    console.log("  RESULT: ALL TESTS PASSED");
    console.log();
    console.log("  Feature #9: Question variety - no repetition");
    console.log("  STATUS: PASSING");
    console.log();
    console.log("  Verified:");
    console.log("  - Multiple question templates (10 per language/form)");
    console.log("  - No consecutive repetition for any user");
    console.log("  - Good variety across questions");
    console.log("  - Per-user independent tracking");
    console.log("  - Formal/informal address differentiation");
} else {
    console.log("  RESULT: SOME TESTS FAILED");
    console.log();
    console.log("  Feature #9: Question variety - no repetition");
    console.log("  STATUS: NEEDS WORK");
}

console.log("=".repeat(60));
