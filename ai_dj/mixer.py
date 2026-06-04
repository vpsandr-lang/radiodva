"""RADIO DVA AI — Lightweight Audio Mixer (optimized for 1GB RAM)."""
import os, wave, struct, math, hashlib, subprocess, random, array
from pathlib import Path

SR = 44100
TMPDIR = "/tmp/radio/mixer"

class AudioMixer:
    def __init__(self):
        os.makedirs(TMPDIR, exist_ok=True)

    def _load(self, path):
        """Load audio into stereo float array. Keeps it simple."""
        if not path or not os.path.exists(path):
            return 0, []
        
        path_str = str(path)
        
        # Convert to WAV if needed
        if path_str.endswith('.mp3'):
            wav_path = os.path.join(TMPDIR, f"c_{hashlib.md5(path_str.encode()).hexdigest()[:8]}.wav")
            if not os.path.exists(wav_path):
                try:
                    subprocess.run([
                        'ffmpeg', '-y', '-i', path_str,
                        '-ac', '2', '-ar', str(SR),
                        '-sample_fmt', 's16', wav_path
                    ], capture_output=True, timeout=30)
                except:
                    return 0, []
            if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 100:
                return 0, []
            path_str = wav_path
        else:
            wav_path = path_str
        
        try:
            with wave.open(wav_path, 'r') as wf:
                n, r, f = wf.getnchannels(), wf.getframerate(), wf.getnframes()
                raw = wf.readframes(f)
            data = array.array('h', raw)
            floats = [max(-1.0, min(1.0, d / 32768.0)) for d in data]
            if n == 1:
                stereo = []
                for s in floats:
                    stereo.extend([s, s])
                floats = stereo
            return f, floats
        except:
            return 0, []

    def get_music(self, style):
        """Fallback: synthetic music."""
        return None

    def create_broadcast_segment(self, music_wav, voice_intro_wav=None, voice_outro_wav=None):
        """Mix intro + music + outro. Lightweight - no loudnorm."""
        m_frames, music = self._load(music_wav)
        i_frames, intro = self._load(voice_intro_wav)
        o_frames, outro = self._load(voice_outro_wav)
        
        if m_frames == 0:
            music = [0.0] * (SR * 4 * 2)  # 4 sec silence
            m_frames = SR * 4
        
        gap = int(SR * 0.2)
        total = i_frames + gap + m_frames + gap + o_frames
        out = [0.0] * (total * 2)
        pos = 0
        
        # Intro
        for i in range(i_frames):
            out[(pos + i) * 2] += intro[i * 2] * 0.85
            out[(pos + i) * 2 + 1] += intro[i * 2 + 1] * 0.85
        pos += i_frames + gap
        
        # Music
        fade = min(200, m_frames // 2)
        for i in range(m_frames):
            f = min(1.0, i / fade) * min(1.0, (m_frames - i) / fade) if fade > 0 else 1.0
            out[(pos + i) * 2] += music[i * 2] * 0.65 * f
            out[(pos + i) * 2 + 1] += music[i * 2 + 1] * 0.65 * f
        pos += m_frames + gap
        
        # Outro
        for i in range(o_frames):
            f = min(1.0, i / 200) if 200 > 0 else 1.0
            if pos + i < total:
                out[(pos + i) * 2] += outro[i * 2] * f * 0.85
                out[(pos + i) * 2 + 1] += outro[i * 2 + 1] * f * 0.85
        
        # Normalize
        peak = max(max(abs(s) for s in out), 0.001)
        gain = min(0.98, 0.92 / peak)
        
        h = hashlib.md5(f"{music_wav}:{voice_intro_wav}:{voice_outro_wav}:{random.random()}".encode()).hexdigest()[:10]
        os.makedirs("/tmp/radio/segments", exist_ok=True)
        wav_path = f"/tmp/radio/segments/seg_{h}.wav"
        
        with wave.open(wav_path, 'w') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            for i in range(total):
                l = max(-32768, min(32767, int(out[i * 2] * gain * 32767)))
                r = max(-32768, min(32767, int(out[i * 2 + 1] * gain * 32767)))
                wf.writeframes(struct.pack('<hh', l, r))
        
        return wav_path

    def wav_to_mp3(self, wav_path):
        """Convert WAV to MP3 at 64kbps (lighter)."""
        if not wav_path or not os.path.exists(wav_path):
            return None
        mp3 = wav_path.replace('.wav', '.mp3')
        try:
            subprocess.run([
                'lame', '--quiet', '-h', '-b', '64', wav_path, mp3
            ], capture_output=True, timeout=30)
            if os.path.exists(mp3) and os.path.getsize(mp3) > 100:
                try: os.remove(wav_path)
                except: pass
                return mp3
        except:
            pass
        return wav_path
