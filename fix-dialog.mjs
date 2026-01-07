/**
 * Fix the continue statement error
 */

import { readFileSync, writeFileSync } from 'fs';

const filePath = 'C:/Projects/3hours/test-bot.mjs';
let content = readFileSync(filePath, 'utf8');

// Fix the exit_dialog handler - replace continue with proper control flow
const badCode = `
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

        // Double-submit prevention for callbacks`;

const fixedCode = `// Double-submit prevention for callbacks`;

content = content.replace(badCode, fixedCode);

// Now add the exit_dialog handler in the proper location - in the callback handling switch/else-if chain
// Find where other callbacks are handled and add there
const handleCallbacksLocation = `else if (callbackData.startsWith("stats_")) {
            await handleStatsFilterCallback(update.callback_query, callbackData);
        }`;

const handleCallbacksFixed = `else if (callbackData === "exit_dialog") {
            // Exit free dialog mode
            userStates.delete(update.callback_query.from.id);
            await editMessage(
                update.callback_query.message.chat.id,
                update.callback_query.message.message_id,
                "✅ Вышли из режима диалога.\\n\\nИспользуй меню для навигации.",
                getMainMenuInline()
            );
            await answerCallback(update.callback_query.id, "Вышли из диалога");
            console.log("✅ User exited free dialog mode");
        } else if (callbackData.startsWith("stats_")) {
            await handleStatsFilterCallback(update.callback_query, callbackData);
        }`;

content = content.replace(handleCallbacksLocation, handleCallbacksFixed);

writeFileSync(filePath, content, 'utf8');
console.log('✅ Fixed the continue statement error');
