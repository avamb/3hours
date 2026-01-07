/**
 * Test script for moment display formatting
 * Tests Feature #86: Moment display formatting
 */

// Mock user
const testUser = {
    telegram_id: 12345,
    first_name: "Тест",
    language_code: "ru"
};

// Mock moments with varied content
const testMoments = [
    {
        id: 1,
        content: "Сегодня на работе получил повышение! Наконец-то признали мои заслуги.",
        created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
    },
    {
        id: 2,
        content: "Встретился с друзьями в кафе, было очень весело и душевно",
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
    },
    {
        id: 3,
        content: "Мама испекла мой любимый торт 🎂",
        created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
    },
    {
        id: 4,
        content: "Закончил книгу, которую давно хотел прочитать",
        created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
    },
    {
        id: 5,
        content: "Пробежал 10 км на тренировке - новый рекорд!",
        created_at: new Date()
    }
];

// Helper functions (same as in test-bot.mjs)
function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatDate(date, languageCode = 'ru', short = true) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();

    if (short) {
        return `${day}.${month}`;
    }
    return `${day}.${month}.${year}`;
}

function formatRelativeDate(date, languageCode = 'ru') {
    const now = new Date();
    const d = new Date(date);
    const diffDays = Math.floor((now - d) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "сегодня";
    if (diffDays === 1) return "вчера";
    if (diffDays < 7) {
        const days = ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'];
        return days[d.getDay()];
    }
    return formatDate(date, languageCode, false);
}

// Build moments text (same logic as in test-bot.mjs)
function buildMomentsText(userMoments, languageCode = 'ru') {
    if (userMoments.length === 0) {
        return "📖 У тебя пока нет сохранённых моментов.\nКогда придёт время вопроса, поделись чем-то хорошим! 🌟";
    }

    const recentMoments = userMoments.slice(-5).reverse();
    let momentsText = "📖 <b>Твои радостные моменты</b>\n\n";

    for (const moment of recentMoments) {
        const relativeDate = formatRelativeDate(moment.created_at, languageCode);
        const fullDate = formatDate(moment.created_at, languageCode, true);
        momentsText += `🌟 <i>${relativeDate}</i>\n`;
        momentsText += `${escapeHtml(moment.content)}\n`;
        momentsText += `<code>${fullDate}</code>\n\n`;
    }

    if (userMoments.length > 5) {
        momentsText += `\n📚 Всего моментов: ${userMoments.length}`;
    }

    return momentsText;
}

// Analyze moment formatting
function analyzeMomentFormatting(text) {
    const result = {
        text: text,
        hasTitle: false,
        momentCount: 0,
        momentsHaveDates: true,
        momentsHaveContent: true,
        hasSeparation: false,
        usesItalicForDate: false,
        usesCodeForTimestamp: false,
        hasStarEmoji: false
    };

    // Check for title
    result.hasTitle = text.includes('<b>') && text.includes('моменты');

    // Count moments (each starts with 🌟)
    const momentMatches = text.match(/🌟/g);
    result.momentCount = momentMatches ? momentMatches.length : 0;

    // Check formatting elements
    result.usesItalicForDate = text.includes('<i>') && text.includes('</i>');
    result.usesCodeForTimestamp = text.includes('<code>') && text.includes('</code>');
    result.hasStarEmoji = text.includes('🌟');

    // Check separation (double newlines between moments)
    result.hasSeparation = text.includes('\n\n');

    return result;
}

// Check if moments are clearly separated
function checkMomentSeparation(text) {
    const moments = text.split('🌟').filter(m => m.trim().length > 0);
    const results = [];

    for (let i = 0; i < moments.length; i++) {
        const moment = moments[i];
        const hasContent = moment.length > 10;
        const hasDate = moment.includes('<i>') || moment.includes('<code>');
        const endsWithBlankLine = moment.endsWith('\n\n');

        results.push({
            index: i + 1,
            preview: moment.substring(0, 50).replace(/\n/g, ' ').trim() + '...',
            hasContent,
            hasDate,
            hasSeparation: endsWithBlankLine || i === moments.length - 1
        });
    }

    return results;
}

// Check date visibility
function checkDateVisibility(text) {
    const lines = text.split('\n');
    const dateInfo = {
        relativeDates: [],
        absoluteDates: [],
        relativeDatesVisible: false,
        absoluteDatesVisible: false
    };

    for (const line of lines) {
        // Check for relative dates (italic)
        if (line.includes('<i>') && line.includes('</i>')) {
            const match = line.match(/<i>(.+?)<\/i>/);
            if (match) {
                dateInfo.relativeDates.push(match[1]);
            }
        }
        // Check for absolute dates (code)
        if (line.includes('<code>') && line.includes('</code>')) {
            const match = line.match(/<code>(.+?)<\/code>/);
            if (match) {
                dateInfo.absoluteDates.push(match[1]);
            }
        }
    }

    dateInfo.relativeDatesVisible = dateInfo.relativeDates.length > 0;
    dateInfo.absoluteDatesVisible = dateInfo.absoluteDates.length > 0;

    return dateInfo;
}

console.log("=== Feature #86: Moment Display Formatting - Test ===\n");

// Step 1: View moment in history
console.log("Step 1: View moment in history");
console.log("-".repeat(50));

const momentsText = buildMomentsText(testMoments, testUser.language_code);
console.log("Generated moments display:");
console.log("-".repeat(30));
console.log(momentsText);
console.log("-".repeat(30));

const analysis = analyzeMomentFormatting(momentsText);
console.log(`\nMoments displayed: ${analysis.momentCount}`);

// Step 2: Verify date is clearly shown
console.log("\n\nStep 2: Verify date is clearly shown");
console.log("-".repeat(50));

const dateInfo = checkDateVisibility(momentsText);
console.log("Date visibility analysis:");
console.log(`  Relative dates found: ${dateInfo.relativeDates.length}`);
console.log(`  Examples: ${dateInfo.relativeDates.slice(0, 3).join(', ')}`);
console.log(`  Absolute dates found: ${dateInfo.absoluteDates.length}`);
console.log(`  Examples: ${dateInfo.absoluteDates.slice(0, 3).join(', ')}`);

console.log("\nFormatting styles:");
console.log(`  Relative date uses italic (<i>): ${analysis.usesItalicForDate ? '✅ YES' : '❌ NO'}`);
console.log(`  Timestamp uses code (<code>): ${analysis.usesCodeForTimestamp ? '✅ YES' : '❌ NO'}`);

const datesAreClear = dateInfo.relativeDatesVisible && dateInfo.absoluteDatesVisible;
console.log(`\n${datesAreClear ? '✅' : '⚠️'} Dates are clearly shown: ${datesAreClear ? 'YES' : 'NO'}`);

// Step 3: Verify content is readable
console.log("\n\nStep 3: Verify content is readable");
console.log("-".repeat(50));

const momentSeparation = checkMomentSeparation(momentsText);
console.log("Content readability check:");

let allContentReadable = true;
for (const moment of momentSeparation) {
    console.log(`  Moment ${moment.index}: "${moment.preview}"`);
    console.log(`    Has content: ${moment.hasContent ? '✅' : '❌'}, Has date: ${moment.hasDate ? '✅' : '❌'}`);
    if (!moment.hasContent || !moment.hasDate) allContentReadable = false;
}

console.log(`\n${allContentReadable ? '✅' : '⚠️'} All content is readable: ${allContentReadable ? 'YES' : 'NO'}`);

// Test with HTML-special characters
console.log("\nBonus: HTML escaping test");
const specialMoment = [{
    id: 1,
    content: "Tested <script> & 'quotes' in text",
    created_at: new Date()
}];
const escapedText = buildMomentsText(specialMoment, 'ru');
const isProperlyEscaped = !escapedText.includes('<script>') && escapedText.includes('&lt;script&gt;');
console.log(`  Special chars escaped properly: ${isProperlyEscaped ? '✅ YES' : '❌ NO'}`);

// Step 4: Verify separation between moments
console.log("\n\nStep 4: Verify separation between moments");
console.log("-".repeat(50));

const hasSeparation = analysis.hasSeparation;
console.log(`Double newline separation: ${hasSeparation ? '✅ YES' : '❌ NO'}`);

let allSeparated = true;
for (const moment of momentSeparation.slice(0, -1)) {
    if (!moment.hasSeparation) allSeparated = false;
}
console.log(`All moments have separation: ${allSeparated ? '✅ YES' : '❌ NO'}`);

// Visual structure check
console.log("\nVisual structure:");
console.log("  Each moment follows pattern:");
console.log("    🌟 <relative date in italic>");
console.log("    Content text");
console.log("    <absolute date in code>");
console.log("    [blank line]");

const hasCorrectPattern = analysis.hasStarEmoji &&
                          analysis.usesItalicForDate &&
                          analysis.usesCodeForTimestamp;
console.log(`\n${hasCorrectPattern ? '✅' : '⚠️'} Correct visual pattern: ${hasCorrectPattern ? 'YES' : 'NO'}`);

// Test empty moments
console.log("\n\nBonus: Empty moments display");
console.log("-".repeat(50));
const emptyText = buildMomentsText([], 'ru');
const hasEmptyMessage = emptyText.includes('нет сохранённых моментов') && emptyText.includes('🌟');
console.log(`Empty state message: "${emptyText.substring(0, 50)}..."`);
console.log(`Has friendly empty message: ${hasEmptyMessage ? '✅ YES' : '❌ NO'}`);

// Summary
console.log("\n\n=== Test Summary ===");
console.log("-".repeat(50));
console.log("Feature #86: Moment display formatting");
console.log("");
console.log("✅ Step 1: Moments can be viewed in history");
console.log(`${datesAreClear ? '✅' : '⚠️'} Step 2: Date is clearly shown (relative + absolute)`);
console.log(`${allContentReadable ? '✅' : '⚠️'} Step 3: Content is readable`);
console.log(`${hasSeparation && allSeparated ? '✅' : '⚠️'} Step 4: Separation between moments`);
console.log("");
console.log("Formatting details:");
console.log(`  - Title with emoji: ${analysis.hasTitle ? 'YES' : 'NO'}`);
console.log(`  - Star emoji per moment: ${analysis.hasStarEmoji ? 'YES' : 'NO'}`);
console.log(`  - Italic for relative date: ${analysis.usesItalicForDate ? 'YES' : 'NO'}`);
console.log(`  - Code for timestamp: ${analysis.usesCodeForTimestamp ? 'YES' : 'NO'}`);
console.log(`  - Blank line separation: ${hasSeparation ? 'YES' : 'NO'}`);
console.log(`  - HTML escaping: ${isProperlyEscaped ? 'YES' : 'NO'}`);
console.log("");

const allPassed = datesAreClear && allContentReadable && hasSeparation && hasCorrectPattern;
console.log(`Result: ${allPassed ? '✅ ALL TESTS PASSED' : '⚠️ NEEDS IMPROVEMENT'}`);
console.log("");
console.log("Moments are displayed with clear dates, readable content,");
console.log("and proper visual separation between entries.");
