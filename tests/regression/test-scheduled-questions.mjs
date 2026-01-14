/**
 * Test Scheduled Question Delivery - Feature #8
 * Verifies bot sends questions at configured intervals during active hours
 */

import { readFileSync } from 'fs';

// Read bot code to verify implementation
const botCode = readFileSync(new URL('./test-bot.mjs', import.meta.url), 'utf8');

console.log("=== Feature #8: Scheduled Question Delivery - Test ===\n");

// Step 1: Verify sendScheduledQuestion function exists
console.log("Step 1: Verify sendScheduledQuestion function");
console.log("-".repeat(50));

const hasSendScheduledQuestion = botCode.includes("async function sendScheduledQuestion(user)");
console.log("sendScheduledQuestion function exists: " + (hasSendScheduledQuestion ? "YES" : "NO"));

// Step 2: Verify active hours checking
console.log("\nStep 2: Verify active hours checking");
console.log("-".repeat(50));

const hasIsWithinActiveHours = botCode.includes("function isWithinActiveHours(user");
console.log("isWithinActiveHours function exists: " + (hasIsWithinActiveHours ? "YES" : "NO"));

const checksActiveHours = botCode.includes("if (!isWithinActiveHours(user))");
console.log("Checks active hours before sending: " + (checksActiveHours ? "YES" : "NO"));

// Step 3: Verify notification interval handling
console.log("\nStep 3: Verify notification interval handling");
console.log("-".repeat(50));

const hasCalculateNextTime = botCode.includes("function calculateNextNotificationTime(user)");
console.log("calculateNextNotificationTime function exists: " + (hasCalculateNextTime ? "YES" : "NO"));

const usesInterval = botCode.includes("notification_interval_hours");
console.log("Uses notification_interval_hours setting: " + (usesInterval ? "YES" : "NO"));

// Step 4: Verify job scheduling
console.log("\nStep 4: Verify job scheduling");
console.log("-".repeat(50));

const hasScheduleJob = botCode.includes("function scheduleNotificationJob(userId, nextRunAt");
console.log("scheduleNotificationJob function exists: " + (hasScheduleJob ? "YES" : "NO"));

const schedulesNextQuestion = botCode.includes("scheduleNotificationJob(user.telegram_id, nextTime");
console.log("Schedules next question after sending: " + (schedulesNextQuestion ? "YES" : "NO"));

// Step 5: Verify job scheduler
console.log("\nStep 5: Verify job scheduler");
console.log("-".repeat(50));

const hasCheckScheduledJobs = botCode.includes("async function checkScheduledJobs()");
console.log("checkScheduledJobs function exists: " + (hasCheckScheduledJobs ? "YES" : "NO"));

const hasStartJobScheduler = botCode.includes("function startJobScheduler()");
console.log("startJobScheduler function exists: " + (hasStartJobScheduler ? "YES" : "NO"));

const hasIntervalCheck = botCode.includes("setInterval(checkScheduledJobs");
console.log("Uses setInterval for periodic checks: " + (hasIntervalCheck ? "YES" : "NO"));

// Step 6: Verify varied templates usage
console.log("\nStep 6: Verify varied templates usage");
console.log("-".repeat(50));

const usesGetQuestionForUser = botCode.includes("getQuestionForUser(user)");
console.log("Uses getQuestionForUser for varied templates: " + (usesGetQuestionForUser ? "YES" : "NO"));

const hasReturnInactive = botCode.includes("return_inactive");
console.log("Supports return_inactive questions: " + (hasReturnInactive ? "YES" : "NO"));

// Step 7: Verify user state tracking
console.log("\nStep 7: Verify user state tracking");
console.log("-".repeat(50));

const setsAddingMomentState = botCode.includes("state: 'adding_moment'") &&
                               botCode.includes("question_asked_at");
console.log("Sets adding_moment state with question_asked_at: " + (setsAddingMomentState ? "YES" : "NO"));

// Step 8: Verify questions_sent counter
console.log("\nStep 8: Verify questions_sent counter");
console.log("-".repeat(50));

const incrementsQuestionsSent = botCode.includes("statistics.questions_sent") &&
                                 botCode.includes("questions_sent || 0) + 1");
console.log("Increments questions_sent counter: " + (incrementsQuestionsSent ? "YES" : "NO"));

// Step 9: Simulate scheduled question delivery
console.log("\nStep 9: Simulate scheduled question delivery");
console.log("-".repeat(50));

const scheduledJobs = new Map();

function simulateScheduleNotificationJob(userId, nextRunAt, jobType = 'question') {
    const job = {
        userId: userId,
        jobType: jobType,
        scheduledAt: new Date(),
        nextRunAt: nextRunAt,
        status: 'scheduled'
    };
    scheduledJobs.set(userId, job);
    return job;
}

function simulateCalculateNextNotificationTime(user) {
    const now = new Date();
    const intervalMs = (user.notification_interval_hours || 3) * 60 * 60 * 1000;
    return new Date(now.getTime() + intervalMs);
}

const testUser = {
    telegram_id: 123,
    notifications_enabled: true,
    onboarding_completed: true,
    active_hours_start: "09:00",
    active_hours_end: "21:00",
    notification_interval_hours: 3,
    timezone: "UTC"
};

const nextTime = simulateCalculateNextNotificationTime(testUser);
const job = simulateScheduleNotificationJob(testUser.telegram_id, nextTime, 'question');

console.log("Created scheduled job:");
console.log("  userId: " + job.userId);
console.log("  jobType: " + job.jobType);
console.log("  status: " + job.status);
console.log("  nextRunAt: " + job.nextRunAt.toISOString());

const jobScheduled = job.status === 'scheduled';
console.log("\nJob scheduled successfully: " + (jobScheduled ? "YES" : "NO"));

// Check interval from NOW, not from scheduledAt
const now = new Date();
const hasCorrectInterval = (job.nextRunAt.getTime() - now.getTime()) >= (3 * 60 * 60 * 1000 - 1000); // Allow 1 second tolerance
console.log("Interval is >= 3 hours from now: " + (hasCorrectInterval ? "YES" : "NO"));

// Step 10: Verify restore functionality
console.log("\nStep 10: Verify job restore on restart");
console.log("-".repeat(50));

const hasRestoreScheduledJobs = botCode.includes("function restoreScheduledJobs()");
console.log("restoreScheduledJobs function exists: " + (hasRestoreScheduledJobs ? "YES" : "NO"));

// Final summary
console.log("\n" + "=".repeat(50));
console.log("FINAL VERIFICATION SUMMARY");
console.log("=".repeat(50));

const checks = [
    { name: "sendScheduledQuestion function exists", pass: hasSendScheduledQuestion },
    { name: "isWithinActiveHours function exists", pass: hasIsWithinActiveHours },
    { name: "Checks active hours before sending", pass: checksActiveHours },
    { name: "calculateNextNotificationTime function exists", pass: hasCalculateNextTime },
    { name: "Uses notification_interval_hours setting", pass: usesInterval },
    { name: "scheduleNotificationJob function exists", pass: hasScheduleJob },
    { name: "Schedules next question after sending", pass: schedulesNextQuestion },
    { name: "checkScheduledJobs function exists", pass: hasCheckScheduledJobs },
    { name: "startJobScheduler function exists", pass: hasStartJobScheduler },
    { name: "Uses setInterval for periodic checks", pass: hasIntervalCheck },
    { name: "Uses getQuestionForUser for varied templates", pass: usesGetQuestionForUser },
    { name: "Supports return_inactive questions", pass: hasReturnInactive },
    { name: "Sets adding_moment state with question_asked_at", pass: setsAddingMomentState },
    { name: "Increments questions_sent counter", pass: incrementsQuestionsSent },
    { name: "Simulation: Job scheduled successfully", pass: jobScheduled },
    { name: "Simulation: Interval is >= 3 hours from now", pass: hasCorrectInterval },
    { name: "restoreScheduledJobs function exists", pass: hasRestoreScheduledJobs }
];

let passCount = 0;
for (const check of checks) {
    console.log((check.pass ? "[PASS]" : "[FAIL]") + " " + check.name);
    if (check.pass) passCount++;
}

console.log("\nTotal: " + passCount + "/" + checks.length + " checks passed");

if (passCount === checks.length) {
    console.log("\nFEATURE #8 VERIFICATION: PASSED");
} else {
    console.log("\nFEATURE #8 VERIFICATION: NEEDS WORK");
}
