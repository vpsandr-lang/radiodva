"""RADIO DVA — Streaming Broadcaster
Generates MP3 segments for sequential streaming.
Fixed: real TTS, real music tracks, proper segment handling.
"""
import sys, os, time, json, random, subprocess, threading, shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from ai_dj.music import MusicScheduler
from ai_dj.scripts import ScriptGenerator
from ai_dj.tts import TTSGenerator
from ai_dj.mixer import AudioMixer

LATEST_SEGMENT = "/tmp/radio/latest_segment.mp3"
SEGMENT_DIR = "/tmp/radio/segments/"
NP_FILE = os.path.join(os.path.dirname(__file__), "now-playing.json")
os.makedirs(SEGMENT_DIR, exist_ok=True)


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
        print("  RADIO DVA — AI Radio", flush=True)
        print("=" * 50, flush=True)
        time.sleep(1)

        while self.running:
            try:
                self._generate_segment()
                time.sleep(0.3)
            except Exception as e:
                print(f"  ❌ Error: {e}", flush=True)
                import traceback
                traceback.print_exc()
                time.sleep(5)

    def _generate_segment(self):
        """Generate one segment: intro -> music -> outro."""
        # Switch host every 3 segments
        if self.segment_count > 0 and self.segment_count % 3 == 0:
            self.host = "Лина" if self.host == "Алекс" else "Алекс"
            self.scripts.switch_dj(self.host)

        track = self.music.next_track()
        flag = track.get("flag", "🎵")
        title = track.get("title", "Unknown")
        artist = track.get("artist", "Unknown")
        ts = time.strftime('%H:%M:%S')

        print(f"[{ts}] #{self.segment_count} {flag} {title} — {artist} [{self.host}]", flush=True)

        # Generate script and voiceovers
        hour = time.localtime().tm_hour
        intro_text, outro_text = self.scripts.generate_show_segment(track, None, hour)

        t0 = time.time()
        intro_path = self.tts.generate(intro_text, self.host)
        outro_path = self.tts.generate(outro_text, self.host)
        tts_time = time.time() - t0

        # Get music file
        music_path = track.get("file_path")
        if not music_path or not os.path.exists(music_path):
            style = track.get("style", "world")
            music_path = self.mixer.get_music(style)
        
        if music_path:
            print(f"  🎵 Music: {os.path.basename(music_path)}", flush=True)

        # Create segment
        segment_wav = self.mixer.create_broadcast_segment(
            music_wav=music_path,
            voice_intro_wav=intro_path,
            voice_outro_wav=outro_path
        )

        # Convert to MP3
        mp3_path = self.mixer.wav_to_mp3(segment_wav)

        if mp3_path and os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
            # Copy to latest
            # Atomic write: copy to temp, then rename
        tmp_seg = LATEST_SEGMENT + '.tmp'
        shutil.copy2(mp3_path, tmp_seg)
        os.replace(tmp_seg, LATEST_SEGMENT)
            
            # Save with segment number
            seg_file = os.path.join(SEGMENT_DIR, f"seg_{self.segment_count:04d}.mp3")
            shutil.copy2(mp3_path, seg_file)
            
            # Keep only last 10 segments
            self._cleanup_old()
            
            size_kb = os.path.getsize(LATEST_SEGMENT) // 1024
            t_total = time.time() - t0
            print(f"  Segment {size_kb}KB | TTS:{tts_time:.1f}s | Total:{t_total:.1f}s", flush=True)
        else:
            print(f"  ⚠️ Segment generation failed", flush=True)

        # Update now-playing
        self._update_now_playing(track)
        self.segment_count += 1

    def _cleanup_old(self, keep=10):
        """Keep only last N segment files."""
        try:
            files = sorted(Path(SEGMENT_DIR).glob("seg_*.mp3"))
            for f in files[:-keep]:
                f.unlink(missing_ok=True)
        except:
            pass

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


_active_broadcaster = None

def start_broadcaster():
    """Start the file broadcaster in a background thread."""
    t = threading.Thread(target=_run_broadcaster, daemon=True)
    t.start()
    return t

def _run_broadcaster():
    global _active_broadcaster
    bc = FileBroadcaster()
    _active_broadcaster = bc
    bc.run()

def get_stream_data():
    """Get the latest segment data."""
    try:
        if os.path.exists(LATEST_SEGMENT):
            with open(LATEST_SEGMENT, 'rb') as f:
                return f.read()
    except:
        pass
    return None
