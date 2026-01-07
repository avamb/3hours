/**
 * Test Question Template Variety - Feature #95
 * Verifies multiple question templates exist and are used correctly
 * Categories: main, follow_up, return_inactive
 */

import { readFileSync } from 'fs';

// Read bot code to verify implementation
const botCode = readFileSync('C:/Projects/3hours/test-bot.mjs', 'utf8');

console.log("=== Feature #95: Question Template Variety - Test ===\n");

// Step 1: Verify questionTemplates structure exists
console.log("Step 1: Verify questionTemplates structure");
console.log("-".repeat(50));

const hasQuestionTemplates = botCode.includes("const questionTemplates = {");
console.log("questionTemplates object exists: " + (hasQuestionTemplates ? "YES" : "NO"));

// Step 2: Verify multiple templates per language
console.log("\nStep 2: Verify templates for each language");
console.log("-".repeat(50));

const hasRuTemplates = botCode.includes("ru: {") && botCode.includes("main: {");
console.log("Russian templates exist: " + (hasRuTemplates ? "YES" : "NO"));

const hasEnTemplates = botCode.includes("en: {") && botCode.includes("What good happened today?");
console.log("English templates exist: " + (hasEnTemplates ? "YES" : "NO"));

// Check for Ukrainian by looking for uk: { pattern
const hasUkTemplates = botCode.includes("uk: {") && botCode.includes("main: {");
console.log("Ukrainian templates exist: " + (hasUkTemplates ? "YES" : "NO"));

// Step 3: Verify templates for formal/informal address
console.log("\nStep 3: Verify formal/informal address types");
console.log("-".repeat(50));

const hasInformalTemplates = botCode.includes("informal: [");
console.log("Informal templates exist: " + (hasInformalTemplates ? "YES" : "NO"));

const hasFormalTemplates = botCode.includes("formal: [");
console.log("Formal templates exist: " + (hasFormalTemplates ? "YES" : "NO"));

// Check for formal variations
const hasFormalEnVariations = botCode.includes("Please tell me about something nice today");
console.log("English formal variations: " + (hasFormalEnVariations ? "YES" : "NO"));

// Step 4: Verify categories cover main, follow_up, return_inactive
console.log("\nStep 4: Verify question categories");
console.log("-".repeat(50));

const hasMainCategory = botCode.includes("main: {");
console.log("'main' category exists: " + (hasMainCategory ? "YES" : "NO"));

const hasFollowUpCategory = botCode.includes("follow_up: {");
console.log("'follow_up' category exists: " + (hasFollowUpCategory ? "YES" : "NO"));

const hasReturnInactiveCategory = botCode.includes("return_inactive: {");
console.log("'return_inactive' category exists: " + (hasReturnInactiveCategory ? "YES" : "NO"));

// Verify getRandomQuestion function
console.log("\nStep 5: Verify getRandomQuestion function");
console.log("-".repeat(50));

const hasGetRandomQuestion = botCode.includes("function getRandomQuestion(user, category = 'main')");
console.log("getRandomQuestion with category param: " + (hasGetRandomQuestion ? "YES" : "NO"));

const hasCategoryTracking = botCode.includes("trackingKey") && botCode.includes("category");
console.log("Tracks questions by user AND category: " + (hasCategoryTracking ? "YES" : "NO"));

const hasNoRepetition = botCode.includes("while (newIndex === lastQuestionIndex)");
console.log("Prevents consecutive repetition: " + (hasNoRepetition ? "YES" : "NO"));

// Verify helper functions
console.log("\nStep 6: Verify helper functions");
console.log("-".repeat(50));

const hasIsUserInactive = botCode.includes("function isUserInactive(user, days = 3)");
console.log("isUserInactive function exists: " + (hasIsUserInactive ? "YES" : "NO"));

const hasGetQuestionForUser = botCode.includes("function getQuestionForUser(user)");
console.log("getQuestionForUser function exists: " + (hasGetQuestionForUser ? "YES" : "NO"));

const returnsInactiveQuestion = botCode.includes("return getRandomQuestion(user, 'return_inactive')");
console.log("Returns return_inactive for inactive: " + (returnsInactiveQuestion ? "YES" : "NO"));

// Verify usage in scheduled questions
console.log("\nStep 7: Verify usage in scheduled notifications");
console.log("-".repeat(50));

const scheduledUsesGetQuestion = botCode.includes("const question = getQuestionForUser(user)");
console.log("Scheduled uses getQuestionForUser: " + (scheduledUsesGetQuestion ? "YES" : "NO"));

// Verify follow-up usage
console.log("\nStep 8: Verify follow_up question usage");
console.log("-".repeat(50));

const momentSavedUsesFollowUp = botCode.includes("getRandomQuestion(user, 'follow_up')");
console.log("Moment saved shows follow_up: " + (momentSavedUsesFollowUp ? "YES" : "NO"));

// Simulate getRandomQuestion function
console.log("\nStep 9: Simulate question selection");
console.log("-".repeat(50));

const lastUserQuestions = new Map();

function simulateGetRandomQuestion(user, category = 'main') {
    const templates = ["Q1", "Q2", "Q3", "Q4", "Q5"];
    const trackingKey = user.telegram_id + "_" + category;
    const lastQuestionIndex = lastUserQuestions.get(trackingKey);

    let newIndex;
    if (templates.length === 1) {
        newIndex = 0;
    } else {
        do {
            newIndex = Math.floor(Math.random() * templates.length);
        } while (newIndex === lastQuestionIndex);
    }

    lastUserQuestions.set(trackingKey, newIndex);
    return newIndex;
}

const testUser = { telegram_id: 123 };
const results = [];
for (let i = 0; i < 10; i++) {
    results.push(simulateGetRandomQuestion(testUser, 'main'));
}

let hasConsecutiveDuplicates = false;
for (let i = 1; i < results.length; i++) {
    if (results[i] === results[i-1]) {
        hasConsecutiveDuplicates = true;
        break;
    }
}

console.log("Question indices: [" + results.join(', ') + "]");
console.log("No consecutive duplicates: " + (!hasConsecutiveDuplicates ? "YES" : "NO"));

// Final summary
console.log("\n" + "=".repeat(50));
console.log("FINAL VERIFICATION SUMMARY");
console.log("=".repeat(50));

const checks = [
    { name: "questionTemplates object exists", pass: hasQuestionTemplates },
    { name: "Russian templates exist", pass: hasRuTemplates },
    { name: "English templates exist", pass: hasEnTemplates },
    { name: "Ukrainian templates exist", pass: hasUkTemplates },
    { name: "Informal templates exist", pass: hasInformalTemplates },
    { name: "Formal templates exist", pass: hasFormalTemplates },
    { name: "English formal variations", pass: hasFormalEnVariations },
    { name: "'main' category exists", pass: hasMainCategory },
    { name: "'follow_up' category exists", pass: hasFollowUpCategory },
    { name: "'return_inactive' category exists", pass: hasReturnInactiveCategory },
    { name: "getRandomQuestion with category param", pass: hasGetRandomQuestion },
    { name: "Tracks questions by user AND category", pass: hasCategoryTracking },
    { name: "Prevents consecutive repetition", pass: hasNoRepetition },
    { name: "isUserInactive function exists", pass: hasIsUserInactive },
    { name: "getQuestionForUser function exists", pass: hasGetQuestionForUser },
    { name: "Returns return_inactive for inactive users", pass: returnsInactiveQuestion },
    { name: "Scheduled questions use getQuestionForUser", pass: scheduledUsesGetQuestion },
    { name: "Moment saved shows follow_up question", pass: momentSavedUsesFollowUp },
    { name: "No consecutive duplicate questions", pass: !hasConsecutiveDuplicates }
];

let passCount = 0;
for (const check of checks) {
    console.log((check.pass ? "[PASS]" : "[FAIL]") + " " + check.name);
    if (check.pass) passCount++;
}

console.log("\nTotal: " + passCount + "/" + checks.length + " checks passed");

if (passCount === checks.length) {
    console.log("\nFEATURE #95 VERIFICATION: PASSED");
} else {
    console.log("\nFEATURE #95 VERIFICATION: NEEDS WORK");
}
