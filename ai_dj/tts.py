"""RADIO DVA AI — TTS with real voice cloning.
Алекс uses real recorded voice clips.
Лина uses edge-tts (fallback).
"""
import os, subprocess, hashlib, random
from pathlib import Path
import asyncio
import edge_tts

VOICE_CLONE_DIR = Path("/root/Radio/ai_dj/voice_clone")

class TTSGenerator:
    def __init__(self):
        self.cache_dir = Path("/root/Radio/ai_dj/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.voice_clips = []
        self._load_clips()

    def _load_clips(self):
        """Load Алекс's real voice clips."""
        clip_dir = VOICE_CLONE_DIR
        if clip_dir.exists():
            for f in sorted(clip_dir.glob("alex_phrase_*.mp3")):
                if f.stat().st_size > 5000:  # min 5KB
                    self.voice_clips.append(str(f))
        print(f"  🎤 Loaded {len(self.voice_clips)} real voice clips for Алекс", flush=True)

    def generate(self, text, dj_name="Алекс"):
        """Generate speech. For Алекс: play real voice clip. For Лина: edge-tts."""
        if not text or not text.strip():
            return None

        if dj_name == "Алекс" and self.voice_clips:
            return self._real_voice()

        # Лина fallback to edge-tts
        return self._edge_tts(text, dj_name)

    def _real_voice(self):
        """Pick a random real voice clip and prepare it."""
        clip = random.choice(self.voice_clips)
        h = hashlib.md5(f"real_v2_{clip}".encode()).hexdigest()
        wav = self.cache_dir / f"{h}.wav"
        if wav.exists() and os.path.getsize(wav) > 100:
            return str(wav)

        # Convert MP3 to WAV for mixing
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", clip,
                "-acodec", "pcm_s16le", "-ac", "1", "-ar", "22050",
                str(wav)
            ], capture_output=True, timeout=15)
            if wav.exists() and os.path.getsize(wav) > 100:
                clip_name = os.path.basename(clip)
                return str(wav)
        except: pass
        return None

    def _edge_tts(self, text, dj_name):
        """Fallback TTS for Лина."""
        voice = "ru-RU-SvetlanaNeural"
        rate = random.choice(["+0%", "+3%", "+5%"])
        h = hashlib.md5(f"{text}:{dj_name}:{rate}".encode()).hexdigest()
        wav = self.cache_dir / f"{h}.wav"
        if wav.exists() and os.path.getsize(wav) > 100:
            return str(wav)

        try:
            tmp = self.cache_dir / f"tmp_{h}.mp3"
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
