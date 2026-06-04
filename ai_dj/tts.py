"""RADIO DVA AI — Real TTS using edge-tts for Russian voices.
Fixed: robust asyncio handling, faster output, better error handling.
"""
import os, subprocess, hashlib, asyncio, tempfile, time
from pathlib import Path
import edge_tts

# Use a global event loop for thread safety
_loop = None
def _get_loop():
    global _loop
    try:
        if _loop is None or _loop.is_closed():
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
        return _loop
    except RuntimeError:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
        return _loop

class TTSGenerator:
    def __init__(self):
        self.cache_dir = Path("/root/Radio/ai_dj/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.voices = {
            "Алекс": "ru-RU-DmitryNeural",
            "Лина": "ru-RU-SvetlanaNeural",
        }

    def generate(self, text, dj_name="Алекс", filename=None):
        if not text or not text.strip():
            return None
        
        voice = self.voices.get(dj_name, "ru-RU-DmitryNeural")
        h = hashlib.md5(f"{text}:{dj_name}:v3".encode()).hexdigest()
        
        # Check cache
        cached = self.cache_dir / f"{h}.wav"
        if cached.exists() and os.path.getsize(cached) > 1000:
            try:
                dur = self._get_duration(str(cached))
                if dur > 0.3:
                    return str(cached)
            except:
                pass
        
        tmp_mp3 = self.cache_dir / f"tmp_{h}.mp3"
        tmp_wav = self.cache_dir / f"raw_{h}.wav"
        
        try:
            # Step 1: edge-tts with fast rate
            loop = _get_loop()
            loop.run_until_complete(
                edge_tts.Communicate(text, voice, rate="+50%").save(str(tmp_mp3))
            )
            
            if not tmp_mp3.exists() or os.path.getsize(tmp_mp3) < 100:
                return None
            
            # Step 2: apply atempo and convert to WAV
            result = subprocess.run([
                "ffmpeg", "-y", "-i", str(tmp_mp3),
                "-af", "atempo=1.6",
                "-ac", "1", "-ar", "44100",
                "-sample_fmt", "s16",
                str(tmp_wav)
            ], capture_output=True, timeout=60)
            
            if result.returncode != 0 or not tmp_wav.exists() or os.path.getsize(tmp_wav) < 100:
                # Try without atempo
                result = subprocess.run([
                    "ffmpeg", "-y", "-i", str(tmp_mp3),
                    "-ac", "1", "-ar", "44100",
                    "-sample_fmt", "s16",
                    str(tmp_wav)
                ], capture_output=True, timeout=60)
                if result.returncode != 0 or not tmp_wav.exists() or os.path.getsize(tmp_wav) < 100:
                    return None
            
            # Copy to cache
            subprocess.run(["cp", str(tmp_wav), str(cached)], capture_output=True)
            
            # Cleanup temp files
            for f in [tmp_mp3, tmp_wav]:
                try: os.remove(str(f))
                except: pass
            
            if cached.exists() and os.path.getsize(cached) > 1000:
                dur = self._get_duration(str(cached))
                wps = len(text.split()) / dur if dur > 0 else 0
                print(f"  🎤 TTS: {dur:.1f}s = {wps:.1f} w/s {self._speed_label(wps)}", flush=True)
                return str(cached)
                
        except subprocess.TimeoutExpired:
            print(f"  ⚠️ TTS timeout", flush=True)
        except Exception as e:
            print(f"  ⚠️ TTS err: {e}", flush=True)
            try:
                result = subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", "2", str(cached)
                ], capture_output=True, timeout=30)
                if cached.exists() and os.path.getsize(cached) > 1000:
                    return str(cached)
            except:
                pass
        
        return None

    def _get_duration(self, wav_path):
        try:
            r = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', wav_path
            ], capture_output=True, text=True, timeout=10)
            dur = float(r.stdout.strip() or 0)
            return dur
        except:
            return 0

    def _speed_label(self, wps):
        if wps >= 3.5: return "🚀"
        if wps >= 2.8: return "⚡"
        if wps >= 2.0: return "👍"
        return "🐢"
