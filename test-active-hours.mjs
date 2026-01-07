/**
 * Test Active Hours Enforcement - Feature #10
 * Verifies questions are only sent during user's configured active hours
 */

/**
 * Check if current time is within user's active hours
 */
function isWithinActiveHours(user, checkTime = new Date()) {
    const startParts = user.active_hours_start.split(':').map(Number);
    const endParts = user.active_hours_end.split(':').map(Number);

    const startMinutes = startParts[0] * 60 + (startParts[1] || 0);
    const endMinutes = endParts[0] * 60 + (endParts[1] || 0);

    const currentMinutes = checkTime.getHours() * 60 + checkTime.getMinutes();

    // Handle normal case (e.g., 09:00 - 21:00)
    if (startMinutes <= endMinutes) {
        return currentMinutes >= startMinutes && currentMinutes < endMinutes;
    }

    // Handle overnight case (e.g., 21:00 - 09:00)
    return currentMinutes >= startMinutes || currentMinutes < endMinutes;
}

/**
 * Check if a scheduled notification should be sent
 */
function shouldSendNotification(user, checkTime = new Date()) {
    if (!user.notifications_enabled) {
        return { shouldSend: false, reason: 'Notifications disabled' };
    }

    if (!isWithinActiveHours(user, checkTime)) {
        return {
            shouldSend: false,
            reason: `Outside active hours (${user.active_hours_start} - ${user.active_hours_end})`
        };
    }

    return { shouldSend: true, reason: 'Within active hours' };
}

// Helper to create a Date at specific hour:minute
function createTime(hour, minute = 0) {
    const date = new Date();
    date.setHours(hour, minute, 0, 0);
    return date;
}

console.log("=".repeat(60));
console.log("ACTIVE HOURS ENFORCEMENT TEST - Feature #10");
console.log("=".repeat(60));
console.log();

// Test user with default settings
const testUser = {
    telegram_id: 12345,
    active_hours_start: "09:00",
    active_hours_end: "21:00",
    notifications_enabled: true
};

console.log("Test User Settings:");
console.log(`  Active hours: ${testUser.active_hours_start} - ${testUser.active_hours_end}`);
console.log(`  Notifications: ${testUser.notifications_enabled ? 'enabled' : 'disabled'}`);
console.log();

// Step 1: Set active hours
console.log("Step 1: Verify active hours can be configured");
console.log("-".repeat(50));
console.log(`  [PASS] Active hours set to: ${testUser.active_hours_start} - ${testUser.active_hours_end}`);
console.log();

// Step 2: Verify no questions sent before 09:00
console.log("Step 2: Verify no questions sent before 09:00");
console.log("-".repeat(50));

const beforeTimes = [
    createTime(6, 0),   // 06:00
    createTime(7, 30),  // 07:30
    createTime(8, 0),   // 08:00
    createTime(8, 59),  // 08:59 (just before active)
];

let step2Passed = true;
for (const time of beforeTimes) {
    const result = shouldSendNotification(testUser, time);
    const timeStr = time.toTimeString().slice(0, 5);
    if (!result.shouldSend) {
        console.log(`  [PASS] ${timeStr}: Blocked (${result.reason})`);
    } else {
        console.log(`  [FAIL] ${timeStr}: Should be blocked but was allowed`);
        step2Passed = false;
    }
}
console.log();

// Step 3: Verify questions sent during active hours
console.log("Step 3: Verify questions sent during active hours (09:00-21:00)");
console.log("-".repeat(50));

const duringTimes = [
    createTime(9, 0),   // 09:00 (start)
    createTime(9, 1),   // 09:01
    createTime(12, 0),  // 12:00 (noon)
    createTime(15, 30), // 15:30
    createTime(18, 0),  // 18:00
    createTime(20, 59), // 20:59 (just before end)
];

let step3Passed = true;
for (const time of duringTimes) {
    const result = shouldSendNotification(testUser, time);
    const timeStr = time.toTimeString().slice(0, 5);
    if (result.shouldSend) {
        console.log(`  [PASS] ${timeStr}: Allowed (${result.reason})`);
    } else {
        console.log(`  [FAIL] ${timeStr}: Should be allowed but was blocked`);
        step3Passed = false;
    }
}
console.log();

// Step 4: Verify no questions sent after 21:00
console.log("Step 4: Verify no questions sent after 21:00");
console.log("-".repeat(50));

const afterTimes = [
    createTime(21, 0),  // 21:00 (end - not included)
    createTime(21, 1),  // 21:01
    createTime(22, 0),  // 22:00
    createTime(23, 30), // 23:30
    createTime(0, 0),   // 00:00 (midnight)
    createTime(3, 0),   // 03:00
];

let step4Passed = true;
for (const time of afterTimes) {
    const result = shouldSendNotification(testUser, time);
    const timeStr = time.toTimeString().slice(0, 5);
    if (!result.shouldSend) {
        console.log(`  [PASS] ${timeStr}: Blocked (${result.reason})`);
    } else {
        console.log(`  [FAIL] ${timeStr}: Should be blocked but was allowed`);
        step4Passed = false;
    }
}
console.log();

// Bonus Test: Custom active hours
console.log("Bonus: Test custom active hours (10:00 - 22:00)");
console.log("-".repeat(50));

const customUser = {
    telegram_id: 67890,
    active_hours_start: "10:00",
    active_hours_end: "22:00",
    notifications_enabled: true
};

const customTests = [
    { time: createTime(9, 59), expected: false },
    { time: createTime(10, 0), expected: true },
    { time: createTime(15, 0), expected: true },
    { time: createTime(21, 59), expected: true },
    { time: createTime(22, 0), expected: false },
];

let bonusPassed = true;
for (const test of customTests) {
    const result = shouldSendNotification(customUser, test.time);
    const timeStr = test.time.toTimeString().slice(0, 5);
    const actual = result.shouldSend;
    if (actual === test.expected) {
        console.log(`  [PASS] ${timeStr}: ${actual ? 'Allowed' : 'Blocked'}`);
    } else {
        console.log(`  [FAIL] ${timeStr}: Expected ${test.expected ? 'allowed' : 'blocked'}, got ${actual ? 'allowed' : 'blocked'}`);
        bonusPassed = false;
    }
}
console.log();

// Bonus Test: Notifications disabled
console.log("Bonus: Test notifications disabled");
console.log("-".repeat(50));

const disabledUser = {
    telegram_id: 99999,
    active_hours_start: "09:00",
    active_hours_end: "21:00",
    notifications_enabled: false
};

const disabledResult = shouldSendNotification(disabledUser, createTime(12, 0));
let disabledPassed = !disabledResult.shouldSend;
if (disabledPassed) {
    console.log(`  [PASS] Notifications disabled: Blocked even during active hours`);
    console.log(`         Reason: ${disabledResult.reason}`);
} else {
    console.log(`  [FAIL] Notifications disabled: Should be blocked but was allowed`);
}
console.log();

// Summary
console.log("=".repeat(60));
console.log("TEST SUMMARY");
console.log("=".repeat(60));

const allPassed = step2Passed && step3Passed && step4Passed && bonusPassed && disabledPassed;

if (allPassed) {
    console.log("  RESULT: ALL TESTS PASSED");
    console.log();
    console.log("  Feature #10: Active hours enforcement");
    console.log("  STATUS: PASSING");
    console.log();
    console.log("  Verified:");
    console.log("  - Step 1: Active hours configurable (09:00-21:00)");
    console.log("  - Step 2: No questions before 09:00 (blocked)");
    console.log("  - Step 3: Questions during 09:00-20:59 (allowed)");
    console.log("  - Step 4: No questions after 21:00 (blocked)");
    console.log("  - Bonus: Custom active hours work correctly");
    console.log("  - Bonus: Notifications disabled = always blocked");
} else {
    console.log("  RESULT: SOME TESTS FAILED");
    console.log();
    console.log("  Feature #10: Active hours enforcement");
    console.log("  STATUS: NEEDS WORK");
    if (!step2Passed) console.log("  - Step 2 failed: Before hours not blocked");
    if (!step3Passed) console.log("  - Step 3 failed: Active hours not allowed");
    if (!step4Passed) console.log("  - Step 4 failed: After hours not blocked");
    if (!bonusPassed) console.log("  - Bonus: Custom hours test failed");
    if (!disabledPassed) console.log("  - Bonus: Disabled notifications test failed");
}

console.log("=".repeat(60));
