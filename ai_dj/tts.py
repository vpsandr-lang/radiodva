"""RADIO DVA AI — High-quality TTS for natural human voice.
CD-quality pipeline, no downsampling, expressive SSML.
"""
import os, subprocess, hashlib, random
from pathlib import Path
import asyncio
import edge_tts

class TTSGenerator:
    def __init__(self):
        self.cache_dir = Path("/root/Radio/ai_dj/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.voice_map = {
            "Алекс": "ru-RU-DmitryNeural",
            "Лина": "ru-RU-SvetlanaNeural"
        }
        self.rate_opts = {
            "Алекс": ["+3%", "+5%", "+8%"],
            "Лина": ["+0%", "+3%", "+5%"]
        }

    def generate(self, text, dj_name="Алекс"):
        if not text or not text.strip():
            return None
        
        voice = self.voice_map.get(dj_name, "ru-RU-DmitryNeural")
        rate = random.choice(self.rate_opts.get(dj_name, ["+5%"]))
        
        h = hashlib.md5(f"{text}:{dj_name}:hq:v3:{rate}".encode()).hexdigest()
        cached = self.cache_dir / f"{h}.wav"
        if cached.exists() and os.path.getsize(cached) > 100:
            return str(cached)
        
        try:
            tmp_mp3 = self.cache_dir / f"tmp_{h}.mp3"
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                edge_tts.Communicate(text, voice, rate=rate).save(str(tmp_mp3))
            )
            loop.close()
            
            if tmp_mp3.exists() and os.path.getsize(tmp_mp3) > 100:
                # CD-quality: 44100 Hz stereo for natural voice
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(tmp_mp3),
                    "-acodec", "pcm_s16le", "-ac", "2", "-ar", "44100",
                    str(cached)
                ], capture_output=True, timeout=30)
                try: os.remove(str(tmp_mp3))
                except: pass
                if cached.exists() and os.path.getsize(cached) > 100:
                    print(f"  🎙️ [{dj_name} @ {rate}]: {len(text)} chars", flush=True)
                    return str(cached)
        except Exception as e:
            print(f"  ⚠️ TTS: {e}", flush=True)
        
        return None
