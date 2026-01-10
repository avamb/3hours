/**
 * Script to add OpenAI-powered free dialog with context
 */

import { readFileSync, writeFileSync } from 'fs';

const filePath = 'C:/Projects/3hours/test-bot.mjs';
let content = readFileSync(filePath, 'utf8');

// 1. Add OpenAI API key constant after BOT_TOKEN
const openaiConstant = `
// OpenAI API configuration
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || 'YOUR_OPENAI_API_KEY_HERE';
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';
`;

const insertAfter = "const BASE_URL = `https://api.telegram.org/bot${BOT_TOKEN}`;";
content = content.replace(insertAfter, insertAfter + openaiConstant);

// 2. Add generateDialogResponse function after groupMomentsByTopics
const dialogFunction = `

/**
 * Generate a personalized dialog response using OpenAI GPT-4
 * Uses user's moment history to provide relevant context
 * @param {string} userMessage - User's message
 * @param {object} user - User object
 * @param {Array} userMoments - User's saved moments
 * @returns {string} AI-generated response
 */
async function generateDialogResponse(userMessage, user, userMoments) {
    try {
        // Build context from user's moments
        let historyContext = "";
        if (userMoments.length > 0) {
            // Get last 10 moments for context (most recent first)
            const recentMoments = userMoments.slice(-10).reverse();
            historyContext = "Последние радостные моменты пользователя:\\n";
            for (const moment of recentMoments) {
                const date = new Date(moment.created_at).toLocaleDateString('ru-RU');
                historyContext += \`- \${date}: \${moment.content}\\n\`;
            }
            historyContext += "\\n";
        }

        // Build the system prompt
        const systemPrompt = \`Ты — дружелюбный помощник для развития позитивного мышления.
Твоя задача — поддержать пользователя, помочь ему увидеть хорошее в жизни.

Правила:
1. Будь тёплым и эмпатичным
2. Давай советы как "взгляд со стороны"
3. Напоминай о прошлых радостных моментах из истории пользователя
4. Помогай находить позитив в текущей ситуации
5. Явно указывай, что все решения принимает сам пользователь
6. Используй форму обращения: \${user.formal_address ? 'на «вы»' : 'на «ты»'}
7. Отвечай на языке пользователя (\${user.language_code === 'en' ? 'English' : user.language_code === 'uk' ? 'Українською' : 'Русский'})
8. Будь кратким, но содержательным (2-3 абзаца максимум)

\${historyContext}
Имя пользователя: \${user.first_name}\`;

        const response = await fetch(OPENAI_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': \`Bearer \${OPENAI_API_KEY}\`
            },
            body: JSON.stringify({
                model: 'gpt-4o-mini',
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: userMessage }
                ],
                max_tokens: 500,
                temperature: 0.7
            })
        });

        if (!response.ok) {
            console.error(\`OpenAI API error: \${response.status}\`);
            return null;
        }

        const data = await response.json();
        if (data.choices && data.choices[0] && data.choices[0].message) {
            console.log("✅ AI dialog response generated");
            return data.choices[0].message.content;
        }

        return null;
    } catch (error) {
        console.error("Error generating dialog response:", error.message);
        return null;
    }
}

/**
 * Generate a fallback response when OpenAI is unavailable
 * Uses user's moments to provide personalized support
 */
function generateFallbackDialogResponse(userMessage, user, userMoments) {
    const name = user.formal_address ? "Вы" : "ты";

    // Check if user has moments to reference
    if (userMoments.length > 0) {
        const randomMoment = userMoments[Math.floor(Math.random() * userMoments.length)];
        const momentContent = randomMoment.content.length > 100
            ? randomMoment.content.substring(0, 100) + "..."
            : randomMoment.content;

        const responses = [
            \`Я слышу \${name.toLowerCase()}. 💝 Помн\${user.formal_address ? 'ите' : 'ишь'}, как \${name.toLowerCase()} \${user.formal_address ? 'писали' : 'писал(а)'}: "\${momentContent}"? Такие моменты показывают, что в жизни много хорошего.\`,
            \`Спасибо, что \${user.formal_address ? 'поделились' : 'поделился(ась)'}. Кстати, среди \${user.formal_address ? 'Ваших' : 'твоих'} радостных моментов есть такой: "\${momentContent}". Может, это поможет взглянуть на ситуацию иначе? 🌟\`,
            \`Я \${user.formal_address ? 'Вас' : 'тебя'} понимаю. У \${name.toLowerCase()} есть много хороших моментов — например, "\${momentContent}". Давай\${user.formal_address ? 'те' : ''} вместе найдём что-то хорошее и сейчас! ✨\`
        ];

        return responses[Math.floor(Math.random() * responses.length)];
    }

    // Generic supportive response if no moments
    const responses = [
        \`Я слышу \${name.toLowerCase()}. 💝 Хоть у нас пока нет сохранённых радостных моментов, я уверен, что они есть в \${user.formal_address ? 'Вашей' : 'твоей'} жизни. Расскажи\${user.formal_address ? 'те' : ''} мне о чём-то хорошем, что произошло недавно?\`,
        \`Спасибо, что \${user.formal_address ? 'поделились' : 'поделился(ась)'}. Давай\${user.formal_address ? 'те' : ''} попробуем найти что-то позитивное вместе. Что хорошего \${user.formal_address ? 'Вы видели' : 'ты видел(а)'} сегодня, пусть даже мелочь? 🌟\`
    ];

    return responses[Math.floor(Math.random() * responses.length)];
}
`;

// Find groupMomentsByTopics function end and add after it
const groupMomentsEnd = `function groupMomentsByTopics(userMoments) {
    const groups = {};
    for (const moment of userMoments) {
        const topics = moment.topics || ['other'];
        for (const topicId of topics) {
            if (!groups[topicId]) {
                groups[topicId] = [];
            }
            groups[topicId].push(moment);
        }
    }
    return groups;
}`;

content = content.replace(groupMomentsEnd, groupMomentsEnd + dialogFunction);

// 3. Update menu_talk handler to set dialog state
const oldMenuTalk = `case "menu_talk":
            await sendMessage(chatId,
                "💬 <b>Режим диалога</b>\\n\\n" +
                "Я готов выслушать тебя. Расскажи, что у тебя на душе. " +
                "Я постараюсь помочь взглядом со стороны, " +
                "но помни — все решения принимаешь ты сам. 💝\\n\\n" +
                "Чтобы выйти из режима диалога, напиши /start"
            );
            break;`;

const newMenuTalk = `case "menu_talk":
            // Set user state to dialog mode
            userStates.set(user.telegram_id, { state: 'free_dialog' });
            await sendMessage(chatId,
                "💬 <b>Режим диалога</b>\\n\\n" +
                "Я готов выслушать тебя. Расскажи, что у тебя на душе. " +
                "Я постараюсь помочь взглядом со стороны, " +
                "используя твою историю радостных моментов для поддержки. " +
                "Но помни — все решения принимаешь ты сам. 💝\\n\\n" +
                "Чтобы выйти из режима диалога, напиши /start",
                {
                    inline_keyboard: [
                        [{ text: "❌ Выйти из диалога", callback_data: "exit_dialog" }]
                    ]
                }
            );
            console.log(\`✅ User \${user.telegram_id} entered free dialog mode\`);
            break;`;

content = content.replace(oldMenuTalk, newMenuTalk);

// 4. Add exit_dialog handler in callback processing
// Find where to add it - after the main menu callbacks section
const exitDialogHandler = `
        // Handle exit dialog callback
        if (callbackData === "exit_dialog") {
            userStates.delete(update.callback_query.from.id);
            await editMessage(
                update.callback_query.message.chat.id,
                update.callback_query.message.message_id,
                "✅ Вышли из режима диалога.\\n\\nИспользуй меню для навигации.",
                getMainMenuInline()
            );
            await answerCallback(update.callback_query.id, "Вышли из диалога");
            continue;
        }
`;

// Find a good place to add it - after callback processing starts
const callbackProcessingStart = "// Double-submit prevention for callbacks";
content = content.replace(
    callbackProcessingStart,
    exitDialogHandler + "\n        " + callbackProcessingStart
);

// 5. Add dialog message handling in the text message handler
// Find the part where we check for "adding moment" state
const oldAddingMomentCheck = `// Check if user is in "adding moment" state
    const state = userStates.get(user.telegram_id);

    if (state && state.state === 'adding_moment') {`;

const newAddingMomentCheck = `// Check if user is in "adding moment" state or "free dialog" mode
    const state = userStates.get(user.telegram_id);

    // Handle free dialog mode
    if (state && state.state === 'free_dialog') {
        console.log(\`Processing dialog message from user \${user.telegram_id}\`);

        // Get user's moments for context
        const userMoments = getUserMoments(user.telegram_id);

        // Try to generate AI response
        let response = await generateDialogResponse(text, user, userMoments);

        // Fall back to template-based response if AI fails
        if (!response) {
            console.log("⚠️ AI response failed, using fallback");
            response = generateFallbackDialogResponse(text, user, userMoments);
        }

        await sendMessage(chatId, response, {
            inline_keyboard: [
                [{ text: "❌ Выйти из диалога", callback_data: "exit_dialog" }]
            ]
        });

        return true;
    }

    if (state && state.state === 'adding_moment') {`;

content = content.replace(oldAddingMomentCheck, newAddingMomentCheck);

// Write the updated content
writeFileSync(filePath, content, 'utf8');
console.log('✅ test-bot.mjs updated with OpenAI-powered free dialog with context');
