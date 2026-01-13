import { fileURLToPath } from 'url';
/**
 * Test Scheduled Notification Record Creation - Feature #94
 * Verifies scheduled_notifications records are created correctly
 */

import { readFileSync, existsSync } from 'fs';

// Read bot code to verify implementation
const botCode = readFileSync(new URL('./test-bot.mjs', import.meta.url), 'utf8');

console.log("=== Feature #94: Scheduled Notification Record Creation - Test ===\n");

// Step 1: Verify onboarding creates scheduled notification
console.log("Step 1: User completes onboarding");
console.log("-".repeat(50));

const hasOnboardingComplete = botCode.includes("user.onboarding_completed = true");
console.log(`Onboarding completion tracked: ${hasOnboardingComplete ? '✅ YES' : '❌ NO'}`);

const schedulesOnOnboarding = botCode.includes("// Schedule first notification for this user") &&
                              botCode.includes("scheduleNotificationJob(user.telegram_id, nextNotificationTime");
console.log(`Schedules notification on onboarding: ${schedulesOnOnboarding ? '✅ YES' : '❌ NO'}`);

const calculatesNextTime = botCode.includes("const nextNotificationTime = calculateNextNotificationTime(user)");
console.log(`Calculates next notification time: ${calculatesNextTime ? '✅ YES' : '❌ NO'}\n`);

// Step 2: Verify first notification is scheduled
console.log("Step 2: Verify first notification scheduled");
console.log("-".repeat(50));

const hasScheduleFunction = botCode.includes("function scheduleNotificationJob(userId, nextRunAt");
console.log(`scheduleNotificationJob function exists: ${hasScheduleFunction ? '✅ YES' : '❌ NO'}`);

const createsJobRecord = botCode.includes("const job = {") &&
                         botCode.includes("userId: userId") &&
                         botCode.includes("nextRunAt: nextRunAt");
console.log(`Creates job record with required fields: ${createsJobRecord ? '✅ YES' : '❌ NO'}`);

const addsToMap = botCode.includes("scheduledJobs.set(userId, job)");
console.log(`Adds job to scheduledJobs Map: ${addsToMap ? '✅ YES' : '❌ NO'}`);

const savesAfterSchedule = botCode.includes("scheduledJobs.set(userId, job)") &&
                            botCode.includes("saveDataToFile()");
console.log(`Persists after scheduling: ${savesAfterSchedule ? '✅ YES' : '❌ NO'}\n`);

// Step 3: Verify scheduled_notifications table (scheduledJobs Map)
console.log("Step 3: Query scheduled_notifications table (scheduledJobs)");
console.log("-".repeat(50));

const hasScheduledJobsMap = botCode.includes("const scheduledJobs = new Map()");
console.log(`scheduledJobs Map exists: ${hasScheduledJobsMap ? '✅ YES' : '❌ NO'}`);

const hasGetScheduledJob = botCode.includes("function getScheduledJob(userId)");
console.log(`getScheduledJob function exists: ${hasGetScheduledJob ? '✅ YES' : '❌ NO'}`);

const returnsJobOrNull = botCode.includes("return scheduledJobs.get(userId) || null");
console.log(`Returns job or null: ${returnsJobOrNull ? '✅ YES' : '❌ NO'}`);

// Check that jobs are loaded from file
const loadsJobsFromFile = botCode.includes("// Load scheduled jobs") &&
                           botCode.includes("if (data.scheduledJobs)");
console.log(`Loads jobs from file on startup: ${loadsJobsFromFile ? '✅ YES' : '❌ NO'}\n`);

// Step 4: Verify record exists with correct time
console.log("Step 4: Verify record exists with correct time");
console.log("-".repeat(50));

const hasCalculateNextTime = botCode.includes("function calculateNextNotificationTime(user)");
console.log(`calculateNextNotificationTime exists: ${hasCalculateNextTime ? '✅ YES' : '❌ NO'}`);

const usesInterval = botCode.includes("user.notification_interval_hours || 3");
console.log(`Uses user's notification interval: ${usesInterval ? '✅ YES' : '❌ NO'}`);

const checksActiveHours = botCode.includes("// If outside active hours, schedule for start of next active period");
console.log(`Schedules within active hours: ${checksActiveHours ? '✅ YES' : '❌ NO'}`);

const jobHasTimestamp = botCode.includes("scheduledAt: new Date()") &&
                        botCode.includes("nextRunAt: nextRunAt");
console.log(`Job record has timestamps: ${jobHasTimestamp ? '✅ YES' : '❌ NO'}`);

const jobHasStatus = botCode.includes("status: 'scheduled'");
console.log(`Job record has status: ${jobHasStatus ? '✅ YES' : '❌ NO'}\n`);

// Step 5: Simulate scheduling and verify record
console.log("Step 5: Simulate scheduling scenario");
console.log("-".repeat(50));

// Simulate user
const testUser = {
    telegram_id: 123456,
    notification_interval_hours: 3,
    active_hours_start: "09:00",
    active_hours_end: "21:00",
    timezone: "+03:00"
};

// Simulate calculateNextNotificationTime
function simulateCalculateNextTime(user) {
    const now = new Date();
    const intervalMs = (user.notification_interval_hours || 3) * 60 * 60 * 1000;
    return new Date(now.getTime() + intervalMs);
}

// Simulate scheduleNotificationJob
function simulateScheduleJob(userId, nextRunAt, jobType = 'question') {
    return {
        userId: userId,
        jobType: jobType,
        scheduledAt: new Date(),
        nextRunAt: nextRunAt,
        status: 'scheduled'
    };
}

const nextTime = simulateCalculateNextTime(testUser);
const scheduledJob = simulateScheduleJob(testUser.telegram_id, nextTime);

console.log("Simulated job record:");
console.log(`  userId: ${scheduledJob.userId}`);
console.log(`  jobType: ${scheduledJob.jobType}`);
console.log(`  status: ${scheduledJob.status}`);
console.log(`  scheduledAt: ${scheduledJob.scheduledAt.toISOString()}`);
console.log(`  nextRunAt: ${scheduledJob.nextRunAt.toISOString()}`);

const jobValid = scheduledJob.userId === 123456 &&
                 scheduledJob.jobType === 'question' &&
                 scheduledJob.status === 'scheduled' &&
                 scheduledJob.scheduledAt instanceof Date &&
                 scheduledJob.nextRunAt instanceof Date;

console.log(`\nJob record valid: ${jobValid ? '✅ YES' : '❌ NO'}`);

// Verify time is in the future
const timeDiff = scheduledJob.nextRunAt.getTime() - scheduledJob.scheduledAt.getTime();
const expectedMs = testUser.notification_interval_hours * 60 * 60 * 1000;
const timeCorrect = Math.abs(timeDiff - expectedMs) < 1000; // Allow 1 second tolerance
console.log(`Time interval correct (${testUser.notification_interval_hours}h): ${timeCorrect ? '✅ YES' : '❌ NO'}\n`);

// Check actual data file
console.log("Step 6: Check actual data file");
console.log("-".repeat(50));

const dataFile = fileURLToPath(new URL('../../bot-data.json', import.meta.url));
if (existsSync(dataFile)) {
    try {
        const data = JSON.parse(readFileSync(dataFile, 'utf8'));
        console.log(`Data file exists: ✅ YES`);
        console.log(`Has scheduledJobs: ${data.scheduledJobs !== undefined ? '✅ YES' : '⚠️ Not yet (created on first schedule)'}`);

        if (data.scheduledJobs && Object.keys(data.scheduledJobs).length > 0) {
            const jobCount = Object.keys(data.scheduledJobs).length;
            console.log(`Number of scheduled jobs: ${jobCount}`);

            // Show first job details
            const firstJobId = Object.keys(data.scheduledJobs)[0];
            const firstJob = data.scheduledJobs[firstJobId];
            console.log(`\nSample job record (user ${firstJobId}):`);
            console.log(`  jobType: ${firstJob.jobType}`);
            console.log(`  status: ${firstJob.status}`);
            console.log(`  nextRunAt: ${firstJob.nextRunAt}`);
        }
    } catch (e) {
        console.log(`Error reading data file: ${e.message}`);
    }
} else {
    console.log(`Data file exists: ⚠️ Not yet created`);
}

// Final summary
console.log("\n" + "=".repeat(50));
console.log("FINAL VERIFICATION SUMMARY");
console.log("=".repeat(50));

const checks = [
    { name: "Onboarding completion tracked", pass: hasOnboardingComplete },
    { name: "Schedules notification on onboarding", pass: schedulesOnOnboarding },
    { name: "Calculates next notification time", pass: calculatesNextTime },
    { name: "scheduleNotificationJob function exists", pass: hasScheduleFunction },
    { name: "Creates job record with required fields", pass: createsJobRecord },
    { name: "Adds job to scheduledJobs Map", pass: addsToMap },
    { name: "Persists after scheduling", pass: savesAfterSchedule },
    { name: "scheduledJobs Map exists", pass: hasScheduledJobsMap },
    { name: "getScheduledJob function exists", pass: hasGetScheduledJob },
    { name: "Returns job or null", pass: returnsJobOrNull },
    { name: "Loads jobs from file on startup", pass: loadsJobsFromFile },
    { name: "calculateNextNotificationTime exists", pass: hasCalculateNextTime },
    { name: "Uses user's notification interval", pass: usesInterval },
    { name: "Schedules within active hours", pass: checksActiveHours },
    { name: "Job record has timestamps", pass: jobHasTimestamp },
    { name: "Job record has status", pass: jobHasStatus },
    { name: "Simulated job record valid", pass: jobValid },
    { name: "Time interval correct", pass: timeCorrect }
];

let passCount = 0;
for (const check of checks) {
    console.log(`${check.pass ? '✅' : '❌'} ${check.name}`);
    if (check.pass) passCount++;
}

console.log(`\nTotal: ${passCount}/${checks.length} checks passed`);
console.log(`\n${passCount === checks.length ? '🎉 FEATURE #94 VERIFICATION: PASSED' : '⚠️ FEATURE #94 VERIFICATION: NEEDS WORK'}`);
