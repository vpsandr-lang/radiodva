"""RADIO DVA — AI DJ Broadcast Engine (background thread).

Generates continuous audio segments with DJ banter, music, and voiceovers.
Writes directly to the StreamBuffer for HTTP streaming clients.
"""

import sys
import os
import time
import json
import random
import wave
import struct
import math
import threading
import subprocess
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from ai_dj.music import MusicScheduler, TRACKS
from ai_dj.scripts import ScriptGenerator
from ai_dj.tts import TTSGenerator
from ai_dj.mixer import AudioMixer
from api.stream_buffer import STREAM

# Ensure /tmp/radio exists
os.makedirs("/tmp/radio", exist_ok=True)

# State file for API
NP_FILE = os.path.join(os.path.dirname(__file__), "now-playing.json")
MESSAGES_FILE = os.path.join(os.path.dirname(__file__), "messages.json")


class AIDJBroadcaster(threading.Thread):
    """Background thread that runs the AI DJ broadcast engine."""

    def __init__(self):
        super().__init__(daemon=True)
        self.name = "AI-DJ-Broadcaster"
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
        print("🎧 AI DJ Broadcaster started", flush=True)
        time.sleep(2)  # Wait for server to be ready

        # First, check if we have pre-generated content to seed the buffer
        self._seed_buffer()

        while self.running:
            try:
                self._generate_segment()
            except Exception as e:
                print(f"⚠️ DJ error: {e}", flush=True)
                import traceback
                traceback.print_exc()
                time.sleep(5)

    def _seed_buffer(self):
        """Seed the stream buffer with pre-generated audio."""
        candidates = [
            "/tmp/radio/playlist_full.mp3",
            "/tmp/radio/playlist_loop.mp3",
            "/tmp/radio/playlist.mp3",
            "/root/Radio/ai_dj/tracks/playlist_full.mp3",
            "/root/Radio/ai_dj/tracks/playlist.mp3",
            "/tmp/radio/live.ogg",
        ]
        for path in candidates:
            if os.path.exists(path) and os.path.getsize(path) > 100000:
                print(f"📀 Seeding buffer from {path} ({os.path.getsize(path)//1024}KB)", flush=True)
                with open(path, 'rb') as f:
                    data = f.read()
                # Split into chunks for the buffer
                chunk_size = 32768
                for i in range(0, len(data), chunk_size):
                    STREAM.append(data[i:i+chunk_size])
                STREAM.update_metadata(status="broadcasting", title="Загрузка...", artist="RADIO DVA")
                return

        # If no pre-generated content, generate a simple tone
        print("⚡ No pre-generated audio found, generating test tone", flush=True)
        self._generate_test_tone()

    def _generate_test_tone(self):
        """Generate a simple test tone as fallback."""
        sr = 44100
        duration = 10
        samples = []
        for i in range(sr * duration):
            t = i / sr
            # A smooth pad chord
            val = (math.sin(2 * math.pi * 220 * t) * 0.1 +
                   math.sin(2 * math.pi * 277.18 * t) * 0.08 +
                   math.sin(2 * math.pi * 329.63 * t) * 0.06)
            fade = min(t / 0.1, 1.0, (duration - t) / 0.1)
            val *= fade * 0.5
            samples.append(max(-1, min(1, val)))

        wav_path = "/tmp/radio/seed_tone.wav"
        with wave.open(wav_path, 'w') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            for s in samples:
                si = max(-32768, min(32767, int(s * 32767)))
                wf.writeframes(struct.pack('<hh', si, si))

        mp3_path = "/tmp/radio/seed_tone.mp3"
        try:
            subprocess.run(['lame', '--quiet', '-b', '64', wav_path, mp3_path],
                          capture_output=True, timeout=30)
            if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
                with open(mp3_path, 'rb') as f:
                    data = f.read()
                chunk_size = 32768
                for i in range(0, len(data), chunk_size):
                    STREAM.append(data[i:i+chunk_size])
        except:
            pass

    def _generate_segment(self):
        """Generate one broadcast segment with DJ intro + music + outro."""
        # Switch host every 3 segments
        if self.segment_count > 0 and self.segment_count % 3 == 0:
            self.host = "Лина" if self.host == "Алекс" else "Алекс"
            self.scripts.switch_dj(self.host)

        # Pick track
        track = self.music.next_track()
        flag = track.get("flag", "🌍")
        title = track.get("title", "Unknown")
        artist = track.get("artist", "Unknown")

        ts = time.strftime('%H:%M:%S')
        print(f"[{ts}] #{self.segment_count} {flag} {title} — {artist} [{self.host}]", flush=True)

        # Generate script
        hour = time.localtime().tm_hour
        intro_text, outro_text = self.scripts.generate_show_segment(track, None, hour)

        # Generate voiceovers
        intro_path = self.tts.generate(intro_text, self.host, f"seg_{self.segment_count}_i.wav")
        outro_path = self.tts.generate(outro_text, self.host, f"seg_{self.segment_count}_o.wav")

        # Get music track
        style = "rus" if flag == "🇷🇺" else "world"
        music_path = self.mixer.get_music(style)

        # Create broadcast segment (intro + music + outro)
        segment_wav = self.mixer.create_broadcast_segment(
            music_wav=music_path,
            voice_intro_wav=intro_path,
            voice_outro_wav=outro_path
        )

        # Convert to MP3
        mp3_path = self.mixer.wav_to_mp3(segment_wav)

        # Read and broadcast
        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
            with open(mp3_path, 'rb') as f:
                mp3_data = f.read()

            # Split into chunks for smoother streaming
            chunk_size = 16384
            for i in range(0, len(mp3_data), chunk_size):
                STREAM.append(mp3_data[i:i+chunk_size])
                time.sleep(0.05)  # Small delay for smooth delivery

            size_kb = os.path.getsize(mp3_path) // 1024
            print(f"  📡 Broadcast: {size_kb}KB | Listeners: {STREAM.listener_count()}", flush=True)

        # Update state
        STREAM.update_metadata(
            title=title,
            artist=artist,
            flag=flag,
            host=self.host,
            intro=intro_text[:100],
            status="broadcasting",
            tracks_played=self.segment_count + 1,
        )

        # Also write to now-playing.json for API
        self._update_now_playing(track)

        self.segment_count += 1

        # Brief pause for natural pacing (voiceover adds ~5-10s already)
        time.sleep(random.uniform(0.3, 1.0))

    def _update_now_playing(self, track):
        """Update now-playing JSON file for API."""
        try:
            data = {
                "title": track.get("title", "RADIO DVA"),
                "artist": track.get("artist", "Двойная Волна"),
                "flag": track.get("flag", "🎵"),
                "host": self.host,
                "intro": STREAM.get_metadata().get("intro", ""),
                "listeners": STREAM.listener_count(),
                "tracks_played": self.segment_count + 1,
                "uptime_hours": int((time.time() - self.start_time) / 3600),
            }
            with open(NP_FILE, 'w') as f:
                json.dump(data, f, ensure_ascii=False)
        except:
            pass


def start_broadcaster():
    """Start the AI DJ broadcaster thread."""
    thread = AIDJBroadcaster()
    thread.start()
    return thread
