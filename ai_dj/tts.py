"""RADIO DVA AI — Ultra-light TTS using edge-tts."""
import os, subprocess, hashlib, asyncio
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
        self.voices = {"Алекс": "ru-RU-DmitryNeural", "Лина": "ru-RU-SvetlanaNeural"}

    def generate(self, text, dj_name="Алекс", filename=None):
        if not text or not text.strip():
            return None
        
        voice = self.voices.get(dj_name, "ru-RU-DmitryNeural")
        h = hashlib.md5(f"{text}:{dj_name}:v5".encode()).hexdigest()
        cached = self.cache_dir / f"{h}.wav"
        
        if cached.exists() and os.path.getsize(cached) > 100:
            return str(cached)
        
        tmp_mp3 = self.cache_dir / f"tmp_{h}.mp3"
        
        try:
            loop = _get_loop()
            loop.run_until_complete(
                edge_tts.Communicate(text, voice, rate="+50%").save(str(tmp_mp3))
            )
            
            if not tmp_mp3.exists() or os.path.getsize(tmp_mp3) < 100:
                return None
            
            # Direct MP3->WAV, no filters (fast)
            subprocess.run([
                "ffmpeg", "-y", "-i", str(tmp_mp3),
                "-ac", "1", "-ar", "22050",
                "-sample_fmt", "s16",
                str(cached)
            ], capture_output=True, timeout=30)
            
            try: os.remove(str(tmp_mp3))
            except: pass
            
            if cached.exists() and os.path.getsize(cached) > 100:
                return str(cached)
        except:
            pass
        
        return None
