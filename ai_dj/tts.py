"""RADIO DVA AI — Real TTS using edge-tts for Russian voices."""
import os, subprocess, tempfile, hashlib, time
from pathlib import Path

class TTSGenerator:
    def __init__(self):
        self.cache_dir = Path("/root/Radio/ai_dj/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.voices = {
            "Алекс": "ru-RU-DmitryNeural",
            "Лина": "ru-RU-SvetlanaNeural",
        }
        # Fast rate: +30% speed, slight pitch up for clarity
        self.rate_map = {
            "Алекс": "+30%",
            "Лина": "+30%",
        }

    def generate(self, text, dj_name="Алекс", filename=None):
        if not text or not text.strip():
            return None
        
        # Cache key
        h = hashlib.md5(f"{text}:{dj_name}".encode()).hexdigest()
        cached = self.cache_dir / f"{h}.wav"
        if cached.exists() and os.path.getsize(cached) > 1000:
            return str(cached)

        voice = self.voices.get(dj_name, "ru-RU-DmitryNeural")
        rate = self.rate_map.get(dj_name, "+30%")

        # Generate TTS via edge-tts
        tmp_mp3 = self.cache_dir / f"tmp_{h}.mp3"
        tmp_wav = self.cache_dir / f"{h}.wav"
        
        try:
            cmd = [
                "edge-tts",
                "--voice", voice,
                "--rate", rate,
                "--text", text,
                "--write-media", str(tmp_mp3),
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=60, text=True)
            if result.returncode != 0:
                print(f"  ⚠️ edge-tts error: {result.stderr[:200]}", flush=True)
                return None
            
            if not tmp_mp3.exists() or os.path.getsize(tmp_mp3) < 100:
                return None

            # Convert MP3 to WAV at 44100Hz mono
            subprocess.run([
                "ffmpeg", "-y", "-i", str(tmp_mp3),
                "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1",
                "-af", "atempo=1.45",
                str(tmp_wav)
            ], capture_output=True, timeout=30)
            
            if tmp_wav.exists() and os.path.getsize(tmp_wav) > 1000:
                # Clean up tmp mp3
                try: os.remove(str(tmp_mp3))
                except: pass
                return str(tmp_wav)
        except subprocess.TimeoutExpired:
            print(f"  ⚠️ edge-tts timeout for text: {text[:50]}", flush=True)
        except Exception as e:
            print(f"  ⚠️ TTS error: {e}", flush=True)
        
        return None

    def get_audio_duration(self, wav_path):
        """Get duration of a WAV file in seconds."""
        try:
            import wave
            with wave.open(wav_path, 'r') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return frames / float(rate) if rate > 0 else 0
        except:
            return 0
