"""RADIO DVA AI — High-quality TTS for natural human voice.
Zero downsampling, CD-quality pipeline with SSML expressiveness.
"""
import os, subprocess, hashlib, random, re
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

    def _build_ssml(self, text, dj_name):
        """Build SSML with expressive prosody for natural speech."""
        voice = self.voice_map.get(dj_name, "ru-RU-DmitryNeural")
        rate = random.choice(self.rate_opts.get(dj_name, ["+5%"]))
        pitch = "+8Hz" if dj_name == "Алекс" else "+12Hz"
        
        # Escape XML special characters
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
        
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="ru-RU">
    <voice name="{voice}">
        <prosody rate="{rate}" pitch="{pitch}" volume="+10%">
            {text}
        </prosody>
    </voice>
</speak>'''
        return ssml, rate

    def generate(self, text, dj_name="Алекс"):
        if not text or not text.strip():
            return None
        
        ssml, rate = self._build_ssml(text, dj_name)
        h = hashlib.md5(f"{text}:{dj_name}:hq:v2".encode()).hexdigest()
        cached = self.cache_dir / f"{h}.wav"
        if cached.exists() and os.path.getsize(cached) > 100:
            return str(cached)
        
        try:
            tmp_mp3 = self.cache_dir / f"tmp_{h}.mp3"
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                edge_tts.Communicate(ssml, voice="", rate="").save(str(tmp_mp3))
            )
            loop.close()
            
            if tmp_mp3.exists() and os.path.getsize(tmp_mp3) > 100:
                # Convert to WAV at FULL quality (44100 Hz, stereo)
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(tmp_mp3),
                    "-acodec", "pcm_s16le", "-ac", "2", "-ar", "44100",
                    str(cached)
                ], capture_output=True, timeout=30)
                try: os.remove(str(tmp_mp3))
                except: pass
                if cached.exists() and os.path.getsize(cached) > 100:
                    print(f"  🎙️ [{dj_name} @ {rate} HQ]: {len(text)} chars", flush=True)
                    return str(cached)
        except Exception as e:
            print(f"  ⚠️ TTS error: {e}", flush=True)
            # Fallback: plain text fallback
            try:
                voice = self.voice_map.get(dj_name, "ru-RU-DmitryNeural")
                fallback_rate = random.choice(self.rate_opts.get(dj_name, ["+5%"]))
                tmp2 = self.cache_dir / f"tmp2_{h}.mp3"
                loop2 = asyncio.new_event_loop()
                asyncio.set_event_loop(loop2)
                loop2.run_until_complete(
                    edge_tts.Communicate(text, voice, rate=fallback_rate).save(str(tmp2))
                )
                loop2.close()
                if tmp2.exists() and os.path.getsize(tmp2) > 100:
                    subprocess.run([
                        "ffmpeg", "-y", "-i", str(tmp2),
                        "-acodec", "pcm_s16le", "-ac", "2", "-ar", "44100",
                        str(cached)
                    ], capture_output=True, timeout=30)
                    try: os.remove(str(tmp2))
                    except: pass
                    if cached.exists() and os.path.getsize(cached) > 100:
                        return str(cached)
            except: pass
        
        return None
