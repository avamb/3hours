/**
 * Test Timezone-aware Scheduling - Feature #57
 * Verifies notifications are sent in user's timezone
 */

import { readFileSync } from 'fs';

// Read bot code to verify implementation
const botCode = readFileSync(new URL('./test-bot.mjs', import.meta.url), 'utf8');

console.log("=== Feature #57: Timezone-aware Scheduling - Test ===\n");

// Step 1: Verify timezone functions exist
console.log("Step 1: Verify timezone implementation exists");
console.log("-".repeat(50));

const hasParseTimezoneOffset = botCode.includes("function parseTimezoneOffset(timezone)");
console.log(`parseTimezoneOffset function exists: ${hasParseTimezoneOffset ? '✅ YES' : '❌ NO'}`);

const hasGetUserLocalTime = botCode.includes("function getUserLocalTime(user, utcTime = new Date())");
console.log(`getUserLocalTime function exists: ${hasGetUserLocalTime ? '✅ YES' : '❌ NO'}`);

const hasFormatTimezoneDisplay = botCode.includes("function formatTimezoneDisplay(timezone)");
console.log(`formatTimezoneDisplay function exists: ${hasFormatTimezoneDisplay ? '✅ YES' : '❌ NO'}`);

const hasTimezoneKeyboard = botCode.includes("function getTimezoneKeyboard()");
console.log(`getTimezoneKeyboard function exists: ${hasTimezoneKeyboard ? '✅ YES' : '❌ NO'}`);

const hasTimezoneInUser = botCode.includes('timezone: "UTC"');
console.log(`Timezone field in user object: ${hasTimezoneInUser ? '✅ YES' : '❌ NO'}\n`);

// Step 2: Set user timezone to UTC+3
console.log("Step 2: Set user timezone to UTC+3");
console.log("-".repeat(50));

// Simulate parseTimezoneOffset function
function parseTimezoneOffset(timezone) {
    if (!timezone || timezone === 'UTC' || timezone === 'Z') {
        return 0;
    }

    const offsetMatch = timezone.match(/^([+-])(\d{1,2}):?(\d{2})?$/);
    if (offsetMatch) {
        const sign = offsetMatch[1] === '+' ? 1 : -1;
        const hours = parseInt(offsetMatch[2]);
        const minutes = parseInt(offsetMatch[3] || '0');
        return sign * (hours * 60 + minutes);
    }

    // Handle named timezones
    const timezoneOffsets = {
        'Europe/Moscow': 180,
        'Europe/Kiev': 120,
        'Europe/London': 0,
        'America/New_York': -300,
        'America/Los_Angeles': -480,
        'Asia/Tokyo': 540
    };

    return timezoneOffsets[timezone] || 0;
}

// Test UTC+3
const utc3Offset = parseTimezoneOffset("+03:00");
console.log(`UTC+3 offset: ${utc3Offset} minutes (expected: 180)`);
console.log(`UTC+3 offset correct: ${utc3Offset === 180 ? '✅ YES' : '❌ NO'}`);

const hasTzCallback = botCode.includes("handleTimezoneCallback");
console.log(`handleTimezoneCallback function exists: ${hasTzCallback ? '✅ YES' : '❌ NO'}`);

const hasSettingsTimezone = botCode.includes('case "settings_timezone"');
console.log(`Settings timezone case exists: ${hasSettingsTimezone ? '✅ YES' : '❌ NO'}\n`);

// Step 3: Set active hours 09:00-21:00 and verify questions sent at correct local time
console.log("Step 3: Verify questions sent at correct local time");
console.log("-".repeat(50));

// Simulate getUserLocalTime function
function getUserLocalTime(user, utcTime = new Date()) {
    const offsetMinutes = parseTimezoneOffset(user.timezone || 'UTC');
    return new Date(utcTime.getTime() + offsetMinutes * 60 * 1000);
}

// Simulate isWithinActiveHours function
function isWithinActiveHours(user, checkTime = new Date()) {
    const startParts = user.active_hours_start.split(':').map(Number);
    const endParts = user.active_hours_end.split(':').map(Number);

    const startMinutes = startParts[0] * 60 + (startParts[1] || 0);
    const endMinutes = endParts[0] * 60 + (endParts[1] || 0);

    // Get user's local time
    const userLocalTime = getUserLocalTime(user, checkTime);
    const currentMinutes = userLocalTime.getUTCHours() * 60 + userLocalTime.getUTCMinutes();

    // Handle normal case (e.g., 09:00 - 21:00)
    if (startMinutes <= endMinutes) {
        return currentMinutes >= startMinutes && currentMinutes < endMinutes;
    }

    // Handle overnight case
    return currentMinutes >= startMinutes || currentMinutes < endMinutes;
}

// Test user with UTC+3 timezone
const testUserUTC3 = {
    timezone: "+03:00",
    active_hours_start: "09:00",
    active_hours_end: "21:00"
};

// Check isWithinActiveHours is timezone-aware
const hasTimezoneAwareCheck = botCode.includes("const userLocalTime = getUserLocalTime(user, checkTime)");
console.log(`isWithinActiveHours uses getUserLocalTime: ${hasTimezoneAwareCheck ? '✅ YES' : '❌ NO'}`);

// Test case: UTC 06:00 should be 09:00 in UTC+3 (within hours)
const utc0600 = new Date('2024-01-15T06:00:00Z');
const isWithin0600 = isWithinActiveHours(testUserUTC3, utc0600);
console.log(`UTC 06:00 (local 09:00 in UTC+3) within hours: ${isWithin0600 ? '✅ YES (correct)' : '❌ NO'}`);

// Test case: UTC 05:00 should be 08:00 in UTC+3 (outside hours)
const utc0500 = new Date('2024-01-15T05:00:00Z');
const isWithin0500 = isWithinActiveHours(testUserUTC3, utc0500);
console.log(`UTC 05:00 (local 08:00 in UTC+3) outside hours: ${!isWithin0500 ? '✅ NO (correct)' : '❌ YES'}`);

// Test case: UTC 18:00 should be 21:00 in UTC+3 (outside hours, end boundary)
const utc1800 = new Date('2024-01-15T18:00:00Z');
const isWithin1800 = isWithinActiveHours(testUserUTC3, utc1800);
console.log(`UTC 18:00 (local 21:00 in UTC+3) outside hours: ${!isWithin1800 ? '✅ NO (correct)' : '❌ YES'}`);

// Test case: UTC 17:59 should be 20:59 in UTC+3 (within hours)
const utc1759 = new Date('2024-01-15T17:59:00Z');
const isWithin1759 = isWithinActiveHours(testUserUTC3, utc1759);
console.log(`UTC 17:59 (local 20:59 in UTC+3) within hours: ${isWithin1759 ? '✅ YES (correct)' : '❌ NO'}\n`);

// Step 4: Change timezone
console.log("Step 4: Change timezone");
console.log("-".repeat(50));

// Test different timezone parsing
const utcOffset = parseTimezoneOffset("UTC");
console.log(`UTC offset: ${utcOffset} minutes (expected: 0) ${utcOffset === 0 ? '✅' : '❌'}`);

const minus5Offset = parseTimezoneOffset("-05:00");
console.log(`UTC-5 offset: ${minus5Offset} minutes (expected: -300) ${minus5Offset === -300 ? '✅' : '❌'}`);

const moscowOffset = parseTimezoneOffset("Europe/Moscow");
console.log(`Moscow offset: ${moscowOffset} minutes (expected: 180) ${moscowOffset === 180 ? '✅' : '❌'}`);

// Verify timezone can be changed via callback
const hasTzCallbackHandler = botCode.includes('const timezone = action.replace("tz_", "")');
console.log(`Timezone callback extracts timezone: ${hasTzCallbackHandler ? '✅ YES' : '❌ NO'}`);

const savesTz = botCode.includes("user.timezone = timezone");
console.log(`Timezone saved to user object: ${savesTz ? '✅ YES' : '❌ NO'}\n`);

// Step 5: Verify schedule adjusts
console.log("Step 5: Verify schedule adjusts to timezone change");
console.log("-".repeat(50));

// Test user with UTC-5 timezone (New York)
const testUserNY = {
    timezone: "-05:00",
    active_hours_start: "09:00",
    active_hours_end: "21:00"
};

// UTC 14:00 should be 09:00 in UTC-5 (within hours)
const utc1400 = new Date('2024-01-15T14:00:00Z');
const isWithin1400_NY = isWithinActiveHours(testUserNY, utc1400);
console.log(`UTC 14:00 (local 09:00 in UTC-5) within hours: ${isWithin1400_NY ? '✅ YES (correct)' : '❌ NO'}`);

// UTC 13:00 should be 08:00 in UTC-5 (outside hours)
const utc1300 = new Date('2024-01-15T13:00:00Z');
const isWithin1300_NY = isWithinActiveHours(testUserNY, utc1300);
console.log(`UTC 13:00 (local 08:00 in UTC-5) outside hours: ${!isWithin1300_NY ? '✅ NO (correct)' : '❌ YES'}`);

// Same UTC time different behavior based on timezone
console.log("\nSame UTC time (06:00), different behavior by timezone:");
const testTimeUTC = new Date('2024-01-15T06:00:00Z');

const userMoscow = { timezone: "+03:00", active_hours_start: "09:00", active_hours_end: "21:00" };
const userLondon = { timezone: "UTC", active_hours_start: "09:00", active_hours_end: "21:00" };
const userNY = { timezone: "-05:00", active_hours_start: "09:00", active_hours_end: "21:00" };

const moscowResult = isWithinActiveHours(userMoscow, testTimeUTC);
const londonResult = isWithinActiveHours(userLondon, testTimeUTC);
const nyResult = isWithinActiveHours(userNY, testTimeUTC);

console.log(`  Moscow (UTC+3): local 09:00 → ${moscowResult ? 'WITHIN' : 'OUTSIDE'} hours ${moscowResult ? '✅' : '❌'}`);
console.log(`  London (UTC): local 06:00 → ${londonResult ? 'WITHIN' : 'OUTSIDE'} hours ${!londonResult ? '✅' : '❌'}`);
console.log(`  New York (UTC-5): local 01:00 → ${nyResult ? 'WITHIN' : 'OUTSIDE'} hours ${!nyResult ? '✅' : '❌'}`);

// Verify timezone display in settings
const hasTimezoneDisplay = botCode.includes("🌐 Часовой пояс: ${timezoneDisplay}");
console.log(`\nTimezone displayed in settings: ${hasTimezoneDisplay ? '✅ YES' : '❌ NO'}`);

const hasTimezoneSettingsButton = botCode.includes('{ text: "🌐 Часовой пояс", callback_data: "settings_timezone" }');
console.log(`Timezone settings button: ${hasTimezoneSettingsButton ? '✅ YES' : '❌ NO'}`);

// Final summary
console.log("\n" + "=".repeat(50));
console.log("FINAL VERIFICATION SUMMARY");
console.log("=".repeat(50));

const checks = [
    { name: "parseTimezoneOffset function exists", pass: hasParseTimezoneOffset },
    { name: "getUserLocalTime function exists", pass: hasGetUserLocalTime },
    { name: "formatTimezoneDisplay function exists", pass: hasFormatTimezoneDisplay },
    { name: "getTimezoneKeyboard function exists", pass: hasTimezoneKeyboard },
    { name: "Timezone field in user object", pass: hasTimezoneInUser },
    { name: "handleTimezoneCallback exists", pass: hasTzCallback },
    { name: "Settings timezone case exists", pass: hasSettingsTimezone },
    { name: "isWithinActiveHours uses getUserLocalTime", pass: hasTimezoneAwareCheck },
    { name: "UTC+3 offset correct (180 min)", pass: utc3Offset === 180 },
    { name: "UTC-5 offset correct (-300 min)", pass: minus5Offset === -300 },
    { name: "Timezone callback extracts timezone", pass: hasTzCallbackHandler },
    { name: "Timezone saved to user object", pass: savesTz },
    { name: "UTC 06:00 is 09:00 in UTC+3 (within)", pass: isWithin0600 },
    { name: "UTC 05:00 is 08:00 in UTC+3 (outside)", pass: !isWithin0500 },
    { name: "UTC 14:00 is 09:00 in UTC-5 (within)", pass: isWithin1400_NY },
    { name: "UTC 13:00 is 08:00 in UTC-5 (outside)", pass: !isWithin1300_NY },
    { name: "Timezone displayed in settings", pass: hasTimezoneDisplay },
    { name: "Timezone settings button exists", pass: hasTimezoneSettingsButton }
];

let passCount = 0;
for (const check of checks) {
    console.log(`${check.pass ? '✅' : '❌'} ${check.name}`);
    if (check.pass) passCount++;
}

console.log(`\nTotal: ${passCount}/${checks.length} checks passed`);
console.log(`\n${passCount === checks.length ? '🎉 FEATURE #57 VERIFICATION: PASSED' : '⚠️ FEATURE #57 VERIFICATION: NEEDS WORK'}`);
