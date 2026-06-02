/**
 * RADIO DVA — Audio Player (Fixed for HTTP)
 */

class RadioPlayer {
    constructor() {
        this.audio = new Audio();
        this.isPlaying = false;
        this.volume = 0.7;
        this.streamUrl = RADIO_CONFIG.streamUrl;
        this.audio.volume = this.volume;
        this.listeners = {};

        // Event handlers
        this.audio.addEventListener('play', () => this.isPlaying = true);
        this.audio.addEventListener('pause', () => this.isPlaying = false);
        this.audio.addEventListener('error', (e) => this.emit('error', 'Ошибка подключения'));
        this.audio.addEventListener('waiting', () => this.emit('status', 'buffering'));
        this.audio.addEventListener('canplay', () => { if(this.isPlaying) this.emit('status', 'playing'); });
        this.audio.addEventListener('loadedmetadata', () => { if(this.isPlaying) this.emit('status', 'playing'); });
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
        if (this.isPlaying) return;
        this.emit('status', 'connecting');
        
        this.audio.src = this.streamUrl;
        this.audio.load();
        
        const promise = this.audio.play();
        if (promise !== undefined) {
            promise.then(() => {
                this.isPlaying = true;
                this.emit('status', 'playing');
            }).catch(err => {
                console.warn('Play error:', err);
                this.emit('error', 'Нажми на кнопку Play (браузер блокирует автозапуск)');
                this.emit('status', 'stopped');
            });
        }
    }

    stop() {
        this.audio.pause();
        this.audio.src = '';
        this.audio.load();
        this.isPlaying = false;
        this.emit('status', 'stopped');
    }

    setVolume(val) {
        this.volume = Math.max(0, Math.min(1, val));
        this.audio.volume = this.volume;
    }

    destroy() {
        this.stop();
        this.audio.removeAttribute('src');
        this.audio.load();
        this.listeners = {};
    }
}
