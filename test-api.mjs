/**
 * Test bot API to verify date formatting feature
 */

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || 'YOUR_BOT_TOKEN_HERE';
const BASE_URL = `https://api.telegram.org/bot${BOT_TOKEN}`;

async function getMe() {
    const response = await fetch(`${BASE_URL}/getMe`);
    return await response.json();
}

async function main() {
    console.log('Testing bot API...');

    const me = await getMe();
    if (me.ok) {
        console.log('Bot info:', me.result);
        console.log('Bot is online and responding!');
    } else {
        console.error('Bot error:', me);
    }
}

main().catch(console.error);
