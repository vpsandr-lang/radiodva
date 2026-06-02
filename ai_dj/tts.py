"""RADIO DVA AI — Simple TTS using internal synthesis."""
import os, wave, struct, math, hashlib
from pathlib import Path

class TTSGenerator:
    def __init__(self):
        self.dir = Path("/root/Radio/ai_dj/tracks")
        self.dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, text, dj_name="Алекс", filename=None):
        if not text or not text.strip():
            return None
        if filename is None:
            h = hashlib.md5(text.encode()).hexdigest()[:10]
            filename = f"tts_{h}.wav"
        out = str(self.dir / filename)
        if os.path.exists(out) and os.path.getsize(out) > 100:
            return out
        
        sr = 22050
        dur = min(5.0, max(1.0, len(text) * 0.05))
        base_pitch = 220 if dj_name == "Алекс" else 280  # Male/Female difference
        
        samples = []
        for i in range(int(sr * dur)):
            t = i / sr
            # Speech-like modulation: pitch bends and vibrato
            pitch = base_pitch + math.sin(t * 2.5) * 60 + math.sin(t * 5.3) * 25
            # Formants for richness
            val = (math.sin(2*math.pi*pitch*t) * 0.12 +
                   math.sin(2*math.pi*pitch*1.5*t + math.sin(t*4)*0.3) * 0.06 +
                   math.sin(2*math.pi*pitch*2.1*t) * 0.04 +
                   math.sin(2*math.pi*40*t) * 0.06)  # breath
            # Envelope
            fade = min(t/0.05, 1, (dur-t)/0.05)
            val *= fade * 0.3
            val = max(-1, min(1, val))
            samples.append(int(val * 32767))
        
        with wave.open(out, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(struct.pack('<' + 'h'*len(samples), *samples))
        return out
