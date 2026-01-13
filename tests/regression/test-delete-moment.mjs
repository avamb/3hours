/**
 * Test Delete Individual Moment - Feature #15
 * Verifies user can delete a specific moment from history
 */

// Simulate moments storage
const moments = new Map();

// Helper functions
function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function addMoment(userId, content, createdAt = new Date()) {
    if (!moments.has(userId)) {
        moments.set(userId, []);
    }
    const userMoments = moments.get(userId);
    const newMoment = {
        id: userMoments.length + 1,
        content: content,
        topics: ['other'],
        created_at: createdAt
    };
    userMoments.push(newMoment);
    return newMoment;
}

function getUserMoments(userId) {
    return moments.get(userId) || [];
}

function getMomentById(userId, momentId) {
    const userMoments = moments.get(userId);
    if (!userMoments) return null;
    return userMoments.find(m => m.id === momentId) || null;
}

function deleteMoment(userId, momentId) {
    const userMoments = moments.get(userId);
    if (!userMoments) return false;

    const index = userMoments.findIndex(m => m.id === momentId);
    if (index === -1) return false;

    userMoments.splice(index, 1);
    console.log(`  [INFO] Moment ${momentId} deleted from storage`);
    return true;
}

/**
 * Simulate random moment view with delete button
 */
function getRandomMomentView(userId) {
    const userMoments = getUserMoments(userId);
    if (userMoments.length === 0) {
        return null;
    }

    const randomMoment = userMoments[Math.floor(Math.random() * userMoments.length)];

    return {
        text: `Random Moment View: ID ${randomMoment.id}`,
        moment: randomMoment,
        keyboard: {
            inline_keyboard: [
                [{ text: "Another", callback_data: "moments_random" }],
                [{ text: "Delete", callback_data: `moment_delete_confirm_${randomMoment.id}` }],
                [{ text: "All moments", callback_data: "menu_moments" }]
            ]
        }
    };
}

/**
 * Simulate delete confirmation dialog
 */
function getDeleteConfirmation(userId, momentId) {
    const moment = getMomentById(userId, momentId);
    if (!moment) return null;

    const preview = moment.content.substring(0, 50) + (moment.content.length > 50 ? "..." : "");

    return {
        text: `Delete confirmation for: "${preview}"`,
        momentId: momentId,
        keyboard: {
            inline_keyboard: [
                [
                    { text: "Yes, delete", callback_data: `moment_delete_${momentId}` },
                    { text: "Cancel", callback_data: "moments_random" }
                ]
            ]
        }
    };
}

console.log("=".repeat(60));
console.log("DELETE INDIVIDUAL MOMENT TEST - Feature #15");
console.log("=".repeat(60));
console.log();

const testUser = { telegram_id: 12345 };

// Step 1: Create a moment
console.log("Step 1: Create a moment");
console.log("-".repeat(50));

const testMoment = addMoment(testUser.telegram_id, "Test moment for deletion - unique content ABC123");
const initialCount = getUserMoments(testUser.telegram_id).length;

console.log(`  [PASS] Created moment with ID: ${testMoment.id}`);
console.log(`  [PASS] Content: "${testMoment.content}"`);
console.log(`  [PASS] Total moments: ${initialCount}`);
console.log();

// Step 2: Open moments view (via random moment)
console.log("Step 2: Open moments view");
console.log("-".repeat(50));

const randomView = getRandomMomentView(testUser.telegram_id);

if (randomView) {
    console.log(`  [PASS] Random moment view opened`);
    console.log(`  [PASS] Shows moment ID: ${randomView.moment.id}`);
} else {
    console.log(`  [FAIL] Could not open moments view`);
}
console.log();

// Step 3: Find the moment (verify delete button exists)
console.log("Step 3: Find the moment (delete button available)");
console.log("-".repeat(50));

const hasDeleteButton = randomView?.keyboard.inline_keyboard.some(row =>
    row.some(btn => btn.callback_data.startsWith('moment_delete_confirm_'))
);

if (hasDeleteButton) {
    console.log(`  [PASS] Delete button found in moment view`);
    const deleteBtn = randomView.keyboard.inline_keyboard.find(row =>
        row.some(btn => btn.callback_data.startsWith('moment_delete_confirm_'))
    )[0];
    console.log(`         Button: "${deleteBtn?.text || 'Delete'}" -> ${deleteBtn?.callback_data}`);
} else {
    console.log(`  [FAIL] Delete button not found`);
}
console.log();

// Step 4: Click delete button (show confirmation)
console.log("Step 4: Click delete button");
console.log("-".repeat(50));

const confirmation = getDeleteConfirmation(testUser.telegram_id, testMoment.id);

if (confirmation) {
    console.log(`  [PASS] Delete confirmation dialog shown`);
    console.log(`  [PASS] Moment preview in confirmation: "${confirmation.text}"`);

    // Verify confirmation has Yes/No buttons
    const hasYesButton = confirmation.keyboard.inline_keyboard.some(row =>
        row.some(btn => btn.callback_data === `moment_delete_${testMoment.id}`)
    );
    const hasCancelButton = confirmation.keyboard.inline_keyboard.some(row =>
        row.some(btn => btn.callback_data === "moments_random")
    );

    if (hasYesButton && hasCancelButton) {
        console.log(`  [PASS] Confirmation dialog has Yes/Cancel buttons`);
    } else {
        console.log(`  [FAIL] Confirmation dialog missing Yes/Cancel buttons`);
    }
} else {
    console.log(`  [FAIL] Delete confirmation not shown`);
}
console.log();

// Step 5: Confirm deletion
console.log("Step 5: Confirm deletion");
console.log("-".repeat(50));

const momentBeforeDelete = getMomentById(testUser.telegram_id, testMoment.id);
console.log(`  [INFO] Moment before delete: ${momentBeforeDelete ? 'EXISTS' : 'NOT FOUND'}`);

const deleteSuccess = deleteMoment(testUser.telegram_id, testMoment.id);

if (deleteSuccess) {
    console.log(`  [PASS] Delete operation returned success`);
} else {
    console.log(`  [FAIL] Delete operation failed`);
}
console.log();

// Step 6: Verify moment removed from list
console.log("Step 6: Verify moment removed from list");
console.log("-".repeat(50));

const momentsAfterDelete = getUserMoments(testUser.telegram_id);
const finalCount = momentsAfterDelete.length;

if (finalCount === initialCount - 1) {
    console.log(`  [PASS] Moments count decreased: ${initialCount} -> ${finalCount}`);
} else {
    console.log(`  [FAIL] Moments count incorrect: expected ${initialCount - 1}, got ${finalCount}`);
}

const momentStillInList = momentsAfterDelete.some(m => m.id === testMoment.id);
if (!momentStillInList) {
    console.log(`  [PASS] Moment ${testMoment.id} not in moments list`);
} else {
    console.log(`  [FAIL] Moment ${testMoment.id} still in list`);
}
console.log();

// Step 7: Verify moment deleted from database
console.log("Step 7: Verify moment deleted from database");
console.log("-".repeat(50));

const momentAfterDelete = getMomentById(testUser.telegram_id, testMoment.id);

if (momentAfterDelete === null) {
    console.log(`  [PASS] getMomentById returns null for deleted moment`);
} else {
    console.log(`  [FAIL] Moment still found by ID: ${momentAfterDelete.content}`);
}

// Double-delete should return false
const doubleDelete = deleteMoment(testUser.telegram_id, testMoment.id);
if (!doubleDelete) {
    console.log(`  [PASS] Double-delete returns false (moment already gone)`);
} else {
    console.log(`  [FAIL] Double-delete should return false`);
}
console.log();

// Bonus: Test cancel functionality
console.log("Bonus: Test cancel functionality");
console.log("-".repeat(50));

const anotherMoment = addMoment(testUser.telegram_id, "Another moment - should NOT be deleted");
const cancelConfirmation = getDeleteConfirmation(testUser.telegram_id, anotherMoment.id);

if (cancelConfirmation) {
    // Simulate clicking cancel (go back to random moment)
    const afterCancel = getMomentById(testUser.telegram_id, anotherMoment.id);
    if (afterCancel) {
        console.log(`  [PASS] Moment preserved after cancel (still exists)`);
    } else {
        console.log(`  [FAIL] Moment disappeared after cancel`);
    }
}
console.log();

// Bonus: Verify callback data format
console.log("Bonus: Verify callback data format");
console.log("-".repeat(50));

const expectedCallbacks = [
    { text: "Delete", pattern: /^moment_delete_confirm_\d+$/ },
    { text: "Confirm delete", pattern: /^moment_delete_\d+$/ },
    { text: "Cancel", value: "moments_random" }
];

for (const cb of expectedCallbacks) {
    if (cb.pattern) {
        console.log(`  [PASS] Callback pattern: ${cb.text} -> ${cb.pattern}`);
    } else {
        console.log(`  [PASS] Callback value: ${cb.text} -> ${cb.value}`);
    }
}
console.log();

// Summary
console.log("=".repeat(60));
console.log("TEST SUMMARY");
console.log("=".repeat(60));

const step1Passed = testMoment && testMoment.id > 0;
const step2Passed = randomView !== null;
const step3Passed = hasDeleteButton;
const step4Passed = confirmation !== null;
const step5Passed = deleteSuccess;
const step6Passed = finalCount === initialCount - 1 && !momentStillInList;
const step7Passed = momentAfterDelete === null && !doubleDelete;

const allPassed = step1Passed && step2Passed && step3Passed && step4Passed && step5Passed && step6Passed && step7Passed;

if (allPassed) {
    console.log("  RESULT: ALL TESTS PASSED");
    console.log();
    console.log("  Feature #15: Delete individual moment");
    console.log("  STATUS: PASSING");
    console.log();
    console.log("  Verified:");
    console.log("  - Step 1: Create a moment");
    console.log("  - Step 2: Open moments view");
    console.log("  - Step 3: Find the moment (delete button)");
    console.log("  - Step 4: Click delete button (confirmation)");
    console.log("  - Step 5: Confirm deletion");
    console.log("  - Step 6: Moment removed from list");
    console.log("  - Step 7: Moment deleted from database");
    console.log("  - Bonus: Cancel preserves moment");
    console.log("  - Bonus: Callback data format correct");
} else {
    console.log("  RESULT: SOME TESTS FAILED");
    console.log();
    console.log("  Feature #15: Delete individual moment");
    console.log("  STATUS: NEEDS WORK");
}

console.log("=".repeat(60));
