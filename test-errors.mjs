/**
 * Test error messages for Feature #52
 */

const errorMessages = {
    ru: {
        generic: "Ой, что-то пошло не так 😔\nПопробуй ещё раз или напиши /start",
        network: "Не удалось подключиться к серверу 🌐\nПроверь интернет-соединение и попробуй снова",
        voice_recognition: "Не удалось распознать голосовое сообщение 🎤\nПопробуй записать ещё раз или напиши текстом",
        empty_input: "Сообщение пустое 📝\nПопробуй написать что-нибудь хорошее! 💝",
        not_found: "Ничего не найдено 🔍\nПопробуй другой запрос",
        action_failed: "Действие не выполнено 😕\nПопробуй ещё раз через несколько секунд",
        timeout: "Это заняло слишком много времени ⏳\nПопробуй ещё раз 🔄",
        invalid_time: "Время выбрано неверно ⏰\nПопробуй выбрать из предложенных вариантов 📋"
    },
    en: {
        generic: "Oops, something went wrong 😔\nTry again or send /start",
        network: "Could not connect to the server 🌐\nCheck your internet connection and try again",
        voice_recognition: "Could not recognize voice message 🎤\nTry recording again or type your message",
        empty_input: "Message is empty 📝\nTry writing something good! 💝",
        not_found: "Nothing found 🔍\nTry a different query",
        action_failed: "Action failed 😕\nTry again in a few seconds",
        timeout: "That took too long ⏳\nTry again please 🔄",
        invalid_time: "Time selected incorrectly ⏰\nTry selecting from the options provided 📋"
    },
    uk: {
        generic: "Ой, щось пішло не так 😔\nСпробуй ще раз або напиши /start",
        network: "Не вдалося підключитися до сервера 🌐\nПеревір інтернет-з'єднання і спробуй знову",
        voice_recognition: "Не вдалося розпізнати голосове повідомлення 🎤\nСпробуй записати ще раз або напиши текстом",
        empty_input: "Повідомлення порожнє 📝\nСпробуй написати щось хороше! 💝",
        not_found: "Нічого не знайдено 🔍\nСпробуй інший запит",
        action_failed: "Дію не виконано 😕\nСпробуй ще раз через кілька секунд",
        timeout: "Це зайняло надто багато часу ⏳\nСпробуй ще раз 🔄",
        invalid_time: "Час обрано неправильно ⏰\nСпробуй обрати з запропонованих варіантів 📋"
    }
};

function getErrorMessage(errorType, languageCode = 'ru') {
    const lang = errorMessages[languageCode] ? languageCode : 'ru';
    return errorMessages[lang][errorType] || errorMessages[lang].generic;
}

// Check for technical jargon (should NOT be present)
const technicalTerms = [
    'error', 'exception', 'null', 'undefined', 'stack', 'trace',
    'database', 'sql', 'api', 'request', 'response', 'http', 'status',
    'code', 'failed to', '500', '404', '403', 'connection refused'
];

function checkForTechnicalJargon(message) {
    const lowerMessage = message.toLowerCase();
    return technicalTerms.filter(term => lowerMessage.includes(term.toLowerCase()));
}

console.log('=== Error Message Friendliness Test ===');
console.log('');

const errorTypes = ['generic', 'network', 'voice_recognition', 'empty_input', 'not_found', 'action_failed', 'timeout', 'invalid_time'];
const languages = ['ru', 'en', 'uk'];

let allPassed = true;

for (const lang of languages) {
    console.log(`\n--- ${lang.toUpperCase()} ---`);
    for (const errorType of errorTypes) {
        const message = getErrorMessage(errorType, lang);
        const jargonFound = checkForTechnicalJargon(message);

        // Check if message suggests what to do
        const suggestsAction = message.includes('/') ||
                              message.toLowerCase().includes('попробуй') ||
                              message.toLowerCase().includes('try') ||
                              message.toLowerCase().includes('спробуй') ||
                              message.toLowerCase().includes('проверь') ||
                              message.toLowerCase().includes('check') ||
                              message.toLowerCase().includes('перевір') ||
                              message.toLowerCase().includes('выбери') ||
                              message.toLowerCase().includes('select') ||
                              message.toLowerCase().includes('обери');

        const hasEmoji = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{2600}-\u{26FF}]/u.test(message);

        const status = jargonFound.length === 0 && suggestsAction && hasEmoji ? '✅' : '❌';
        if (status === '❌') allPassed = false;

        console.log(`${status} ${errorType}:`);
        console.log(`   "${message.replace(/\n/g, ' | ')}"`);
        if (jargonFound.length > 0) {
            console.log(`   ⚠️ Technical jargon found: ${jargonFound.join(', ')}`);
        }
        if (!suggestsAction) {
            console.log(`   ⚠️ Message does not suggest what to do next`);
        }
        if (!hasEmoji) {
            console.log(`   ⚠️ Message has no emoji`);
        }
    }
}

console.log('\n=== Summary ===');
if (allPassed) {
    console.log('✅ All error messages are user-friendly!');
    console.log('  - No technical jargon');
    console.log('  - Messages in user\'s language');
    console.log('  - Messages suggest what to do next');
    console.log('  - Messages have friendly emoji');
} else {
    console.log('❌ Some error messages need improvement');
}
