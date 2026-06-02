"""RADIO DVA AI — Fast Audio Mixer using pre-generated tracks."""
import os, wave, struct, math, hashlib, subprocess, random
from pathlib import Path

class AudioMixer:
    def __init__(self):
        self.dir = Path("/root/Radio/ai_dj/tracks")
        self.dir.mkdir(parents=True, exist_ok=True)
        self.sr = 44100
    
    def get_music(self, style):
        """Pick a pre-generated track."""
        files = sorted(self.dir.glob(f"pre_{style}_*.wav"))
        if files:
            return str(random.choice(files))
        return self._gen_fallback(style)
    
    def _gen_fallback(self, style):
        path = str(self.dir / f"fallback_{style}.wav")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            return path
        sr, dur = 44100, 5
        key = 220 if style == "rus" else 261
        samples = []
        for i in range(sr * dur):
            t = i / sr
            val = sum(math.sin(2*math.pi*h*t)*0.06 for h in [key, key*1.25, key*1.5])
            val += math.sin(2*math.pi*key*0.5*t)*0.2
            val += math.sin(2*math.pi*200*(t*2%1/0.05))*0.1 if (t*2%1)<0.05 else 0
            val *= min(t/0.3,1,(dur-t)/0.3)*0.4
            val = max(-1,min(1,val))
            samples.append(int(val*32767))
        with wave.open(path,'w') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
            for s in samples:
                wf.writeframes(struct.pack('<hh',s,s))
        return path
    
    def _load(self, path):
        try:
            with wave.open(path) as wf:
                n, r, f = wf.getnchannels(), wf.getframerate(), wf.getnframes()
                raw = wf.readframes(f)
            import array
            data = array.array('h', raw)
            floats = [max(-1,min(1,d/32768.0)) for d in data]
            if n == 1:
                floats = [s for s in floats for _ in range(2)]
            return floats
        except:
            return [0.0]*44100
    
    def create_broadcast_segment(self, music_wav, voice_intro_wav=None, voice_outro_wav=None):
        music = self._load(music_wav) if music_wav and os.path.exists(music_wav) else []
        intro = self._load(voice_intro_wav) if voice_intro_wav and os.path.exists(voice_intro_wav) else []
        outro = self._load(voice_outro_wav) if voice_outro_wav and os.path.exists(voice_outro_wav) else []
        
        gap = int(self.sr * 0.3)
        fade = int(self.sr * 0.2)
        total = len(intro) + gap + len(music) + gap + len(outro)
        if total < 1000: total = int(self.sr * 4)
        
        out = [0.0]*total; pos = 0
        
        # Add intro
        for i,s in enumerate(intro):
            if pos+i >= len(out): break
            f = 1.0 if len(intro)-i >= fade else (len(intro)-i)/fade
            out[pos+i] += s * f * 0.8
        pos += len(intro) + gap
        
        # Add music
        for i,s in enumerate(music):
            if pos+i >= len(out): break
            f = 1.0
            if i < fade: f = i/fade
            if len(music)-i < fade: f = min(f, (len(music)-i)/fade)
            out[pos+i] += s * f * 0.7
        pos += len(music) + gap
        
        # Add outro
        for i,s in enumerate(outro):
            if pos+i >= len(out): break
            f = i/fade if i < fade else 1.0
            out[pos+i] += s * f * 0.8
        
        # Normalize
        peak = max(max(abs(s) for s in out), 0.01)
        gain = min(1.0, 0.92/peak)
        
        h = hashlib.md5(f"{music_wav}{voice_intro_wav}{voice_outro_wav}".encode()).hexdigest()[:10]
        path = str(self.dir / f"seg_{h}.wav")
        
        with wave.open(path, 'w') as wf:
            wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(self.sr)
            for s in out:
                si = max(-32768, min(32767, int(s*gain*32767)))
                wf.writeframes(struct.pack('<hh',si,si))
        return path
    
    def wav_to_mp3(self, wav_path):
        mp3 = wav_path.replace('.wav','.mp3')
        try:
            subprocess.run(['lame','--quiet','-h','-b','128',wav_path,mp3],
                          capture_output=True,timeout=30)
            if os.path.exists(mp3) and os.path.getsize(mp3)>100:
                return mp3
        except: pass
        return wav_path
