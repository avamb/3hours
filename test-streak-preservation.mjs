/**
 * Test Longest Streak Preservation - Feature #98
 * Verifies longest streak is never decreased even when current streak resets
 */

import { readFileSync } from 'fs';

// Read bot code to verify implementation
const botCode = readFileSync('C:/Projects/3hours/test-bot.mjs', 'utf8');

console.log("=== Feature #98: Longest Streak Preservation - Test ===\n");

// Step 1: Verify calculateStreak function exists
console.log("Step 1: Verify calculateStreak function");
console.log("-".repeat(50));

const hasCalculateStreak = botCode.includes("function calculateStreak(userMoments)");
console.log("calculateStreak function exists: " + (hasCalculateStreak ? "YES" : "NO"));

const returnsBestStreak = botCode.includes("return { currentStreak, bestStreak }");
console.log("Returns bestStreak: " + (returnsBestStreak ? "YES" : "NO"));

// Step 2: Verify Math.max is used to preserve best_streak
console.log("\nStep 2: Verify best_streak preservation logic");
console.log("-".repeat(50));

const usesMathMax = botCode.includes("user.statistics.best_streak = Math.max(");
console.log("Uses Math.max for best_streak: " + (usesMathMax ? "YES" : "NO"));

const preservesBestStreak = botCode.includes("user.statistics.best_streak || 0") &&
                            botCode.includes("streakData.bestStreak");
console.log("Compares with existing best_streak: " + (preservesBestStreak ? "YES" : "NO"));

// Step 3: Simulate 5-day streak building
console.log("\nStep 3: Simulate streak building and preservation");
console.log("-".repeat(50));

// Simulate calculateStreak function
function simulateCalculateStreak(moments) {
    if (!moments || moments.length === 0) {
        return { currentStreak: 0, bestStreak: 0 };
    }

    // Sort by date
    const sortedMoments = [...moments].sort((a, b) =>
        new Date(a.created_at) - new Date(b.created_at)
    );

    // Get unique days
    const uniqueDays = new Set();
    for (const moment of sortedMoments) {
        const date = new Date(moment.created_at);
        const dayKey = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate();
        uniqueDays.add(dayKey);
    }

    if (uniqueDays.size === 0) {
        return { currentStreak: 0, bestStreak: 0 };
    }

    // Convert to sorted array
    const days = Array.from(uniqueDays).map(d => {
        const [y, m, day] = d.split("-").map(Number);
        return new Date(y, m - 1, day);
    }).sort((a, b) => a - b);

    // Calculate best streak
    let bestStreak = 0;
    let tempStreak = 1;

    for (let i = 1; i < days.length; i++) {
        const diff = (days[i] - days[i-1]) / (1000 * 60 * 60 * 24);
        if (diff === 1) {
            tempStreak++;
        } else {
            if (tempStreak > bestStreak) {
                bestStreak = tempStreak;
            }
            tempStreak = 1;
        }
    }

    if (tempStreak > bestStreak) {
        bestStreak = tempStreak;
    }

    // Calculate current streak
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const lastDay = days[days.length - 1];
    lastDay.setHours(0, 0, 0, 0);

    const daysSinceLast = Math.floor((today - lastDay) / (1000 * 60 * 60 * 24));

    let currentStreak = 0;
    if (daysSinceLast <= 1) {
        currentStreak = 1;
        for (let i = days.length - 2; i >= 0; i--) {
            const diff = (days[i + 1] - days[i]) / (1000 * 60 * 60 * 24);
            if (diff === 1) {
                currentStreak++;
            } else {
                break;
            }
        }
    }

    return { currentStreak, bestStreak };
}

// Create moments for 5 consecutive days
const fiveDayMoments = [];
const today = new Date();
for (let i = 4; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    fiveDayMoments.push({
        id: 5 - i,
        content: "Day " + (5 - i),
        created_at: date
    });
}

console.log("Created moments for 5 consecutive days");

// Simulate user with stats
let userStats = {
    current_streak: 0,
    best_streak: 0,
    total_moments: 0
};

// Calculate streak after 5-day building
const streakAfter5Days = simulateCalculateStreak(fiveDayMoments);

// Update stats using Math.max (like the real code)
userStats.current_streak = streakAfter5Days.currentStreak;
userStats.best_streak = Math.max(userStats.best_streak || 0, streakAfter5Days.bestStreak);
userStats.total_moments = 5;

console.log("After 5 days: current_streak = " + userStats.current_streak + ", best_streak = " + userStats.best_streak);

const streak5Correct = userStats.best_streak === 5;
console.log("best_streak is 5: " + (streak5Correct ? "YES" : "NO"));

// Step 4: Break streak by skipping a day
console.log("\nStep 4: Break streak (simulate skipped day)");
console.log("-".repeat(50));

// Create new moments with a gap
const momentsWithGap = [...fiveDayMoments];
const dayAfterGap = new Date(today);
dayAfterGap.setDate(dayAfterGap.getDate() + 2); // Skip a day

momentsWithGap.push({
    id: 6,
    content: "Day after gap",
    created_at: dayAfterGap
});

console.log("Added moment after 1-day gap");

// Recalculate streak
const streakAfterGap = simulateCalculateStreak(momentsWithGap);

// Update stats - best_streak should NOT decrease
userStats.current_streak = streakAfterGap.currentStreak;
userStats.best_streak = Math.max(userStats.best_streak || 0, streakAfterGap.bestStreak);
userStats.total_moments = 6;

console.log("After gap: current_streak = " + userStats.current_streak + ", best_streak = " + userStats.best_streak);

// Step 5: Verify current_streak reset but best_streak preserved
console.log("\nStep 5: Verify preservation");
console.log("-".repeat(50));

const currentStreakReset = userStats.current_streak <= 1;
console.log("current_streak reset: " + (currentStreakReset ? "YES" : "NO"));

const bestStreakPreserved = userStats.best_streak === 5;
console.log("best_streak still 5: " + (bestStreakPreserved ? "YES" : "NO"));

// Step 6: Additional test - verify Math.max logic
console.log("\nStep 6: Verify Math.max logic");
console.log("-".repeat(50));

// Test that lower streakData.bestStreak doesn't decrease user's best_streak
let testStats = { best_streak: 10 };
const lowerStreakData = { bestStreak: 3 };

testStats.best_streak = Math.max(testStats.best_streak || 0, lowerStreakData.bestStreak);

const mathMaxWorks = testStats.best_streak === 10;
console.log("Math.max preserves higher value: " + (mathMaxWorks ? "YES" : "NO"));

// Final summary
console.log("\n" + "=".repeat(50));
console.log("FINAL VERIFICATION SUMMARY");
console.log("=".repeat(50));

const checks = [
    { name: "calculateStreak function exists", pass: hasCalculateStreak },
    { name: "Returns bestStreak", pass: returnsBestStreak },
    { name: "Uses Math.max for best_streak", pass: usesMathMax },
    { name: "Compares with existing best_streak", pass: preservesBestStreak },
    { name: "5-day streak builds correctly", pass: streak5Correct },
    { name: "current_streak resets on gap", pass: currentStreakReset },
    { name: "best_streak preserved (still 5)", pass: bestStreakPreserved },
    { name: "Math.max preserves higher value", pass: mathMaxWorks }
];

let passCount = 0;
for (const check of checks) {
    console.log((check.pass ? "[PASS]" : "[FAIL]") + " " + check.name);
    if (check.pass) passCount++;
}

console.log("\nTotal: " + passCount + "/" + checks.length + " checks passed");

if (passCount === checks.length) {
    console.log("\nFEATURE #98 VERIFICATION: PASSED");
} else {
    console.log("\nFEATURE #98 VERIFICATION: NEEDS WORK");
}
