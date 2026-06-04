"""RADIO DVA AI — Warm, polite TTS with smile in the voice.
Uses edge-tts with gentle prosody for friendly radio hosts.
"""
import os, subprocess, hashlib, random
from pathlib import Path
import asyncio
import edge_tts

class TTSGenerator:
    def __init__(self):
        self.cache_dir = Path("/root/Radio/ai_dj/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.voice_names = {
            "Алекс": "ru-RU-DmitryNeural",
            "Лина": "ru-RU-SvetlanaNeural"
        }
        # Gentle prosody settings for warm, friendly voice
        self.prosody = {
            "Алекс": {"pitch": "+8Hz", "rate": "+5%", "volume": "+10%"},
            "Лина": {"pitch": "+12Hz", "rate": "+3%", "volume": "+15%"}
        }
        # Natural rate variation
        self.rate_opts = {
            "Алекс": ["+3%", "+5%", "+8%", "+10%"],
            "Лина": ["+0%", "+3%", "+5%", "+8%"]
        }

    def generate(self, text, dj_name="Алекс"):
        if not text or not text.strip():
            return None
        
        # Use plain text with voice and natural rate
        voice = self.voice_names.get(dj_name, "ru-RU-DmitryNeural")
        rate = random.choice(self.rate_opts.get(dj_name, ["+5%"]))
        
        h = hashlib.md5(f"{text}:{dj_name}:{rate}:warm".encode()).hexdigest()
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
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(tmp_mp3),
                    "-ac", "1", "-ar", "22050",
                    "-sample_fmt", "s16",
                    str(cached)
                ], capture_output=True, timeout=30)
                try: os.remove(str(tmp_mp3))
                except: pass
                if cached.exists() and os.path.getsize(cached) > 100:
                    print(f"  🎙️ [{dj_name} @ {rate}]: {len(text)} chars", flush=True)
                    return str(cached)
        except Exception as e:
            print(f"  ⚠️ TTS error: {e}", flush=True)
        
        return None
