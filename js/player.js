/**
 * RADIO DVA — Audio Player (Segment-based streaming)
 * Fixed: pause actually stops. No auto-resume.
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
        this._userStopped = false;  // true when user explicitly pressed pause

        this.audio.addEventListener('error', () => this._onError());
        this.audio.addEventListener('ended', () => this._onEnded());
        this.audio.addEventListener('canplay', () => this._onReady());
        this.audio.addEventListener('loadstart', () => {
            if (this.isPlaying && !this._userStopped) this.emit('status', 'connecting');
        });
        this.audio.addEventListener('waiting', () => {
            if (this.isPlaying && !this._userStopped) this.emit('status', 'buffering');
        });
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
        this._userStopped = false;
        this.emit('status', 'connecting');
        this.audio.src = this.streamUrl + '?t=' + Date.now();
        this.audio.load();

        const promise = this.audio.play();
        if (promise !== undefined) {
            promise.then(() => {
                this.isPlaying = true;
                this._userStopped = false;
                this.emit('status', 'playing');
            }).catch(err => {
                console.warn('Play error:', err);
                this.isPlaying = false;
                this.emit('error', 'Нажми Play (браузер блокирует автозапуск)');
                this.emit('status', 'stopped');
            });
        }
    }

    stop() {
        // Set flags BEFORE resetting audio to prevent race conditions
        this.isPlaying = false;
        this._userStopped = true;
        if (this.retryTimeout) {
            clearTimeout(this.retryTimeout);
            this.retryTimeout = null;
        }
        this.audio.pause();
        this.audio.removeAttribute('src');
        this.audio.load();
        this.emit('status', 'stopped');
    }

    setVolume(val) {
        this.volume = Math.max(0, Math.min(1, val));
        this.audio.volume = this.volume;
    }

    _onError() {
        if (!this.isPlaying || this._userStopped) return;
        this.emit('error', 'Ошибка загрузки. Переподключаюсь...');
        if (this.retryTimeout) clearTimeout(this.retryTimeout);
        this.retryTimeout = setTimeout(() => {
            if (!this.isPlaying || this._userStopped) return;
            this.emit('status', 'connecting');
            this.audio.src = this.streamUrl + '?t=' + Date.now();
            this.audio.load();
            this.audio.play().catch(() => {});
        }, 3000);
    }

    _onEnded() {
        if (!this.isPlaying || this._userStopped) {
            this.emit('status', 'stopped');
            return;
        }
        this.emit('status', 'connecting');
        this.audio.src = this.streamUrl + '?t=' + Date.now();
        this.audio.load();
        this.audio.play().catch(() => {
            if (!this.isPlaying || this._userStopped) return;
            setTimeout(() => {
                if (!this.isPlaying || this._userStopped) return;
                this.audio.src = this.streamUrl + '?t=' + Date.now();
                this.audio.load();
                this.audio.play().catch(() => {});
            }, 2000);
        });
    }

    _onReady() {
        if (this.isPlaying && !this._userStopped) this.emit('status', 'playing');
    }

    destroy() {
        this.stop();
        this.audio.removeAttribute('src');
        this.audio.load();
        this.listeners = {};
    }
}
