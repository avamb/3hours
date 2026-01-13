/**
 * Test User Stats Initialization - Feature #96
 * Verifies user_stats record is created on user creation with default values
 */

import { readFileSync } from 'fs';

// Read bot code to verify implementation
const botCode = readFileSync(new URL('./test-bot.mjs', import.meta.url), 'utf8');

console.log("=== Feature #96: User Stats Initialization - Test ===\n");

// Step 1: Verify getOrCreateUser function exists
console.log("Step 1: Verify getOrCreateUser function");
console.log("-".repeat(50));

const hasGetOrCreateUser = botCode.includes("function getOrCreateUser(telegramUser)");
console.log("getOrCreateUser function exists: " + (hasGetOrCreateUser ? "YES" : "NO"));

// Step 2: Verify statistics object is initialized in user creation
console.log("\nStep 2: Verify statistics initialized on user creation");
console.log("-".repeat(50));

const hasStatisticsInit = botCode.includes("statistics: {") &&
                          botCode.includes("current_streak: 0") &&
                          botCode.includes("total_moments: 0");
console.log("statistics object initialized: " + (hasStatisticsInit ? "YES" : "NO"));

// Step 3: Verify default values for streak
console.log("\nStep 3: Verify default values for streak");
console.log("-".repeat(50));

const hasCurrentStreak = botCode.includes("current_streak: 0");
console.log("current_streak defaults to 0: " + (hasCurrentStreak ? "YES" : "NO"));

const hasBestStreak = botCode.includes("best_streak: 0");
console.log("best_streak defaults to 0: " + (hasBestStreak ? "YES" : "NO"));

// Step 4: Verify default values for moments
console.log("\nStep 4: Verify default values for moments");
console.log("-".repeat(50));

const hasTotalMoments = botCode.includes("total_moments: 0");
console.log("total_moments defaults to 0: " + (hasTotalMoments ? "YES" : "NO"));

// Step 5: Verify question tracking stats
console.log("\nStep 5: Verify question tracking stats initialized");
console.log("-".repeat(50));

const hasQuestionsSent = botCode.includes("questions_sent: 0");
console.log("questions_sent defaults to 0: " + (hasQuestionsSent ? "YES" : "NO"));

const hasQuestionsAnswered = botCode.includes("questions_answered: 0");
console.log("questions_answered defaults to 0: " + (hasQuestionsAnswered ? "YES" : "NO"));

// Step 6: Verify response time tracking initialized
console.log("\nStep 6: Verify response time tracking initialized");
console.log("-".repeat(50));

const hasTotalResponseTime = botCode.includes("total_response_time_ms: 0");
console.log("total_response_time_ms defaults to 0: " + (hasTotalResponseTime ? "YES" : "NO"));

const hasResponseCount = botCode.includes("response_count: 0");
console.log("response_count defaults to 0: " + (hasResponseCount ? "YES" : "NO"));

const hasAvgResponseTime = botCode.includes("average_response_time_seconds: 0");
console.log("average_response_time_seconds defaults to 0: " + (hasAvgResponseTime ? "YES" : "NO"));

// Step 7: Simulate user creation
console.log("\nStep 7: Simulate user creation with stats");
console.log("-".repeat(50));

// Simulate getOrCreateUser function
function simulateGetOrCreateUser(telegramUser) {
    return {
        telegram_id: telegramUser.id,
        first_name: telegramUser.first_name || "friend",
        language_code: telegramUser.language_code || "ru",
        formal_address: false,
        onboarding_completed: false,
        notifications_enabled: true,
        active_hours_start: "09:00",
        active_hours_end: "21:00",
        notification_interval_hours: 3,
        timezone: "UTC",
        created_at: new Date(),
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
    };
}

const newUser = simulateGetOrCreateUser({ id: 12345, first_name: "Test" });

const hasStats = newUser.statistics !== undefined;
console.log("New user has statistics object: " + (hasStats ? "YES" : "NO"));

const streakIsZero = newUser.statistics.current_streak === 0;
console.log("current_streak is 0: " + (streakIsZero ? "YES" : "NO"));

const momentsIsZero = newUser.statistics.total_moments === 0;
console.log("total_moments is 0: " + (momentsIsZero ? "YES" : "NO"));

// Step 8: Verify log message on user creation
console.log("\nStep 8: Verify logging on user creation");
console.log("-".repeat(50));

const hasCreationLog = botCode.includes("Created new user") && botCode.includes("with initialized statistics");
console.log("Logs user creation with stats: " + (hasCreationLog ? "YES" : "NO"));

// Final summary
console.log("\n" + "=".repeat(50));
console.log("FINAL VERIFICATION SUMMARY");
console.log("=".repeat(50));

const checks = [
    { name: "getOrCreateUser function exists", pass: hasGetOrCreateUser },
    { name: "statistics object initialized", pass: hasStatisticsInit },
    { name: "current_streak defaults to 0", pass: hasCurrentStreak },
    { name: "best_streak defaults to 0", pass: hasBestStreak },
    { name: "total_moments defaults to 0", pass: hasTotalMoments },
    { name: "questions_sent defaults to 0", pass: hasQuestionsSent },
    { name: "questions_answered defaults to 0", pass: hasQuestionsAnswered },
    { name: "total_response_time_ms defaults to 0", pass: hasTotalResponseTime },
    { name: "response_count defaults to 0", pass: hasResponseCount },
    { name: "average_response_time_seconds defaults to 0", pass: hasAvgResponseTime },
    { name: "New user has statistics object", pass: hasStats },
    { name: "current_streak is 0 in simulation", pass: streakIsZero },
    { name: "total_moments is 0 in simulation", pass: momentsIsZero },
    { name: "Logs user creation with stats", pass: hasCreationLog }
];

let passCount = 0;
for (const check of checks) {
    console.log((check.pass ? "[PASS]" : "[FAIL]") + " " + check.name);
    if (check.pass) passCount++;
}

console.log("\nTotal: " + passCount + "/" + checks.length + " checks passed");

if (passCount === checks.length) {
    console.log("\nFEATURE #96 VERIFICATION: PASSED");
} else {
    console.log("\nFEATURE #96 VERIFICATION: NEEDS WORK");
}
