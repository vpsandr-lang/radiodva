/**
 * RADIO DVA — Telegram Bot
 * Отправляет now-playing в Telegram-канал.
 *
 * Использование:
 * 1. Создать бота через @BotFather
 * 2. Добавить бота в канал как администратора
 * 3. Заполнить BOT_TOKEN и CHAT_ID
 * 4. Запустить: node bot/index.js
 */

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || 'ВАШ_ТОКЕН';
const CHAT_ID = process.env.TELEGRAM_CHAT_ID || '@radiodva_channel';

// Simulated current track — in production, fetch from API
function getCurrentTrack() {
    const tracks = [
        { title: 'Prada', artist: 'cassö, RAYE, D-Block Europe', flag: '🌍' },
        { title: 'Поначалу', artist: 'Баста', flag: '🇷🇺' },
        { title: 'Beautiful Things', artist: 'Benson Boone', flag: '🌍' },
        { title: 'Я твоя', artist: 'Anna Asti', flag: '🇷🇺' },
    ];
    return tracks[Math.floor(Math.random() * tracks.length)];
}

async function postToTelegram() {
    const track = getCurrentTrack();
    const message = `🎧 *Сейчас в эфире RADIO DVA*

${track.flag} *${track.title}* — ${track.artist}

🔗 Слушать: https://radiodva.ru`;

    try {
        const response = await fetch(
            `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_id: CHAT_ID,
                    text: message,
                    parse_mode: 'Markdown',
                    disable_web_page_preview: false
                })
            }
        );
        const data = await response.json();
        if (data.ok) {
            console.log(`✅ Posted: ${track.title} — ${track.artist}`);
        } else {
            console.error('❌ Telegram error:', data);
        }
    } catch (err) {
        console.error('❌ Network error:', err.message);
    }
}

// Post every 30 minutes
console.log('🤖 RADIO DVA Telegram Bot started');
postToTelegram();
setInterval(postToTelegram, 30 * 60 * 1000);

// Also allow manual trigger
if (process.argv.includes('--now')) {
    postToTelegram().then(() => process.exit(0));
}
