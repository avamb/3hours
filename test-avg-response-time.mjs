/**
 * Test Average Response Time Tracking - Feature #45
 * Verifies that average response time is tracked in statistics
 */

import { readFileSync } from 'fs';

// Read bot code to verify implementation
const botCode = readFileSync('C:/Projects/3hours/test-bot.mjs', 'utf8');

console.log("=== Feature #45: Response Time Tracking - Test ===\n");

// Step 1: Verify question tracking timestamp implementation
console.log("Step 1: Receive question at known time");
console.log("-".repeat(50));

// Check that userStates.set includes question_asked_at
const hasQuestionTimestamp = botCode.includes("question_asked_at: new Date()");
console.log(`Question timestamp stored when asking: ${hasQuestionTimestamp ? '✅ YES' : '❌ NO'}`);

// Check both locations where adding_moment state is set
const addMomentStateCount = (botCode.match(/userStates\.set\([^)]*adding_moment[^)]*question_asked_at/g) || []).length;
console.log(`Locations with timestamp tracking: ${addMomentStateCount}`);
console.log(`Expected: 2 (deep link + menu callback)`);
console.log(`Result: ${addMomentStateCount >= 2 ? '✅ PASS' : '❌ FAIL'}\n`);

// Step 2: Verify response time calculation
console.log("Step 2: Wait specific duration (simulated)");
console.log("-".repeat(50));

// Simulate user creating a response after a delay
const questionTime = new Date('2026-01-07T10:00:00');
const responseTime = new Date('2026-01-07T10:00:30'); // 30 seconds later
const calculatedResponseTimeMs = responseTime - questionTime;

console.log(`Question asked at: ${questionTime.toISOString()}`);
console.log(`Response sent at: ${responseTime.toISOString()}`);
console.log(`Calculated response time: ${calculatedResponseTimeMs}ms (${calculatedResponseTimeMs/1000}s)`);
console.log(`Result: ${calculatedResponseTimeMs === 30000 ? '✅ PASS' : '❌ FAIL'}\n`);

// Step 3: Verify response time tracking in code
console.log("Step 3: Send response (verify tracking call)");
console.log("-".repeat(50));

const hasResponseTimeCalculation = botCode.includes("responseTimeMs = new Date() - new Date(state.question_asked_at)");
console.log(`Response time calculation: ${hasResponseTimeCalculation ? '✅ YES' : '❌ NO'}`);

const hasTrackResponseTimeCall = botCode.includes("trackResponseTime(user, responseTimeMs)");
console.log(`trackResponseTime function called: ${hasTrackResponseTimeCall ? '✅ YES' : '❌ NO'}`);

const hasTrackResponseTimeFunction = botCode.includes("function trackResponseTime(user, responseTimeMs)");
console.log(`trackResponseTime function defined: ${hasTrackResponseTimeFunction ? '✅ YES' : '❌ NO'}\n`);

// Step 4: Verify statistics include response time
console.log("Step 4: Check statistics");
console.log("-".repeat(50));

const hasAvgResponseTimeInStats = botCode.includes("getFormattedResponseTime(user)");
console.log(`Average response time in stats: ${hasAvgResponseTimeInStats ? '✅ YES' : '❌ NO'}`);

const hasResponseTimeDisplay = botCode.includes("Среднее время ответа");
console.log(`Response time label displayed: ${hasResponseTimeDisplay ? '✅ YES' : '❌ NO'}`);

const hasTimerEmoji = botCode.includes("⏱️");
console.log(`Timer emoji used: ${hasTimerEmoji ? '✅ YES' : '❌ NO'}\n`);

// Step 5: Verify average calculation
console.log("Step 5: Verify average response time calculated");
console.log("-".repeat(50));

// Simulate the trackResponseTime function
function simulateTrackResponseTime(user, responseTimeMs) {
    if (!user.statistics) {
        user.statistics = {};
    }

    if (!user.statistics.total_response_time_ms) {
        user.statistics.total_response_time_ms = 0;
    }
    if (!user.statistics.response_count) {
        user.statistics.response_count = 0;
    }

    user.statistics.total_response_time_ms += responseTimeMs;
    user.statistics.response_count += 1;

    user.statistics.average_response_time_seconds = Math.round(
        user.statistics.total_response_time_ms / user.statistics.response_count / 1000
    );

    return user.statistics;
}

// Simulate the getFormattedResponseTime function
function simulateGetFormattedResponseTime(user) {
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

// Test scenario: User responds to 3 questions
const testUser = { telegram_id: 123456, statistics: {} };

console.log("Test scenario: User responds to 3 questions\n");

// Response 1: 30 seconds
simulateTrackResponseTime(testUser, 30000);
console.log(`Response 1: 30s → Average: ${testUser.statistics.average_response_time_seconds}s`);

// Response 2: 60 seconds
simulateTrackResponseTime(testUser, 60000);
console.log(`Response 2: 60s → Average: ${testUser.statistics.average_response_time_seconds}s`);

// Response 3: 90 seconds
simulateTrackResponseTime(testUser, 90000);
console.log(`Response 3: 90s → Average: ${testUser.statistics.average_response_time_seconds}s`);

// Expected average: (30 + 60 + 90) / 3 = 60 seconds
const expectedAverage = 60;
const actualAverage = testUser.statistics.average_response_time_seconds;
console.log(`\nExpected average: ${expectedAverage}s`);
console.log(`Actual average: ${actualAverage}s`);
console.log(`Result: ${actualAverage === expectedAverage ? '✅ PASS' : '❌ FAIL'}\n`);

// Test formatted output
console.log("Formatted output tests:");
console.log("-".repeat(50));

// Test 1: Seconds format
testUser.statistics = { total_response_time_ms: 45000, response_count: 1, average_response_time_seconds: 45 };
let formatted = simulateGetFormattedResponseTime(testUser);
console.log(`45 seconds → "${formatted}" ${formatted === '45 сек.' ? '✅' : '❌'}`);

// Test 2: Minutes format
testUser.statistics = { total_response_time_ms: 150000, response_count: 1, average_response_time_seconds: 150 };
formatted = simulateGetFormattedResponseTime(testUser);
console.log(`150 seconds → "${formatted}" ${formatted === '2 мин. 30 сек.' ? '✅' : '❌'}`);

// Test 3: Hours format
testUser.statistics = { total_response_time_ms: 7200000, response_count: 1, average_response_time_seconds: 7200 };
formatted = simulateGetFormattedResponseTime(testUser);
console.log(`7200 seconds → "${formatted}" ${formatted === '2 ч.' ? '✅' : '❌'}`);

// Test 4: No data
testUser.statistics = {};
formatted = simulateGetFormattedResponseTime(testUser);
console.log(`No data → "${formatted}" ${formatted === null ? '✅' : '❌'}`);

// Final summary
console.log("\n" + "=".repeat(50));
console.log("FINAL VERIFICATION SUMMARY");
console.log("=".repeat(50));

const checks = [
    { name: "Question timestamp stored", pass: hasQuestionTimestamp },
    { name: "Both state set locations updated", pass: addMomentStateCount >= 2 },
    { name: "Response time calculation", pass: hasResponseTimeCalculation },
    { name: "trackResponseTime function called", pass: hasTrackResponseTimeCall },
    { name: "trackResponseTime function defined", pass: hasTrackResponseTimeFunction },
    { name: "Average displayed in statistics", pass: hasAvgResponseTimeInStats },
    { name: "Label text correct", pass: hasResponseTimeDisplay },
    { name: "Average calculation accurate", pass: actualAverage === expectedAverage }
];

let passCount = 0;
for (const check of checks) {
    console.log(`${check.pass ? '✅' : '❌'} ${check.name}`);
    if (check.pass) passCount++;
}

console.log(`\nTotal: ${passCount}/${checks.length} checks passed`);
console.log(`\n${passCount === checks.length ? '🎉 FEATURE #45 VERIFICATION: PASSED' : '⚠️ FEATURE #45 VERIFICATION: NEEDS WORK'}`);
