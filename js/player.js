/**
 * RADIO DVA — Audio Player
 * Handles streaming audio connection and control
 */

class RadioPlayer {
    constructor() {
        this.audio = new Audio();
        this.audioElement = this.audio;
        this.isPlaying = false;
        this.volume = 0.7;
        this.streamUrl = RADIO_CONFIG.streamUrl;

        this.audio.volume = this.volume;
        this.audio.preload = 'none';

        // Bind event handlers
        this.audio.addEventListener('play', () => this.onPlay());
        this.audio.addEventListener('pause', () => this.onPause());
        this.audio.addEventListener('error', (e) => this.onError(e));
        this.audio.addEventListener('waiting', () => this.onBuffering());
        this.audio.addEventListener('canplay', () => this.onReady());
        this.audio.addEventListener('loadstart', () => this.onConnecting());

        this.listeners = {};
    }

    on(event, callback) {
        if (!this.listeners[event]) this.listeners[event] = [];
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        (this.listeners[event] || []).forEach(cb => cb(data));
    }

    toggle() {
        if (this.isPlaying) {
            this.stop();
        } else {
            this.play();
        }
    }

    play() {
        if (this.isPlaying) return;

        this.audio.src = this.streamUrl;
        this.audio.load();

        const playPromise = this.audio.play();
        if (playPromise !== undefined) {
            playPromise
                .then(() => {
                    this.isPlaying = true;
                    this.emit('status', 'playing');
                })
                .catch(err => {
                    console.warn('Playback failed:', err);
                    this.emit('error', 'Не удалось подключиться к стриму. Попробуй позже.');
                });
        }
    }

    stop() {
        if (!this.isPlaying) return;
        this.audio.pause();
        this.audio.src = '';
        this.audio.load();
        this.isPlaying = false;
        this.emit('status', 'stopped');
    }

    setVolume(val) {
        this.volume = Math.max(0, Math.min(1, val));
        this.audio.volume = this.volume;
        this.emit('volume', this.volume);
    }

    setStream(url) {
        this.streamUrl = url;
        if (this.isPlaying) {
            this.stop();
            setTimeout(() => this.play(), 300);
        }
    }

    // Internal handlers
    onPlay() {
        this.isPlaying = true;
        this.emit('status', 'playing');
    }

    onPause() {
        this.isPlaying = false;
        this.emit('status', 'stopped');
    }

    onError(e) {
        const code = this.audio.error ? this.audio.error.code : -1;
        let msg = 'Ошибка подключения к стриму';
        if (code === MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED) {
            msg = 'Формат стрима не поддерживается браузером';
        } else if (code === MediaError.MEDIA_ERR_NETWORK) {
            msg = 'Сетевая ошибка. Проверь подключение к интернету';
        }
        this.isPlaying = false;
        this.emit('error', msg);
        this.emit('status', 'error');
    }

    onBuffering() {
        this.emit('status', 'buffering');
    }

    onReady() {
        this.emit('status', 'playing');
    }

    onConnecting() {
        this.emit('status', 'connecting');
    }

    destroy() {
        this.stop();
        this.audio.removeAttribute('src');
        this.audio.load();
        this.listeners = {};
    }
}
