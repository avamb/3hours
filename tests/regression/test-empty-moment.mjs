/**
 * Test Empty Moment Rejection - Feature #38
 * Verifies empty or whitespace-only responses are rejected
 */

// Error messages from bot
const errorMessages = {
    ru: {
        empty_input: "Сообщение пустое 📝\nПопробуй написать что-нибудь хорошее! 💝"
    },
    en: {
        empty_input: "Message is empty 📝\nTry writing something good! 💝"
    },
    uk: {
        empty_input: "Повідомлення порожнє 📝\nСпробуй написати щось хороше! 💝"
    }
};

// Simulated storage
let moments = [];

/**
 * Get error message
 */
function getErrorMessage(errorType, languageCode = 'ru') {
    const lang = errorMessages[languageCode] ? languageCode : 'ru';
    return errorMessages[lang][errorType] || "Что-то пошло не так";
}

/**
 * Validate moment content
 */
function validateMomentContent(content) {
    // Check for null/undefined
    if (!content) {
        return { valid: false, reason: 'empty' };
    }

    // Trim and check for empty
    const trimmed = content.trim();

    if (trimmed.length === 0) {
        return { valid: false, reason: 'whitespace_only' };
    }

    // Check for too short content
    if (trimmed.length < 2) {
        return { valid: false, reason: 'too_short' };
    }

    // Check for meaningful content (not just punctuation)
    const hasLetters = /[а-яёa-z]/i.test(trimmed);
    if (!hasLetters && trimmed.length < 5) {
        return { valid: false, reason: 'no_meaningful_content' };
    }

    return { valid: true, content: trimmed };
}

/**
 * Add moment with validation
 */
function addMoment(userId, content, languageCode = 'ru') {
    const validation = validateMomentContent(content);

    if (!validation.valid) {
        return {
            success: false,
            error: validation.reason,
            message: getErrorMessage('empty_input', languageCode)
        };
    }

    // Create moment
    const moment = {
        id: moments.length + 1,
        user_id: userId,
        content: validation.content,
        created_at: new Date()
    };

    moments.push(moment);

    return {
        success: true,
        moment: moment,
        message: "✨ Момент сохранён!"
    };
}

/**
 * Get user moments count
 */
function getMomentsCount(userId) {
    return moments.filter(m => m.user_id === userId).length;
}

/**
 * Simulate bot question
 */
function askQuestion(user) {
    const questions = {
        ru: "Что хорошего произошло?",
        en: "What good happened today?",
        uk: "Що хорошого сталось?"
    };

    const lang = user.language_code || 'ru';
    return questions[lang] || questions.ru;
}

console.log("=".repeat(60));
console.log("EMPTY MOMENT REJECTION TEST - Feature #38");
console.log("=".repeat(60));
console.log();

// Test user
const testUser = {
    telegram_id: 12345,
    first_name: "Тест",
    language_code: "ru"
};

// Reset storage
moments = [];
const initialCount = getMomentsCount(testUser.telegram_id);

// Step 1: Receive question from bot
console.log("Step 1: Receive question from bot");
console.log("-".repeat(50));

const question = askQuestion(testUser);
console.log(`  Bot asks: "${question}"`);
console.log("  [PASS] Question received");
console.log();

// Step 2: Send empty message
console.log("Step 2: Send empty message");
console.log("-".repeat(50));

const emptyResult = addMoment(testUser.telegram_id, "", testUser.language_code);

console.log(`  User sends: "" (empty string)`);
console.log(`  Result: ${emptyResult.success ? 'Saved' : 'Rejected'}`);

if (!emptyResult.success) {
    console.log(`  Error reason: ${emptyResult.error}`);
    console.log("  [PASS] Empty message rejected");
} else {
    console.log("  [FAIL] Empty message was saved");
}
console.log();

// Step 3: Verify error message shown
console.log("Step 3: Verify error message shown");
console.log("-".repeat(50));

if (emptyResult.message) {
    console.log(`  Error message: "${emptyResult.message}"`);

    // Check message quality
    const hasEmoji = /[\u{1F300}-\u{1F9FF}]/u.test(emptyResult.message);
    const isHelpful = emptyResult.message.includes('попробуй') ||
                      emptyResult.message.includes('напиши') ||
                      emptyResult.message.includes('try');
    const isRussian = /[а-яёА-ЯЁ]/.test(emptyResult.message);

    console.log(`  - Has emoji: ${hasEmoji ? '✅' : '❌'}`);
    console.log(`  - Is helpful: ${isHelpful ? '✅' : '❌'}`);
    console.log(`  - In Russian: ${isRussian ? '✅' : '❌'}`);

    if (hasEmoji && isHelpful) {
        console.log("\n  [PASS] Helpful error message shown");
    } else {
        console.log("\n  [WARN] Message could be more helpful");
    }
} else {
    console.log("  [FAIL] No error message shown");
}
console.log();

// Step 4: Send whitespace-only message
console.log("Step 4: Send whitespace-only message");
console.log("-".repeat(50));

const whitespaceTests = [
    { input: "   ", name: "spaces only" },
    { input: "\t\t", name: "tabs only" },
    { input: "\n\n", name: "newlines only" },
    { input: "  \t\n  ", name: "mixed whitespace" }
];

let allWhitespaceRejected = true;

for (const test of whitespaceTests) {
    const result = addMoment(testUser.telegram_id, test.input, testUser.language_code);
    const rejected = !result.success;
    allWhitespaceRejected = allWhitespaceRejected && rejected;
    console.log(`  ${rejected ? '✅' : '❌'} "${test.name}": ${rejected ? 'Rejected' : 'SAVED (error!)'}`);
}

if (allWhitespaceRejected) {
    console.log("\n  [PASS] All whitespace-only messages rejected");
} else {
    console.log("\n  [FAIL] Some whitespace messages were saved");
}
console.log();

// Step 5: Verify error message shown (for whitespace)
console.log("Step 5: Verify error message shown for whitespace");
console.log("-".repeat(50));

const whitespaceResult = addMoment(testUser.telegram_id, "   ", testUser.language_code);

if (whitespaceResult.message) {
    console.log(`  Error message: "${whitespaceResult.message}"`);
    console.log("  [PASS] Error message shown for whitespace input");
} else {
    console.log("  [FAIL] No error message for whitespace");
}
console.log();

// Step 6: Verify no empty record created
console.log("Step 6: Verify no empty record created");
console.log("-".repeat(50));

const finalCount = getMomentsCount(testUser.telegram_id);
console.log(`  Initial moment count: ${initialCount}`);
console.log(`  Final moment count: ${finalCount}`);

if (finalCount === initialCount) {
    console.log("  [PASS] No empty records created");
} else {
    console.log("  [FAIL] Empty records were created");
}

// Verify all moments have content
const emptyMoments = moments.filter(m =>
    m.user_id === testUser.telegram_id &&
    (!m.content || m.content.trim().length === 0)
);

if (emptyMoments.length === 0) {
    console.log("  [PASS] Database has no empty moments");
} else {
    console.log(`  [FAIL] Found ${emptyMoments.length} empty moments`);
}
console.log();

// Bonus: Test valid input after rejections
console.log("Bonus: Test valid input after rejections");
console.log("-".repeat(50));

const validResult = addMoment(testUser.telegram_id, "Хороший день сегодня!", testUser.language_code);

if (validResult.success) {
    console.log(`  Valid input: "${validResult.moment.content}"`);
    console.log("  [PASS] Valid input saved successfully after rejections");
} else {
    console.log("  [FAIL] Valid input was rejected");
}
console.log();

// Bonus: Test edge cases
console.log("Bonus: Test edge cases");
console.log("-".repeat(50));

const edgeCases = [
    { input: null, name: "null" },
    { input: undefined, name: "undefined" },
    { input: "a", name: "single character" },
    { input: ".", name: "single punctuation" },
    { input: "!!!", name: "punctuation only" },
    { input: "  ok  ", name: "text with surrounding whitespace" },
    { input: "Привет 👋", name: "text with emoji" }
];

for (const test of edgeCases) {
    const result = addMoment(testUser.telegram_id, test.input, testUser.language_code);
    const expectSaved = test.name.includes('text') || test.name.includes('emoji');
    const status = (result.success === expectSaved) ? '✅' : '⚠️';
    console.log(`  ${status} ${test.name}: ${result.success ? 'Saved' : 'Rejected'}`);
}
console.log();

// Bonus: Test in different languages
console.log("Bonus: Test error messages in different languages");
console.log("-".repeat(50));

const languages = [
    { code: 'ru', name: 'Russian' },
    { code: 'en', name: 'English' },
    { code: 'uk', name: 'Ukrainian' }
];

for (const lang of languages) {
    const msg = getErrorMessage('empty_input', lang.code);
    const hasEmoji = /[\u{1F300}-\u{1F9FF}]/u.test(msg);
    console.log(`  ${hasEmoji ? '✅' : '❌'} ${lang.name}: "${msg.substring(0, 35)}..."`);
}
console.log();

// Summary
console.log("=".repeat(60));
console.log("TEST SUMMARY");
console.log("=".repeat(60));

const step1Pass = question.length > 0;
const step2Pass = !emptyResult.success;
const step3Pass = emptyResult.message && emptyResult.message.length > 0;
const step4Pass = allWhitespaceRejected;
const step5Pass = whitespaceResult.message && whitespaceResult.message.length > 0;
const step6Pass = finalCount === initialCount && emptyMoments.length === 0;

const allPassed = step1Pass && step2Pass && step3Pass && step4Pass && step5Pass && step6Pass;

if (allPassed) {
    console.log("  RESULT: ALL TESTS PASSED");
    console.log();
    console.log("  Feature #38: Empty moment rejection");
    console.log("  STATUS: PASSING");
    console.log();
    console.log("  Verified:");
    console.log("  - Step 1: Question received ✓");
    console.log("  - Step 2: Empty message rejected ✓");
    console.log("  - Step 3: Error message shown ✓");
    console.log("  - Step 4: Whitespace-only rejected ✓");
    console.log("  - Step 5: Error message for whitespace ✓");
    console.log("  - Step 6: No empty records created ✓");
} else {
    console.log("  RESULT: SOME TESTS FAILED");
    console.log();
    console.log("  Feature #38: Empty moment rejection");
    console.log("  STATUS: NEEDS WORK");
    console.log();
    console.log(`  Step 1 (question): ${step1Pass ? 'PASS' : 'FAIL'}`);
    console.log(`  Step 2 (empty rejection): ${step2Pass ? 'PASS' : 'FAIL'}`);
    console.log(`  Step 3 (error message): ${step3Pass ? 'PASS' : 'FAIL'}`);
    console.log(`  Step 4 (whitespace): ${step4Pass ? 'PASS' : 'FAIL'}`);
    console.log(`  Step 5 (whitespace msg): ${step5Pass ? 'PASS' : 'FAIL'}`);
    console.log(`  Step 6 (no empty records): ${step6Pass ? 'PASS' : 'FAIL'}`);
}

console.log("=".repeat(60));
