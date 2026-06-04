"""RADIO DVA — Simple File-Based Broadcaster
Generates MP3 segments with real DJ voices and real music tracks.
"""
import sys, os, time, json, random, subprocess, threading, wave, struct, math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from ai_dj.music import MusicScheduler
from ai_dj.scripts import ScriptGenerator
from ai_dj.tts import TTSGenerator
from ai_dj.mixer import AudioMixer

STREAM_FILE = "/tmp/radio/current_broadcast.mp3"
SEGMENT_DIR = "/tmp/radio/segments/"
CACHE_DIR = "/tmp/radio/cache/"
os.makedirs(SEGMENT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

NP_FILE = os.path.join(os.path.dirname(__file__), "now-playing.json")


class FileBroadcaster:
    """Background thread that generates broadcast segments."""

    def __init__(self):
        self.music = MusicScheduler()
        self.scripts = ScriptGenerator("Алекс")
        self.tts = TTSGenerator()
        self.mixer = AudioMixer()
        self.host = "Алекс"
        self.segment_count = 0
        self.start_time = time.time()
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        print("=" * 50, flush=True)
        print("  RADIO DVA — AI Radio Starting", flush=True)
        print("=" * 50, flush=True)
        
        # Create initial test tone
        self._write_test_tone()
        time.sleep(1)

        while self.running:
            try:
                self._generate_and_write()
            except Exception as e:
                print(f"  ❌ Error: {e}", flush=True)
                import traceback
                traceback.print_exc()
                time.sleep(5)

    def _write_test_tone(self):
        """Write a short test tone so the stream file exists."""
        sr = 44100
        dur = 2
        samples = []
        for i in range(sr * dur):
            t = i / sr
            val = math.sin(2 * math.pi * 220 * t) * 0.15
            fade = min(t / 0.05, 1.0, (dur - t) / 0.05)
            val *= fade
            samples.append(int(val * 32767))
        
        wav = "/tmp/radio/init_tone.wav"
        with wave.open(wav, 'w') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            for s in samples:
                wf.writeframes(struct.pack('<hh', s, s))
        
        mp3 = "/tmp/radio/init_tone.mp3"
        subprocess.run(['lame', '--quiet', '-h', '-b', '64', wav, mp3],
                      capture_output=True, timeout=30)
        
        if os.path.exists(mp3):
            with open(mp3, 'rb') as f:
                data = f.read()
            with open(STREAM_FILE, 'wb') as f:
                f.write(data)
            print(f"  🔈 Initial tone: {len(data)//1024}KB", flush=True)

    def _generate_and_write(self):
        """Generate one broadcast segment and append to stream."""
        # Switch host every 3 segments
        if self.segment_count > 0 and self.segment_count % 3 == 0:
            self.host = "Лина" if self.host == "Алекс" else "Алекс"
            self.scripts.switch_dj(self.host)
            print(f"  🎙️ DJ switch → {self.host}", flush=True)

        # Pick track
        track = self.music.next_track()
        ts = time.strftime('%H:%M:%S')
        flag = track.get("flag", "🎵")
        title = track.get("title", "Unknown")
        artist = track.get("artist", "Unknown")
        genre = track.get("genre", "world")

        print(f"[{ts}] #{self.segment_count} {flag} {title} — {artist} [{self.host}]", flush=True)

        # Generate DJ scripts
        hour = time.localtime().tm_hour
        intro_text, outro_text = self.scripts.generate_show_segment(track, None, hour)
        
        print(f"  📝 Intro: {intro_text[:100]}", flush=True)
        print(f"  📝 Outro: {outro_text[:100]}", flush=True)

        # Generate voiceovers via TTS
        intro_path = self.tts.generate(intro_text, self.host, f"seg_{self.segment_count}_i.wav")
        outro_path = self.tts.generate(outro_text, self.host, f"seg_{self.segment_count}_o.wav")
        
        if intro_path:
            dur = self.tts.get_audio_duration(intro_path)
            print(f"  🎤 Intro voice: {dur:.1f}s", flush=True)
        if outro_path:
            dur = self.tts.get_audio_duration(outro_path)
            print(f"  🎤 Outro voice: {dur:.1f}s", flush=True)

        # Get music file
        music_path = self.mixer.get_music(track)
        if music_path:
            print(f"  🎵 Music: {os.path.basename(music_path)} ({os.path.getsize(music_path)//1024}KB)", flush=True)
        else:
            print(f"  ⚠️ No music file for {track['id']}, using fallback", flush=True)

        # Create broadcast segment
        segment_wav = self.mixer.create_broadcast_segment(
            music_wav=music_path,
            voice_intro_wav=intro_path,
            voice_outro_wav=outro_path
        )

        # Convert to MP3
        mp3_path = self.mixer.wav_to_mp3(segment_wav)

        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
            with open(mp3_path, 'rb') as f:
                mp3_data = f.read()

            mode = 'wb' if self.segment_count == 0 else 'ab'
            with open(STREAM_FILE, mode) as f:
                f.write(mp3_data)

            total_kb = os.path.getsize(STREAM_FILE) // 1024
            seg_kb = len(mp3_data) // 1024
            print(f"  📡 Broadcast: +{seg_kb}KB = {total_kb}KB total", flush=True)

        # Update now-playing
        self._update_now_playing(track)
        self.segment_count += 1
        
        # Small pause between segments
        time.sleep(random.uniform(0.3, 1.0))

    def _update_now_playing(self, track):
        try:
            data = {
                "title": track.get("title", "RADIO DVA"),
                "artist": track.get("artist", "Двойная Волна"),
                "flag": track.get("flag", "🎵"),
                "host": self.host,
                "genre": track.get("genre", "mixed"),
                "listeners": 0,
                "tracks_played": self.segment_count + 1,
                "uptime_hours": int((time.time() - self.start_time) / 3600),
                "status": "broadcasting",
            }
            with open(NP_FILE, 'w') as f:
                json.dump(data, f, ensure_ascii=False)
        except:
            pass


def start_broadcaster():
    """Start the file broadcaster in a background thread."""
    t = threading.Thread(target=_run_broadcaster, daemon=True)
    t.start()
    return t

def _run_broadcaster():
    bc = FileBroadcaster()
    bc.run()
