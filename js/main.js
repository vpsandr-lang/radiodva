/**
 * RADIO DVA AI — Main Application
 * AI-powered radio with virtual hosts
 */
document.addEventListener('DOMContentLoaded', () => {

const $ = (s,p=document)=>p.querySelector(s);
const $$ = (s,p=document)=>p.querySelectorAll(s);

const npTitle = $('#npTitle');
const npArtist = $('#npArtist');
const playerStatus = $('#playerStatus');
const playerTiming = $('#playerTiming');
const btnPlay = $('#btnPlay');
const playIcon = btnPlay.querySelector('.play-icon');
const pauseIcon = btnPlay.querySelector('.pause-icon');
const npCover = $('#npCover');
const vinylRecord = $('#vinylRecord');
const vinylLabel = $('#vinylLabel');
const nowPlaying = $('#nowPlaying');
const equalizer = $('#equalizer');
const headerListeners = $('#headerListeners');
const listenerCount = $('#listenerCount');
const hostDisplay = $('#hostDisplay');
const toast = $('#toast');
const trackList = $('#trackList');

// Init player
const player = new RadioPlayer();
let currentHost = 'Алекс';

// ===== API ====
async function fetchNowPlaying() {
    try {
        const resp = await fetch('/api/now-playing');
        const data = await resp.json();
        if (data.title) {
            npTitle.textContent = data.title;
            npArtist.textContent = `${data.flag || ''} ${data.artist}`;
            currentHost = data.host || 'Алекс';
            if (data.listeners) {
                headerListeners.textContent = `👥 ${data.listeners}`;
                listenerCount.textContent = data.listeners;
            }
            updateHostDisplay(currentHost, data.intro);
        }
    } catch(e) {
        // Fallback to simulated data
    }
}

function updateHostDisplay(host, intro) {
    const hostEl = $('#hostDisplay') || (() => {
        const el = document.createElement('div');
        el.id = 'hostDisplay';
        el.className = 'host-display';
        $('.now-playing').after(el);
        return el;
    })();
    
    const emoji = host === 'Алекс' ? '🎧' : '🎙️';
    const style = host === 'Алекс' ? 'энергичный' : 'плавный';
    
    hostEl.innerHTML = `
        <div class="host-avatar">
            <div class="host-ring">
                <span class="host-emoji">${emoji}</span>
            </div>
            <div class="host-pulse"></div>
        </div>
        <div class="host-info">
            <span class="host-label">В ЭФИРЕ</span>
            <span class="host-name">${host}</span>
            <span class="host-style">${style}</span>
        </div>
    `;
}

// ===== PLAYER CONTROLS =====
const statusMsgs = {
    'playing': '🔴 В эфире', 'stopped': 'Нажми Play',
    'buffering': '⏳ Буферизация...', 'connecting': '⏳ Подключение...',
    'error': '❌ Ошибка'
};

player.on('status', (s) => {
    playerStatus.textContent = statusMsgs[s] || s;
    if (s === 'playing') {
        playerTiming.textContent = '🔴 LIVE';
        playerTiming.style.color = '#ef4444';
        playIcon.style.display = 'none';
        pauseIcon.style.display = 'block';
        nowPlaying.classList.add('playing');
        vinylRecord.classList.add('spinning');
        equalizer.style.opacity = '0.3';
    } else if (s === 'stopped' || s === 'error') {
        playerTiming.textContent = 'RADIO DVA';
        playerTiming.style.color = '#818cf8';
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
        nowPlaying.classList.remove('playing');
        vinylRecord.classList.remove('spinning');
        equalizer.style.opacity = '0.15';
    }
});

btnPlay.addEventListener('click', () => player.toggle());
$('#volumeSlider').addEventListener('input', (e) => player.setVolume(+e.target.value));

// ===== POLL API =====
fetchNowPlaying();
setInterval(fetchNowPlaying, 10000);

// ===== TOAST =====
function showToast(msg) {
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toast._t);
    toast._t = setTimeout(() => toast.classList.remove('show'), 3500);
}
window.showToast = showToast;

// ===== TRACK LIST =====
function renderTracks() {
    if (!trackList) return;
    // Show all tracks
    TRACK_HISTORY.forEach((t, i) => {
        const el = document.createElement('div');
        el.className = 'track-item';
        el.innerHTML = `
            <span class="track-num">${String(i+1).padStart(2,'0')}</span>
            <div class="track-info">
                <div class="track-name">${t.flag} ${t.title}</div>
                <div class="track-artist">${t.artist}</div>
            </div>
            <span class="track-time">${t.time}</span>`;
        trackList.appendChild(el);
    });
}

// ===== VINYL COLOR =====
function hashStr(s) { let h=0; for(let c of s) h=((h<<5)-h)+c.charCodeAt(0); return Math.abs(h); }
const h = hashStr('Prada');
vinylLabel.style.background = `linear-gradient(135deg,hsl(${h%360},60%,40%),hsl(${(h*7)%360},50%,30%))`;

// ===== INIT =====
renderTracks();
npTitle.textContent = 'Загрузка...';
npArtist.textContent = 'RADIO DVA';
playerStatus.textContent = 'Нажми Play';

console.log('%c🎧 RADIO DVA AI v3.0', 'font-size:20px;font-weight:bold;color:#6366f1');
console.log('%cС virtual host — Алекс & Лина', 'color:#818cf8');

});
