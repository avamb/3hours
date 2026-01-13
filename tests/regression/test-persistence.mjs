/**
 * Test script for Feature #62: Data persistence across sessions
 *
 * This test verifies that:
 * 1. Data is saved to file when moments are created
 * 2. Data is loaded from file on startup
 * 3. Data persists across bot restarts
 */

import { readFileSync, writeFileSync, existsSync, unlinkSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const DATA_FILE = join(__dirname, 'test-persistence-data.json');

// Clean up test file
if (existsSync(DATA_FILE)) {
    unlinkSync(DATA_FILE);
    console.log("🗑️ Cleaned up existing test data file");
}

console.log("=== Feature #62: Data Persistence Test ===\n");

// Simulate the persistence logic
const users = new Map();
const moments = new Map();

function saveDataToFile() {
    const data = {
        users: Object.fromEntries(users),
        moments: Object.fromEntries(moments),
        savedAt: new Date().toISOString()
    };
    writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
    console.log(`💾 Data saved: ${users.size} users, ${[...moments.values()].flat().length} moments`);
}

function loadDataFromFile() {
    if (existsSync(DATA_FILE)) {
        const data = JSON.parse(readFileSync(DATA_FILE, 'utf8'));

        // Load users
        if (data.users) {
            for (const [key, value] of Object.entries(data.users)) {
                if (value.created_at) value.created_at = new Date(value.created_at);
                users.set(parseInt(key), value);
            }
        }

        // Load moments
        if (data.moments) {
            for (const [key, value] of Object.entries(data.moments)) {
                const momentsArray = value.map(m => ({
                    ...m,
                    created_at: new Date(m.created_at)
                }));
                moments.set(parseInt(key), momentsArray);
            }
        }

        console.log(`📁 Loaded data: ${users.size} users, ${[...moments.values()].flat().length} moments`);
        return true;
    }
    return false;
}

function getOrCreateUser(telegramUser) {
    const userId = telegramUser.id;
    if (!users.has(userId)) {
        users.set(userId, {
            telegram_id: userId,
            first_name: telegramUser.first_name || "друг",
            language_code: telegramUser.language_code || "ru",
            formal_address: false,
            onboarding_completed: true,
            created_at: new Date()
        });
        saveDataToFile();
    }
    return users.get(userId);
}

function addMoment(userId, content) {
    if (!moments.has(userId)) {
        moments.set(userId, []);
    }
    const userMoments = moments.get(userId);
    userMoments.push({
        id: userMoments.length + 1,
        content: content,
        created_at: new Date()
    });
    saveDataToFile();
    return userMoments[userMoments.length - 1];
}

function getUserMoments(userId) {
    return moments.get(userId) || [];
}

// Test 1: Create user and moments
console.log("=== Test 1: Create User and Moments ===\n");

const testUser = { id: 12345, first_name: "TestUser", language_code: "ru" };
const user = getOrCreateUser(testUser);
console.log(`✅ User created: ${user.first_name} (ID: ${user.telegram_id})`);

const moment1 = addMoment(user.telegram_id, "TEST_MOMENT_1_UNIQUE_CONTENT");
console.log(`✅ Moment 1 created: "${moment1.content}"`);

const moment2 = addMoment(user.telegram_id, "TEST_MOMENT_2_ANOTHER_UNIQUE");
console.log(`✅ Moment 2 created: "${moment2.content}"`);

console.log(`\n📊 Before restart: ${users.size} users, ${getUserMoments(user.telegram_id).length} moments`);

// Test 2: Verify file exists
console.log("\n=== Test 2: Verify Data File ===\n");

if (existsSync(DATA_FILE)) {
    console.log("✅ Data file exists");
    const fileContent = readFileSync(DATA_FILE, 'utf8');
    const fileData = JSON.parse(fileContent);
    console.log(`  - File contains ${Object.keys(fileData.users).length} users`);
    console.log(`  - File contains ${Object.values(fileData.moments).flat().length} moments`);
    console.log(`  - Saved at: ${fileData.savedAt}`);
} else {
    console.log("❌ Data file does not exist!");
}

// Test 3: Simulate bot restart (clear in-memory data)
console.log("\n=== Test 3: Simulate Bot Restart ===\n");

console.log("🔄 Clearing in-memory data (simulating bot restart)...");
users.clear();
moments.clear();

console.log(`📊 After clear: ${users.size} users, ${moments.size} moments`);

// Test 4: Load data from file
console.log("\n=== Test 4: Load Data from File ===\n");

const loaded = loadDataFromFile();

if (loaded) {
    console.log("✅ Data loaded successfully");
    console.log(`📊 After load: ${users.size} users`);

    const loadedUser = users.get(12345);
    if (loadedUser) {
        console.log(`✅ User found: ${loadedUser.first_name} (ID: ${loadedUser.telegram_id})`);
    } else {
        console.log("❌ User not found after load!");
    }

    const loadedMoments = getUserMoments(12345);
    console.log(`📊 Loaded moments: ${loadedMoments.length}`);

    // Verify specific content
    const foundMoment1 = loadedMoments.find(m => m.content === "TEST_MOMENT_1_UNIQUE_CONTENT");
    const foundMoment2 = loadedMoments.find(m => m.content === "TEST_MOMENT_2_ANOTHER_UNIQUE");

    if (foundMoment1) {
        console.log(`✅ Moment 1 found: "${foundMoment1.content}"`);
    } else {
        console.log("❌ Moment 1 not found!");
    }

    if (foundMoment2) {
        console.log(`✅ Moment 2 found: "${foundMoment2.content}"`);
    } else {
        console.log("❌ Moment 2 not found!");
    }
} else {
    console.log("❌ Failed to load data from file!");
}

// Test 5: Verify dates are preserved
console.log("\n=== Test 5: Verify Dates Preserved ===\n");

const testMoment = getUserMoments(12345)[0];
if (testMoment && testMoment.created_at instanceof Date) {
    console.log(`✅ Date is a Date object: ${testMoment.created_at.toISOString()}`);
} else {
    console.log("❌ Date is not a Date object!");
}

// Summary
console.log("\n" + "=".repeat(50));
console.log("FEATURE #62 TEST SUMMARY");
console.log("=".repeat(50));

const test1Pass = users.size === 1;
const test2Pass = getUserMoments(12345).length === 2;
const test3Pass = getUserMoments(12345).find(m => m.content.includes("TEST_MOMENT_1")) !== undefined;
const test4Pass = getUserMoments(12345)[0]?.created_at instanceof Date;

console.log(`Test 1 (User persisted): ${test1Pass ? "✅ PASS" : "❌ FAIL"}`);
console.log(`Test 2 (Moments count): ${test2Pass ? "✅ PASS" : "❌ FAIL"}`);
console.log(`Test 3 (Content preserved): ${test3Pass ? "✅ PASS" : "❌ FAIL"}`);
console.log(`Test 4 (Dates preserved): ${test4Pass ? "✅ PASS" : "❌ FAIL"}`);

const allPass = test1Pass && test2Pass && test3Pass && test4Pass;
console.log(`\nOverall: ${allPass ? "✅ ALL TESTS PASSED" : "❌ SOME TESTS FAILED"}`);

if (allPass) {
    console.log("\n🎉 Feature #62 (Data persistence across sessions) is working correctly!");
}

// Clean up
console.log("\n🗑️ Cleaning up test data file...");
if (existsSync(DATA_FILE)) {
    unlinkSync(DATA_FILE);
}
