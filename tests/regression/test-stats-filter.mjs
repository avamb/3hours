/**
 * Test script for statistics week/month filtering
 * Tests Feature #76: Statistics week/month views
 */

// Helper functions (same as test-bot.mjs)
function formatDate(date, languageCode = 'ru', includeTime = false) {
    const locale = languageCode === 'uk' ? 'uk-UA' :
                   languageCode === 'en' ? 'en-US' : 'ru-RU';
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    return date.toLocaleDateString(locale, options);
}

// Create test moments spanning different time periods
function createTestMoments() {
    const now = new Date();
    const moments = [];

    // Moments from today
    moments.push({
        id: 1,
        content: "Today's moment - work success",
        created_at: new Date(now)
    });

    // Moments from 3 days ago (within week)
    moments.push({
        id: 2,
        content: "3 days ago - friend meetup",
        created_at: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000)
    });

    // Moments from 6 days ago (within week)
    moments.push({
        id: 3,
        content: "6 days ago - gym workout",
        created_at: new Date(now.getTime() - 6 * 24 * 60 * 60 * 1000)
    });

    // Moments from 10 days ago (outside week, within month)
    moments.push({
        id: 4,
        content: "10 days ago - family dinner",
        created_at: new Date(now.getTime() - 10 * 24 * 60 * 60 * 1000)
    });

    // Moments from 20 days ago (within month)
    moments.push({
        id: 5,
        content: "20 days ago - movie night",
        created_at: new Date(now.getTime() - 20 * 24 * 60 * 60 * 1000)
    });

    // Moments from 25 days ago (within month)
    moments.push({
        id: 6,
        content: "25 days ago - shopping spree",
        created_at: new Date(now.getTime() - 25 * 24 * 60 * 60 * 1000)
    });

    // Moments from 35 days ago (outside month)
    moments.push({
        id: 7,
        content: "35 days ago - birthday party",
        created_at: new Date(now.getTime() - 35 * 24 * 60 * 60 * 1000)
    });

    // Moments from 45 days ago (outside month)
    moments.push({
        id: 8,
        content: "45 days ago - vacation memories",
        created_at: new Date(now.getTime() - 45 * 24 * 60 * 60 * 1000)
    });

    return moments;
}

// Simulate stats filter function
function filterMomentsByPeriod(moments, period) {
    const now = new Date();

    if (period === 'week') {
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        return moments.filter(m => m.created_at >= weekAgo);
    } else if (period === 'month') {
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        return moments.filter(m => m.created_at >= monthAgo);
    }

    return moments;
}

// Generate stats text
function generateStatsText(moments, period, languageCode = 'ru') {
    const now = new Date();
    const periodName = period === 'week' ? 'за неделю' : 'за месяц';
    const periodDays = period === 'week' ? 7 : 30;

    const startDate = formatDate(new Date(now.getTime() - periodDays * 24 * 60 * 60 * 1000), languageCode);
    const endDate = formatDate(now, languageCode);

    let statsText = `📊 <b>Статистика ${periodName}</b>\n`;
    statsText += `📅 ${startDate} — ${endDate}\n\n`;
    statsText += `🌟 Моментов: ${moments.length}\n`;

    return statsText;
}

console.log("=== Feature #76: Statistics Week/Month Views - Test ===\n");

// Step 1: Create moments across different weeks
console.log("Step 1: Create moments across different weeks/months");
console.log("-".repeat(50));

const testMoments = createTestMoments();
console.log(`Created ${testMoments.length} test moments:\n`);

for (const moment of testMoments) {
    const daysDiff = Math.floor((new Date() - moment.created_at) / (1000 * 60 * 60 * 24));
    console.log(`  ID ${moment.id}: "${moment.content}" (${daysDiff} days ago)`);
}

// Step 2: View weekly statistics
console.log("\n\nStep 2: View weekly statistics");
console.log("-".repeat(50));

const weekMoments = filterMomentsByPeriod(testMoments, 'week');
console.log(`\nFiltered moments for week: ${weekMoments.length}`);
for (const moment of weekMoments) {
    const daysDiff = Math.floor((new Date() - moment.created_at) / (1000 * 60 * 60 * 24));
    console.log(`  ✓ ID ${moment.id}: ${daysDiff} days ago`);
}

const weekStatsText = generateStatsText(weekMoments, 'week');
console.log(`\nGenerated stats text:\n${weekStatsText}`);

// Step 3: Verify only current week data shown
console.log("\n\nStep 3: Verify only current week data shown");
console.log("-".repeat(50));

const expectedWeekIds = [1, 2, 3]; // Today, 3 days ago, 6 days ago
const actualWeekIds = weekMoments.map(m => m.id).sort();
const weekCorrect = JSON.stringify(expectedWeekIds) === JSON.stringify(actualWeekIds);

console.log(`Expected week moments: IDs [${expectedWeekIds.join(', ')}]`);
console.log(`Actual week moments: IDs [${actualWeekIds.join(', ')}]`);
console.log(`Week filter correct: ${weekCorrect ? '✅ YES' : '❌ NO'}`);

// Step 4: View monthly statistics
console.log("\n\nStep 4: View monthly statistics");
console.log("-".repeat(50));

const monthMoments = filterMomentsByPeriod(testMoments, 'month');
console.log(`\nFiltered moments for month: ${monthMoments.length}`);
for (const moment of monthMoments) {
    const daysDiff = Math.floor((new Date() - moment.created_at) / (1000 * 60 * 60 * 24));
    console.log(`  ✓ ID ${moment.id}: ${daysDiff} days ago`);
}

const monthStatsText = generateStatsText(monthMoments, 'month');
console.log(`\nGenerated stats text:\n${monthStatsText}`);

// Step 5: Verify only current month data shown
console.log("\n\nStep 5: Verify only current month data shown");
console.log("-".repeat(50));

const expectedMonthIds = [1, 2, 3, 4, 5, 6]; // All except 35 and 45 days ago
const actualMonthIds = monthMoments.map(m => m.id).sort();
const monthCorrect = JSON.stringify(expectedMonthIds) === JSON.stringify(actualMonthIds);

console.log(`Expected month moments: IDs [${expectedMonthIds.join(', ')}]`);
console.log(`Actual month moments: IDs [${actualMonthIds.join(', ')}]`);
console.log(`Month filter correct: ${monthCorrect ? '✅ YES' : '❌ NO'}`);

// Summary
console.log("\n\n=== Test Summary ===");
console.log("-".repeat(50));
console.log(`Total test moments: ${testMoments.length}`);
console.log(`Week filter: ${weekCorrect ? '✅ PASS' : '❌ FAIL'} (${weekMoments.length} moments)`);
console.log(`Month filter: ${monthCorrect ? '✅ PASS' : '❌ FAIL'} (${monthMoments.length} moments)`);
console.log(`\nOverall result: ${weekCorrect && monthCorrect ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);

// Verify edge cases
console.log("\n\nEdge Case Verification:");
console.log("-".repeat(50));

// Moment exactly at boundary (7 days ago)
const exactlyWeekAgo = new Date(new Date().getTime() - 7 * 24 * 60 * 60 * 1000);
const boundaryMoment = { id: 99, content: "Exactly 7 days ago", created_at: exactlyWeekAgo };
const weekFilterWithBoundary = filterMomentsByPeriod([boundaryMoment], 'week');
console.log(`Moment exactly 7 days ago in week filter: ${weekFilterWithBoundary.length === 1 ? '✅ Included' : '❌ Excluded'}`);

// Moment exactly at month boundary (30 days ago)
const exactlyMonthAgo = new Date(new Date().getTime() - 30 * 24 * 60 * 60 * 1000);
const monthBoundaryMoment = { id: 100, content: "Exactly 30 days ago", created_at: exactlyMonthAgo };
const monthFilterWithBoundary = filterMomentsByPeriod([monthBoundaryMoment], 'month');
console.log(`Moment exactly 30 days ago in month filter: ${monthFilterWithBoundary.length === 1 ? '✅ Included' : '❌ Excluded'}`);

// Empty moments
const emptyMoments = filterMomentsByPeriod([], 'week');
console.log(`Empty moments list handled: ${emptyMoments.length === 0 ? '✅ Yes' : '❌ No'}`);
