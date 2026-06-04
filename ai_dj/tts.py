"""RADIO DVA AI — TTS via edge-tts with natural voice settings."""
import os, subprocess, hashlib, random
from pathlib import Path
import asyncio
import edge_tts

CACHE_DIR = Path(__file__).parent / "tts_cache"

class TTSGenerator:
    def __init__(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.voice_map = {
            "Алекс": "ru-RU-DmitryNeural",
            "Лина": "ru-RU-SvetlanaNeural"
        }

    def generate(self, text, dj_name="Алекс"):
        if not text or not text.strip():
            return None
        voice = self.voice_map.get(dj_name, "ru-RU-DmitryNeural")
        rate = random.choice(["+0%", "+3%", "+5%", "+8%"])
        h = hashlib.md5(f"{text}:{dj_name}:{rate}".encode()).hexdigest()
        wav = CACHE_DIR / f"{h}.wav"
        if wav.exists() and os.path.getsize(wav) > 100:
            return str(wav)
        try:
            tmp = CACHE_DIR / f"tmp_{h}.mp3"
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                edge_tts.Communicate(text, voice, rate=rate).save(str(tmp))
            )
            loop.close()
            if tmp.exists() and os.path.getsize(tmp) > 100:
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(tmp),
                    "-acodec", "pcm_s16le", "-ac", "1", "-ar", "22050",
                    str(wav)
                ], capture_output=True, timeout=15)
                try: os.remove(str(tmp))
                except: pass
                if wav.exists() and os.path.getsize(wav) > 100:
                    return str(wav)
        except: pass
        return None
