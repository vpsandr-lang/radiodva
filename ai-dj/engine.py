#!/usr/bin/env python3
"""
RADIO DVA AI — Main Broadcast Engine
Orchestrates the full AI radio experience:
1. Music scheduler picks 50/50 tracks
2. Script generator creates DJ dialogue
3. TTS converts to voice
4. Mixer combines voice + music
5. Streams to Icecast continuously
"""
import sys, os, time, json, signal, threading, random
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))
from music import MusicScheduler, TRACKS
from scripts import ScriptGenerator
from tts import TTSGenerator
from mixer import AudioMixer

class RadioEngine:
    """AI Radio Engine — runs 24/7 autonomous broadcast."""

    def __init__(self):
        print("🎧 RADIO DVA AI Engine initializing...")
        self.music = MusicScheduler()
        self.scripts = ScriptGenerator(dj_name="Алекс")
        self.tts = TTSGenerator()
        self.mixer = AudioMixer()
        
        self.current_track = None
        self.host = "Алекс"  # Alternating hosts
        self.running = True
        self.segment_count = 0
        
        # State for API
        self.state = {
            "current_track": TRACKS[0],
            "next_track": TRACKS[1],
            "host": "Алекс",
            "status": "starting",
            "listeners": 0,
            "uptime": 0,
        }
        
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGTERM, self._stop)
        
        print("✅ Engine ready!")

    def _stop(self, *args):
        print("\n⏹️  Engine stopping...")
        self.running = False

    def generate_segment(self):
        """Generate one broadcast segment (intro + music + outro)."""
        # Switch host every 3 segments
        if self.segment_count > 0 and self.segment_count % 3 == 0:
            self.host = "Лина" if self.host == "Алекс" else "Алекс"
            self.scripts.switch_dj(self.host)
            print(f"🎙️ Switch host → {self.host}")

        # Pick track
        track = self.music.next_track()
        next_track = self.music.current_playlist[0] if self.music.current_playlist else track
        
        print(f"🎵 [{self.host}] {track['flag']} {track['title']} — {track['artist']}")

        # Generate script
        hour = time.localtime().tm_hour
        intro_text, outro_text = self.scripts.generate_show_segment(track, next_track, hour)
        
        print(f"  📝 Intro: {intro_text[:80]}...")
        print(f"  📝 Outro: {outro_text[:80]}...")

        # Generate voice
        intro_path = self.tts.generate(intro_text, self.host, f"intro_{self.segment_count}.wav")
        outro_path = self.tts.generate(outro_text, self.host, f"outro_{self.segment_count}.wav")
        
        if intro_path:
            print(f"  🎤 Voice intro: {self.tts.get_audio_duration(intro_path):.1f}s")
        if outro_path:
            print(f"  🎤 Voice outro: {self.tts.get_audio_duration(outro_path):.1f}s")

        # Generate or get music
        style = "rus" if track["flag"] == "🇷🇺" else "world"
        music_path = self.mixer.create_generated_music(style, duration=10)
        
        # Mix
        segment_path = self.mixer.create_broadcast_segment(
            music_wav=music_path,
            voice_intro_wav=intro_path,
            voice_outro_wav=outro_path
        )
        
        # Convert to MP3
        mp3_path = self.mixer.wav_to_mp3(segment_path)
        
        # Update state
        self.state["current_track"] = track
        self.state["next_track"] = next_track
        self.state["host"] = self.host
        self.state["status"] = "broadcasting"
        self.segment_count += 1
        
        return mp3_path

    def run(self):
        """Main loop — continuous broadcast."""
        print("\n🔴 RADIO DVA AI — Broadcast started!")
        print("=" * 50)
        
        start_time = time.time()
        
        while self.running:
            try:
                # Generate segment
                mp3_path = self.generate_segment()
                
                # Read MP3 data
                with open(mp3_path, 'rb') as f:
                    mp3_data = f.read()
                
                # Stream to Icecast
                if os.path.getsize(mp3_path) > 1000:
                    self._stream_to_icecast(mp3_data)
                
                self.state["uptime"] = int(time.time() - start_time)
                
                # Brief pause between segments (simulates live feel)
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"⚠️ Engine error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)

    def _stream_to_icecast(self, mp3_data):
        """Send MP3 data to Icecast."""
        import http.client, base64
        try:
            conn = http.client.HTTPConnection("localhost", 8888, timeout=30)
            auth = base64.b64encode(b"source:hackme").decode()
            headers = {
                "Content-Type": "audio/mpeg",
                "Content-Length": str(len(mp3_data)),
                "Authorization": f"Basic {auth}",
                "ice-name": "RADIO DVA AI",
                "ice-genre": "Mixed",
                "ice-public": "1",
                "ice-bitrate": "128",
                "ice-description": "AI-powered radio: 50/50 Russia and World",
            }
            conn.request("PUT", "/radio.mp3", body=mp3_data, headers=headers)
            resp = conn.getresponse()
            resp.read()
            print(f"  📡 Stream: HTTP {resp.status}")
            conn.close()
        except Exception as e:
            print(f"  ⚠️ Stream error: {e}")

def main():
    engine = RadioEngine()
    engine.run()

if __name__ == "__main__":
    main()
