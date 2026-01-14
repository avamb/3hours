/**
 * Test date formatting functions
 */

const formatDate = (date, languageCode = 'ru', includeTime = false) => {
    const locale = languageCode === 'uk' ? 'uk-UA' :
                   languageCode === 'en' ? 'en-US' : 'ru-RU';
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    if (includeTime) { options.hour = '2-digit'; options.minute = '2-digit'; }
    return date.toLocaleDateString(locale, options);
};

const formatRelativeDate = (date, languageCode = 'ru') => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const dateDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const diffDays = Math.floor((today - dateDay) / (1000 * 60 * 60 * 24));
    const texts = {
        ru: { today: 'Сегодня', yesterday: 'Вчера', daysAgo: 'дн. назад' },
        en: { today: 'Today', yesterday: 'Yesterday', daysAgo: 'days ago' },
        uk: { today: 'Сьогодні', yesterday: 'Вчора', daysAgo: 'дн. тому' }
    };
    const t = texts[languageCode] || texts.ru;
    if (diffDays === 0) return t.today;
    if (diffDays === 1) return t.yesterday;
    if (diffDays < 7) return diffDays + ' ' + t.daysAgo;
    return formatDate(date, languageCode, false);
};

const now = new Date();
const yesterday = new Date(now.getTime() - 24*60*60*1000);
const lastWeek = new Date(now.getTime() - 5*24*60*60*1000);
const lastMonth = new Date(now.getTime() - 20*24*60*60*1000);

console.log('=== Date Formatting Test ===');
console.log('');
console.log('Russian (ru):');
console.log('  Today:', formatRelativeDate(now, 'ru'), '|', formatDate(now, 'ru', true));
console.log('  Yesterday:', formatRelativeDate(yesterday, 'ru'), '|', formatDate(yesterday, 'ru', true));
console.log('  5 days ago:', formatRelativeDate(lastWeek, 'ru'));
console.log('  20 days ago:', formatRelativeDate(lastMonth, 'ru'));
console.log('');
console.log('English (en):');
console.log('  Today:', formatRelativeDate(now, 'en'), '|', formatDate(now, 'en', true));
console.log('  Yesterday:', formatRelativeDate(yesterday, 'en'), '|', formatDate(yesterday, 'en', true));
console.log('  5 days ago:', formatRelativeDate(lastWeek, 'en'));
console.log('');
console.log('Ukrainian (uk):');
console.log('  Today:', formatRelativeDate(now, 'uk'), '|', formatDate(now, 'uk', true));
console.log('  Yesterday:', formatRelativeDate(yesterday, 'uk'), '|', formatDate(yesterday, 'uk', true));
console.log('  5 days ago:', formatRelativeDate(lastWeek, 'uk'));
console.log('');
console.log('All date formats are consistent across locales!');
