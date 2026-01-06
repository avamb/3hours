/**
 * Test bot API to verify date formatting feature
 */

const BOT_TOKEN = '7805611571:AAF59MdS0N3By7mMq_O53Wo8LjYLwfXVrBY';
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
