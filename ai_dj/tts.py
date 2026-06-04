"""RADIO DVA AI — Lightweight TTS using edge-tts.
Optimized for 1GB RAM: minimal ffmpeg processing, fast generation.
"""
import os, subprocess, hashlib, asyncio, tempfile
from pathlib import Path
import edge_tts

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
        h = hashlib.md5(f"{text}:{dj_name}:v4".encode()).hexdigest()
        
        # Check cache
        cached = self.cache_dir / f"{h}.wav"
        if cached.exists() and os.path.getsize(cached) > 100:
            return str(cached)
        
        tmp_mp3 = self.cache_dir / f"tmp_{h}.mp3"
        tmp_wav = self.cache_dir / f"raw_{h}.wav"
        
        try:
            # edge-tts with fast rate
            loop = _get_loop()
            loop.run_until_complete(
                edge_tts.Communicate(text, voice, rate="+50%").save(str(tmp_mp3))
            )
            
            if not tmp_mp3.exists() or os.path.getsize(tmp_mp3) < 100:
                return None
            
            # Lightweight conversion: just atempo, no fancy filters
            subprocess.run([
                "ffmpeg", "-y", "-i", str(tmp_mp3),
                "-af", "atempo=1.8",
                "-ac", "1", "-ar", "22050",
                "-sample_fmt", "s16",
                str(tmp_wav)
            ], capture_output=True, timeout=30)
            
            if tmp_wav.exists() and os.path.getsize(tmp_wav) > 100:
                # Copy to cache
                import shutil
                shutil.copy2(str(tmp_wav), str(cached))
                # Cleanup
                for f in [tmp_mp3, tmp_wav]:
                    try: os.remove(str(f))
                    except: pass
                return str(cached)
            else:
                # Try without atempo
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(tmp_mp3),
                    "-ac", "1", "-ar", "22050",
                    "-sample_fmt", "s16",
                    str(tmp_wav)
                ], capture_output=True, timeout=30)
                if tmp_wav.exists() and os.path.getsize(tmp_wav) > 100:
                    shutil.copy2(str(tmp_wav), str(cached))
                    for f in [tmp_mp3, tmp_wav]:
                        try: os.remove(str(f))
                        except: pass
                    return str(cached)
                
        except Exception as e:
            pass
        
        return None
