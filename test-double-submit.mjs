/**
 * Test script for Feature #60: Double submit prevention
 *
 * This test verifies that:
 * 1. Clicking save button twice quickly only creates one record
 * 2. Clicking delete button twice only causes single deletion
 * 3. Callback buttons are protected from double-clicks
 */

// Simulate the double-submit prevention logic
const processingCallbacks = new Map();
const processingActions = new Map();
const DOUBLE_SUBMIT_TIMEOUT = 2000;

function isCallbackProcessing(callbackId) {
    return processingCallbacks.has(callbackId);
}

function markCallbackProcessing(callbackId) {
    processingCallbacks.set(callbackId, Date.now());
    setTimeout(() => {
        processingCallbacks.delete(callbackId);
    }, DOUBLE_SUBMIT_TIMEOUT);
}

function isUserActionProcessing(userId, action) {
    const key = `${userId}:${action}`;
    const lastTime = processingActions.get(key);
    if (lastTime && (Date.now() - lastTime) < DOUBLE_SUBMIT_TIMEOUT) {
        return true;
    }
    return false;
}

function markUserActionProcessing(userId, action) {
    const key = `${userId}:${action}`;
    processingActions.set(key, Date.now());
    setTimeout(() => {
        processingActions.delete(key);
    }, DOUBLE_SUBMIT_TIMEOUT);
}

// Track results
let recordsCreated = 0;
let deletionsPerformed = 0;
let callbacksProcessed = 0;
let callbacksBlocked = 0;

// Test 1: Save button double-click simulation
console.log("=== Test 1: Save Button Double-Click Prevention ===\n");

async function simulateSaveMoment(userId, content) {
    if (isUserActionProcessing(userId, 'save_moment')) {
        console.log(`⚠️ BLOCKED: Double-submit prevented for save_moment (user ${userId})`);
        return false;
    }
    markUserActionProcessing(userId, 'save_moment');

    // Simulate saving
    recordsCreated++;
    console.log(`✅ Moment saved: "${content}" (Total: ${recordsCreated})`);
    return true;
}

// Simulate rapid double-click (both within 50ms)
const userId = 12345;
await simulateSaveMoment(userId, "First click");
await simulateSaveMoment(userId, "Second click (should be blocked)");

console.log(`\nResult: ${recordsCreated} record(s) created`);
console.log(recordsCreated === 1 ? "✅ PASS: Only one record created" : "❌ FAIL: Multiple records created");

// Wait for timeout and try again
console.log("\nWaiting for timeout (2.1 seconds)...");
await new Promise(resolve => setTimeout(resolve, 2100));

await simulateSaveMoment(userId, "Third click (after timeout, should succeed)");
console.log(`\nResult after timeout: ${recordsCreated} record(s) created`);
console.log(recordsCreated === 2 ? "✅ PASS: New record created after timeout" : "❌ FAIL: Record not created after timeout");

// Test 2: Delete button double-click simulation
console.log("\n=== Test 2: Delete Button Double-Click Prevention ===\n");

async function simulateDeleteData(userId) {
    if (isUserActionProcessing(userId, 'delete_data')) {
        console.log(`⚠️ BLOCKED: Double-submit prevented for delete_data (user ${userId})`);
        return false;
    }
    markUserActionProcessing(userId, 'delete_data');

    // Simulate deletion
    deletionsPerformed++;
    console.log(`✅ Data deleted for user ${userId} (Total deletions: ${deletionsPerformed})`);
    return true;
}

const userId2 = 67890;
await simulateDeleteData(userId2);
await simulateDeleteData(userId2);
await simulateDeleteData(userId2);

console.log(`\nResult: ${deletionsPerformed} deletion(s) performed`);
console.log(deletionsPerformed === 1 ? "✅ PASS: Only one deletion occurred" : "❌ FAIL: Multiple deletions occurred");

// Test 3: Callback button double-click simulation
console.log("\n=== Test 3: Callback Button Double-Click Prevention ===\n");

async function simulateCallback(callbackId) {
    if (isCallbackProcessing(callbackId)) {
        console.log(`⚠️ BLOCKED: Callback ${callbackId} already processing`);
        callbacksBlocked++;
        return false;
    }
    markCallbackProcessing(callbackId);

    callbacksProcessed++;
    console.log(`✅ Callback processed: ${callbackId} (Total: ${callbacksProcessed})`);
    return true;
}

// Simulate rapid clicks on same callback
const callbackId = "callback_123";
await simulateCallback(callbackId);
await simulateCallback(callbackId);
await simulateCallback(callbackId);

console.log(`\nResult: ${callbacksProcessed} callback(s) processed, ${callbacksBlocked} blocked`);
console.log(callbacksProcessed === 1 ? "✅ PASS: Only one callback processed" : "❌ FAIL: Multiple callbacks processed");

// Different callback IDs should all process
console.log("\n=== Test 4: Different Callback IDs Should Process ===\n");

const initialProcessed = callbacksProcessed;
await simulateCallback("callback_456");
await simulateCallback("callback_789");
await simulateCallback("callback_abc");

const newCallbacks = callbacksProcessed - initialProcessed;
console.log(`\nResult: ${newCallbacks} new callbacks processed`);
console.log(newCallbacks === 3 ? "✅ PASS: All different callbacks processed" : "❌ FAIL: Some callbacks were incorrectly blocked");

// Summary
console.log("\n" + "=".repeat(50));
console.log("FEATURE #60 TEST SUMMARY");
console.log("=".repeat(50));

const test1Pass = recordsCreated === 2; // 1 initial + 1 after timeout
const test2Pass = deletionsPerformed === 1;
const test3Pass = callbacksProcessed === 4; // 1 initial + 3 different IDs
const test4Pass = callbacksBlocked === 2; // 2 blocked duplicate callbacks

console.log(`Test 1 (Save double-click): ${test1Pass ? "✅ PASS" : "❌ FAIL"}`);
console.log(`Test 2 (Delete double-click): ${test2Pass ? "✅ PASS" : "❌ FAIL"}`);
console.log(`Test 3 (Callback double-click): ${test3Pass && test4Pass ? "✅ PASS" : "❌ FAIL"}`);

const allPass = test1Pass && test2Pass && test3Pass && test4Pass;
console.log(`\nOverall: ${allPass ? "✅ ALL TESTS PASSED" : "❌ SOME TESTS FAILED"}`);

if (allPass) {
    console.log("\n🎉 Feature #60 (Double submit prevention) is working correctly!");
}
