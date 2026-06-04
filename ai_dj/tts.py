"""RADIO DVA AI — Realistic TTS via ElevenLabs with edge-tts fallback.
Uses ElevenLabs API for natural human-like voices.
"""
import os, subprocess, hashlib, json, time, requests
from pathlib import Path

# ElevenLabs API key from user
ELEVENLABS_API_KEY = "1cbb92a8-d956-43e0-828c-09429ea3e2d8"
ELEVENLABS_VOICES = {
    "Алекс": "ikEInbR5g4UcVjLfr5wD",  # Russian male voice (Antoni)
    "Лина": "pqHf0Nc4XH7JT1R0PZQn",   # Russian female voice (Rachel)
}
ELEVENLABS_MODEL = "eleven_multilingual_v2"

class TTSGenerator:
    def __init__(self):
        self.cache_dir = Path("/root/Radio/ai_dj/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._last_request = 0

    def generate(self, text, dj_name="Алекс", filename=None):
        if not text or not text.strip():
            return None
        
        h = hashlib.md5(f"{text}:{dj_name}:el_v2".encode()).hexdigest()
        cached = self.cache_dir / f"{h}.wav"
        
        # Return cached version if available
        if cached.exists() and os.path.getsize(cached) > 100:
            return str(cached)
        
        # Try ElevenLabs first
        wav_path = self._elevenlabs_tts(text, dj_name, h)
        if wav_path:
            return wav_path
        
        # Fallback to edge-tts
        wav_path = self._edge_tts_fallback(text, dj_name, h)
        return wav_path

    def _elevenlabs_tts(self, text, dj_name, hash_id):
        """Generate speech using ElevenLabs API."""
        voice_id = ELEVENLABS_VOICES.get(dj_name, "ikEInbR5g4UcVjLfr5wD")
        
        # Rate limit: max 5 requests per second
        now = time.time()
        if now - self._last_request < 0.2:
            time.sleep(0.2)
        self._last_request = time.time()
        
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            data = {
                "text": text,
                "model_id": ELEVENLABS_MODEL,
                "voice_settings": {
                    "stability": 0.35,
                    "similarity_boost": 0.80,
                    "style": 0.20,
                    "speak_rate": 1.0
                }
            }
            
            resp = requests.post(url, json=data, headers=headers, timeout=30)
            if resp.status_code == 200:
                mp3_path = self.cache_dir / f"el_{hash_id}.mp3"
                with open(mp3_path, 'wb') as f:
                    f.write(resp.content)
                
                if mp3_path.exists() and os.path.getsize(mp3_path) > 100:
                    # Convert MP3 to WAV for processing
                    wav_path = self.cache_dir / f"{hash_id}.wav"
                    subprocess.run([
                        "ffmpeg", "-y", "-i", str(mp3_path),
                        "-ac", "1", "-ar", "22050",
                        "-sample_fmt", "s16",
                        str(wav_path)
                    ], capture_output=True, timeout=30)
                    
                    try: os.remove(str(mp3_path))
                    except: pass
                    
                    if wav_path.exists() and os.path.getsize(wav_path) > 100:
                        print(f"  🎙️ ElevenLabs [{dj_name}]: {len(text)} chars", flush=True)
                        return str(wav_path)
            else:
                print(f"  ⚠️ ElevenLabs error {resp.status_code}: {resp.text[:100]}", flush=True)
        except Exception as e:
            print(f"  ⚠️ ElevenLabs fail: {e}", flush=True)
        
        return None

    def _edge_tts_fallback(self, text, dj_name, hash_id):
        """Fallback TTS using edge-tts."""
        import asyncio
        import edge_tts
        
        voices = {"Алекс": "ru-RU-DmitryNeural", "Лина": "ru-RU-SvetlanaNeural"}
        voice = voices.get(dj_name, "ru-RU-DmitryNeural")
        
        try:
            # Use a reasonable speed
            tmp_mp3 = self.cache_dir / f"edge_{hash_id}.mp3"
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                edge_tts.Communicate(text, voice, rate="+20%").save(str(tmp_mp3))
            )
            loop.close()
            
            if not tmp_mp3.exists() or os.path.getsize(tmp_mp3) < 100:
                return None
            
            wav_path = self.cache_dir / f"{hash_id}.wav"
            subprocess.run([
                "ffmpeg", "-y", "-i", str(tmp_mp3),
                "-ac", "1", "-ar", "22050",
                "-sample_fmt", "s16",
                str(wav_path)
            ], capture_output=True, timeout=30)
            
            try: os.remove(str(tmp_mp3))
            except: pass
            
            if wav_path.exists() and os.path.getsize(wav_path) > 100:
                print(f"  🎙️ edge-tts [{dj_name}]: {len(text)} chars", flush=True)
                return str(wav_path)
        except:
            pass
        
        return None
