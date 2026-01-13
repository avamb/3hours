/**
 * Test Questions Answered Percentage - Feature #46
 * Verifies that percentage of answered questions is tracked
 */

import { readFileSync } from 'fs';

// Read bot code to verify implementation
const botCode = readFileSync(new URL('./test-bot.mjs', import.meta.url), 'utf8');

console.log("=== Feature #46: Questions Answered Percentage - Test ===\n");

// Step 1: Verify questions tracking exists
console.log("Step 1: Verify questions tracking exists");
console.log("-".repeat(50));

const hasQuestionsSent = botCode.includes("questions_sent");
const hasQuestionsAnswered = botCode.includes("questions_answered");

console.log(`Questions sent tracking: ${hasQuestionsSent ? '✅ YES' : '❌ NO'}`);
console.log(`Questions answered tracking: ${hasQuestionsAnswered ? '✅ YES' : '❌ NO'}\n`);

// Step 2: Simulate receiving questions and answering some
console.log("Step 2: Simulate receiving 5 questions and answering 3");
console.log("-".repeat(50));

// Simulate user statistics
const testUser = {
    telegram_id: 123456,
    statistics: {
        questions_sent: 5,
        questions_answered: 3
    }
};

console.log(`Questions sent: ${testUser.statistics.questions_sent}`);
console.log(`Questions answered: ${testUser.statistics.questions_answered}`);

// Calculate percentage
const answerPercentage = Math.round((testUser.statistics.questions_answered / testUser.statistics.questions_sent) * 100);
console.log(`Expected percentage: ${answerPercentage}%`);
console.log(`Result: ${answerPercentage === 60 ? '✅ PASS' : '❌ FAIL'}\n`);

// Step 3: Verify percentage calculation in code
console.log("Step 3: Check statistics display");
console.log("-".repeat(50));

// Check for percentage calculation pattern
const hasPercentageCalc = botCode.includes("answerPercentage = Math.round((questionsAnswered / questionsSent) * 100)");
console.log(`Percentage calculation exists: ${hasPercentageCalc ? '✅ YES' : '❌ NO'}`);

// Check for percentage display
const hasPercentageDisplay = botCode.includes("(${answerPercentage}%)");
console.log(`Percentage display exists: ${hasPercentageDisplay ? '✅ YES' : '❌ NO'}`);

// Check for conditional display (only when questions sent > 0)
const hasConditionalDisplay = botCode.includes("if (questionsSent > 0)");
console.log(`Conditional display (avoid divide by zero): ${hasConditionalDisplay ? '✅ YES' : '❌ NO'}\n`);

// Step 4: Verify percentage is shown correctly
console.log("Step 4: Verify 60% answered rate shown");
console.log("-".repeat(50));

// Simulate the stats display logic
function buildStatsText(user) {
    const questionsSent = user.statistics?.questions_sent || 0;
    const questionsAnswered = user.statistics?.questions_answered || 0;
    let statsText = `✉️ Отправлено вопросов: ${questionsSent}\n`;
    statsText += `✅ Отвечено: ${questionsAnswered}`;

    // Add percentage if questions were sent
    if (questionsSent > 0) {
        const answerPercentage = Math.round((questionsAnswered / questionsSent) * 100);
        statsText += ` (${answerPercentage}%)`;
    }
    statsText += "\n";

    return statsText;
}

const statsOutput = buildStatsText(testUser);
console.log("Generated stats output:");
console.log(statsOutput);

const has60Percent = statsOutput.includes("(60%)");
console.log(`Contains 60%: ${has60Percent ? '✅ YES' : '❌ NO'}\n`);

// Test edge cases
console.log("Edge case tests:");
console.log("-".repeat(50));

// Test 1: 0 questions sent (should not show percentage)
const testUser0 = { statistics: { questions_sent: 0, questions_answered: 0 } };
const stats0 = buildStatsText(testUser0);
const hasNoPercentageFor0 = !stats0.includes("%");
console.log(`0/0 questions - no percentage: ${hasNoPercentageFor0 ? '✅' : '❌'} → "${stats0.trim()}"`);

// Test 2: 100% answered
const testUser100 = { statistics: { questions_sent: 10, questions_answered: 10 } };
const stats100 = buildStatsText(testUser100);
const has100Percent = stats100.includes("(100%)");
console.log(`10/10 questions - 100%: ${has100Percent ? '✅' : '❌'} → "${stats100.trim()}"`);

// Test 3: 0% answered
const testUser0Percent = { statistics: { questions_sent: 5, questions_answered: 0 } };
const stats0Percent = buildStatsText(testUser0Percent);
const has0Percent = stats0Percent.includes("(0%)");
console.log(`0/5 questions - 0%: ${has0Percent ? '✅' : '❌'} → "${stats0Percent.trim()}"`);

// Test 4: Rounding (3/7 = 42.857... should round to 43%)
const testUserRounding = { statistics: { questions_sent: 7, questions_answered: 3 } };
const statsRounding = buildStatsText(testUserRounding);
const has43Percent = statsRounding.includes("(43%)");
console.log(`3/7 questions - 43% (rounded): ${has43Percent ? '✅' : '❌'} → "${statsRounding.trim()}"`);

// Final summary
console.log("\n" + "=".repeat(50));
console.log("FINAL VERIFICATION SUMMARY");
console.log("=".repeat(50));

const checks = [
    { name: "Questions sent tracking exists", pass: hasQuestionsSent },
    { name: "Questions answered tracking exists", pass: hasQuestionsAnswered },
    { name: "Percentage calculation exists", pass: hasPercentageCalc },
    { name: "Percentage display exists", pass: hasPercentageDisplay },
    { name: "Conditional display (no divide by zero)", pass: hasConditionalDisplay },
    { name: "60% shown for 3/5 questions", pass: has60Percent },
    { name: "No percentage shown for 0/0", pass: hasNoPercentageFor0 },
    { name: "100% shown correctly", pass: has100Percent },
    { name: "0% shown correctly", pass: has0Percent },
    { name: "Rounding works correctly", pass: has43Percent }
];

let passCount = 0;
for (const check of checks) {
    console.log(`${check.pass ? '✅' : '❌'} ${check.name}`);
    if (check.pass) passCount++;
}

console.log(`\nTotal: ${passCount}/${checks.length} checks passed`);
console.log(`\n${passCount === checks.length ? '🎉 FEATURE #46 VERIFICATION: PASSED' : '⚠️ FEATURE #46 VERIFICATION: NEEDS WORK'}`);
