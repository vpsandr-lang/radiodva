/**
 * RADIO DVA — Audio Player (Segment-based streaming)
 */
class RadioPlayer {
    constructor() {
        this.audio = new Audio();
        this.isPlaying = false;
        this.volume = 0.7;
        this.streamUrl = RADIO_CONFIG.streamUrl;
        this.audio.volume = this.volume;
        this.listeners = {};
        this.retryTimeout = null;

        this.audio.addEventListener('error', () => this._onError());
        this.audio.addEventListener('ended', () => this._onEnded());
        this.audio.addEventListener('canplay', () => this._onReady());
        this.audio.addEventListener('loadstart', () => this.emit('status', 'connecting'));
        this.audio.addEventListener('waiting', () => this.emit('status', 'buffering'));
    }

    on(event, callback) {
        if (!this.listeners[event]) this.listeners[event] = [];
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        (this.listeners[event] || []).forEach(cb => cb(data));
    }

    toggle() {
        if (this.isPlaying) this.stop();
        else this.play();
    }

    play() {
        this.emit('status', 'connecting');
        this.audio.src = this.streamUrl + '?t=' + Date.now();
        this.audio.load();

        const promise = this.audio.play();
        if (promise !== undefined) {
            promise.then(() => {
                this.isPlaying = true;
                this.emit('status', 'playing');
            }).catch(err => {
                console.warn('Play error:', err);
                this.emit('error', 'Нажми Play (браузер блокирует автозапуск)');
                this.emit('status', 'stopped');
            });
        }
    }

    stop() {
        this.audio.pause();
        this.audio.src = '';
        this.audio.load();
        this.isPlaying = false;
        if (this.retryTimeout) {
            clearTimeout(this.retryTimeout);
            this.retryTimeout = null;
        }
        this.emit('status', 'stopped');
    }

    setVolume(val) {
        this.volume = Math.max(0, Math.min(1, val));
        this.audio.volume = this.volume;
    }

    _onError() {
        this.isPlaying = false;
        this.emit('error', 'Ошибка загрузки. Переподключаюсь...');
        this.emit('status', 'stopped');
        // Retry after 3s (isPlaying was already set to false, so use a flag)
        if (this.retryTimeout) clearTimeout(this.retryTimeout);
        this.retryTimeout = setTimeout(() => {
            this.emit('status', 'connecting');
            this.audio.src = this.streamUrl + '?t=' + Date.now();
            this.audio.load();
            this.audio.play().catch(() => {});
        }, 3000);
    }

    _onEnded() {
        // Load next segment
        this.emit('status', 'connecting');
        this.audio.src = this.streamUrl + '?t=' + Date.now();
        this.audio.load();
        this.audio.play().catch(() => {
            // Retry once after 2s
            setTimeout(() => {
                this.audio.src = this.streamUrl + '?t=' + Date.now();
                this.audio.load();
                this.audio.play().catch(() => {});
            }, 2000);
        });
    }

    _onReady() {
        if (this.isPlaying) this.emit('status', 'playing');
    }

    destroy() {
        this.stop();
        this.audio.removeAttribute('src');
        this.audio.load();
        this.listeners = {};
    }
}
