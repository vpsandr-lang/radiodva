"""RADIO DVA AI — Natural TTS via edge-tts with optimized settings."""
import os, subprocess, hashlib, random
from pathlib import Path
import asyncio
import edge_tts

class TTSGenerator:
    def __init__(self):
        self.cache_dir = Path("/root/Radio/ai_dj/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.voices = {
            "Алекс": "ru-RU-DmitryNeural",
            "Лина": "ru-RU-SvetlanaNeural"
        }

    def _generate_wav(self, text, voice, rate_str):
        """Generate WAV from text using edge-tts."""
        h = hashlib.md5(f"{text}:{voice}:{rate_str}".encode()).hexdigest()
        cached = self.cache_dir / f"{h}.wav"
        if cached.exists() and os.path.getsize(cached) > 100:
            return str(cached)
        
        try:
            tmp_mp3 = self.cache_dir / f"tmp_{h}.mp3"
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                edge_tts.Communicate(text, voice, rate=rate_str).save(str(tmp_mp3))
            )
            loop.close()
            
            if tmp_mp3.exists() and os.path.getsize(tmp_mp3) > 100:
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
        except: pass
        return None

    def generate(self, text, dj_name="Алекс"):
        if not text or not text.strip():
            return None
        
        voice = self.voices.get(dj_name, "ru-RU-DmitryNeural")
        
        # Natural radio pacing
        # Алекс: energetic but natural, Лина: smooth
        rate_options = {
            "Алекс": ["+5%", "+10%", "+8%", "+12%"],
            "Лина": ["+0%", "+5%", "+3%", "+8%"]
        }
        rate = random.choice(rate_options.get(dj_name, ["+10%"]))
        
        wav = self._generate_wav(text, voice, rate)
        if wav:
            print(f"  🎙️ [{dj_name} @ {rate}]: {len(text)} chars", flush=True)
        return wav
