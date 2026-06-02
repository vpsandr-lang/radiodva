"""
RADIO DVA — Simple File-Based Broadcaster
Generates MP3 segments and concatenates them into current_broadcast.mp3
"""
import sys
import os
import time
import json
import random
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from ai_dj.music import MusicScheduler
from ai_dj.scripts import ScriptGenerator
from ai_dj.tts import TTSGenerator
from ai_dj.mixer import AudioMixer

STREAM_FILE = "/tmp/radio/current_broadcast.mp3"
SEGMENT_DIR = "/tmp/radio/segments/"
os.makedirs(SEGMENT_DIR, exist_ok=True)

NP_FILE = os.path.join(os.path.dirname(__file__), "now-playing.json")


class FileBroadcaster:
    """Background thread that generates MP3 segments and writes to a file."""

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
        print("AI DJ File Broadcaster started", flush=True)
        time.sleep(3)

        # Generate initial test tone
        self._generate_test_tone()

        # Main loop
        while self.running:
            try:
                self._generate_and_write()
            except Exception as e:
                print(f"Error: {e}", flush=True)
                import traceback
                traceback.print_exc()
                time.sleep(5)

    def _generate_test_tone(self):
        """Generate a test tone as placeholder."""
        import wave, struct, math
        sr = 44100
        duration = 10
        samples = []
        for i in range(sr * duration):
            t = i / sr
            val = (math.sin(2 * math.pi * 220 * t) * 0.1 +
                   math.sin(2 * math.pi * 277.18 * t) * 0.08 +
                   math.sin(2 * math.pi * 329.63 * t) * 0.06)
            fade = min(t / 0.05, 1.0, (duration - t) / 0.05)
            val *= fade * 0.5
            val = max(-1, min(1, val))
            samples.append(int(val * 32767))

        wav_path = "/tmp/radio/seed_tone.wav"
        with wave.open(wav_path, 'w') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            for s in samples:
                wf.writeframes(struct.pack('<hh', s, s))

        mp3_path = "/tmp/radio/seed_tone.mp3"
        try:
            subprocess.run(['lame', '--quiet', '-h', '-b', '64', wav_path, mp3_path],
                          capture_output=True, timeout=30)
            if os.path.exists(mp3_path):
                os.system(f"cp {mp3_path} {STREAM_FILE}")
                print(f"Test tone: {os.path.getsize(STREAM_FILE)//1024}KB", flush=True)
        except:
            pass

    def _generate_and_write(self):
        """Generate one segment and append to stream file."""
        # Switch host every 3 segments
        if self.segment_count > 0 and self.segment_count % 3 == 0:
            self.host = "Лина" if self.host == "Алекс" else "Алекс"
            self.scripts.switch_dj(self.host)

        track = self.music.next_track()
        flag = track.get("flag", "🌍")
        title = track.get("title", "Unknown")
        artist = track.get("artist", "Unknown")
        ts = time.strftime('%H:%M:%S')

        print(f"[{ts}] #{self.segment_count} {flag} {title} — {artist} [{self.host}]", flush=True)

        # Generate script and voiceovers
        hour = time.localtime().tm_hour
        intro_text, outro_text = self.scripts.generate_show_segment(track, None, hour)
        intro_path = self.tts.generate(intro_text, self.host, f"seg_{self.segment_count}_i.wav")
        outro_path = self.tts.generate(outro_text, self.host, f"seg_{self.segment_count}_o.wav")

        # Get music
        style = "rus" if flag == "🇷🇺" else "world"
        music_path = self.mixer.get_music(style)

        # Create segment
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

            # If first segment, overwrite; otherwise append
            mode = 'wb' if self.segment_count == 0 else 'ab'
            with open(STREAM_FILE, mode) as f:
                f.write(mp3_data)

            size_kb = os.path.getsize(STREAM_FILE) // 1024
            print(f"Broadcast: {size_kb}KB total", flush=True)

        # Update now-playing
        self._update_now_playing(track)
        self.segment_count += 1
        time.sleep(random.uniform(0.3, 1.0))

    def _update_now_playing(self, track):
        try:
            data = {
                "title": track.get("title", "RADIO DVA"),
                "artist": track.get("artist", "Двойная Волна"),
                "flag": track.get("flag", "🎵"),
                "host": self.host,
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
    import threading
    t = threading.Thread(target=_run_broadcaster, daemon=True)
    t.start()
    return t

def _run_broadcaster():
    bc = FileBroadcaster()
    bc.run()
