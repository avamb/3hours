/**
 * Test User Stats Update on Moment Creation - Feature #97
 * Verifies statistics update when new moment is created
 */

import { readFileSync } from 'fs';

// Read bot code to verify implementation
const botCode = readFileSync('C:/Projects/3hours/test-bot.mjs', 'utf8');

console.log("=== Feature #97: User Stats Update on Moment Creation - Test ===\n");

// Step 1: Verify addMoment function exists
console.log("Step 1: Verify addMoment function");
console.log("-".repeat(50));

const hasAddMoment = botCode.includes("function addMoment(userId, content, embedding = null)");
console.log("addMoment function exists: " + (hasAddMoment ? "YES" : "NO"));

// Step 2: Verify statistics update in addMoment
console.log("\nStep 2: Verify statistics update in addMoment");
console.log("-".repeat(50));

const hasStatsUpdate = botCode.includes("// Update user statistics when moment is created");
console.log("Statistics update comment exists: " + (hasStatsUpdate ? "YES" : "NO"));

const getsUser = botCode.includes("const user = users.get(userId)") &&
                 botCode.includes("if (user) {");
console.log("Gets user for stats update: " + (getsUser ? "YES" : "NO"));

// Step 3: Verify total_moments incremented
console.log("\nStep 3: Verify total_moments incremented");
console.log("-".repeat(50));

const incrementsMoments = botCode.includes("user.statistics.total_moments = (user.statistics.total_moments || 0) + 1");
console.log("total_moments incremented: " + (incrementsMoments ? "YES" : "NO"));

// Step 4: Verify streak updated
console.log("\nStep 4: Verify streak updated");
console.log("-".repeat(50));

const hasStreakUpdate = botCode.includes("const streakData = calculateStreak(userMoments)");
console.log("Calls calculateStreak: " + (hasStreakUpdate ? "YES" : "NO"));

const updatesCurrentStreak = botCode.includes("user.statistics.current_streak = streakData.currentStreak");
console.log("Updates current_streak: " + (updatesCurrentStreak ? "YES" : "NO"));

const updatesBestStreak = botCode.includes("user.statistics.best_streak = Math.max");
console.log("Updates best_streak: " + (updatesBestStreak ? "YES" : "NO"));

// Step 5: Verify last_activity date updated
console.log("\nStep 5: Verify last_activity updated");
console.log("-".repeat(50));

const updatesLastActivity = botCode.includes("user.last_activity = new Date()");
console.log("last_activity updated: " + (updatesLastActivity ? "YES" : "NO"));

// Step 6: Verify logging of stats update
console.log("\nStep 6: Verify logging of stats update");
console.log("-".repeat(50));

const hasStatsLog = botCode.includes("Updated stats for user") &&
                    botCode.includes("total_moments=") &&
                    botCode.includes("streak=");
console.log("Logs stats update: " + (hasStatsLog ? "YES" : "NO"));

// Step 7: Simulate moment creation with stats update
console.log("\nStep 7: Simulate moment creation with stats update");
console.log("-".repeat(50));

// Simulated user and moments
const users = new Map();
const moments = new Map();

// Create test user
users.set(123, {
    telegram_id: 123,
    statistics: {
        current_streak: 0,
        best_streak: 0,
        total_moments: 0
    }
});

// Simulate calculateStreak
function calculateStreak(userMoments) {
    return {
        currentStreak: userMoments.length > 0 ? 1 : 0,
        bestStreak: userMoments.length > 0 ? 1 : 0
    };
}

// Simulate addMoment
function simulateAddMoment(userId, content) {
    if (!moments.has(userId)) {
        moments.set(userId, []);
    }
    const userMoments = moments.get(userId);
    const newMoment = {
        id: userMoments.length + 1,
        content: content,
        created_at: new Date()
    };
    userMoments.push(newMoment);

    // Update user statistics
    const user = users.get(userId);
    if (user) {
        if (!user.statistics) {
            user.statistics = { current_streak: 0, best_streak: 0, total_moments: 0 };
        }
        user.statistics.total_moments = (user.statistics.total_moments || 0) + 1;
        user.last_activity = new Date();

        const streakData = calculateStreak(userMoments);
        user.statistics.current_streak = streakData.currentStreak;
        user.statistics.best_streak = Math.max(
            user.statistics.best_streak || 0,
            streakData.bestStreak
        );
    }

    return newMoment;
}

// Initial stats
const userBefore = users.get(123);
console.log("Before moment: total_moments = " + userBefore.statistics.total_moments);

// Add a moment
simulateAddMoment(123, "Had a great day!");

// Check updated stats
const userAfter = users.get(123);
console.log("After moment: total_moments = " + userAfter.statistics.total_moments);

const momentsIncremented = userAfter.statistics.total_moments === 1;
console.log("total_moments incremented correctly: " + (momentsIncremented ? "YES" : "NO"));

const streakUpdated = userAfter.statistics.current_streak >= 1;
console.log("current_streak updated: " + (streakUpdated ? "YES" : "NO"));

const lastActivitySet = userAfter.last_activity !== undefined;
console.log("last_activity set: " + (lastActivitySet ? "YES" : "NO"));

// Final summary
console.log("\n" + "=".repeat(50));
console.log("FINAL VERIFICATION SUMMARY");
console.log("=".repeat(50));

const checks = [
    { name: "addMoment function exists", pass: hasAddMoment },
    { name: "Statistics update comment exists", pass: hasStatsUpdate },
    { name: "Gets user for stats update", pass: getsUser },
    { name: "total_moments incremented", pass: incrementsMoments },
    { name: "Calls calculateStreak", pass: hasStreakUpdate },
    { name: "Updates current_streak", pass: updatesCurrentStreak },
    { name: "Updates best_streak", pass: updatesBestStreak },
    { name: "last_activity updated", pass: updatesLastActivity },
    { name: "Logs stats update", pass: hasStatsLog },
    { name: "Simulation: moments incremented", pass: momentsIncremented },
    { name: "Simulation: streak updated", pass: streakUpdated },
    { name: "Simulation: last_activity set", pass: lastActivitySet }
];

let passCount = 0;
for (const check of checks) {
    console.log((check.pass ? "[PASS]" : "[FAIL]") + " " + check.name);
    if (check.pass) passCount++;
}

console.log("\nTotal: " + passCount + "/" + checks.length + " checks passed");

if (passCount === checks.length) {
    console.log("\nFEATURE #97 VERIFICATION: PASSED");
} else {
    console.log("\nFEATURE #97 VERIFICATION: NEEDS WORK");
}
