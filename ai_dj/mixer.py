"""RADIO DVA AI — Real Audio Mixer using actual MP3 tracks."""
import os, wave, struct, math, hashlib, subprocess, random, tempfile
from pathlib import Path

class AudioMixer:
    def __init__(self):
        self.work_dir = Path("/tmp/radio/mixer")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.sr = 44100

    def get_music(self, track):
        """Get an MP3 file path for a track. Returns path or None."""
        from music import get_track_path
        return get_track_path(track)

    def _load_audio(self, path, target_sr=44100, target_channels=2):
        """Load any audio file into float array [0..1]."""
        if not path or not os.path.exists(path):
            return [0.0] * (target_sr * 2)  # 1 sec silence

        # Normalize path
        path = str(path)
        
        # Convert to WAV first
        tmp_wav = self.work_dir / f"tmp_{hashlib.md5(path.encode()).hexdigest()[:10]}.wav"
        try:
            if not tmp_wav.exists():
                subprocess.run([
                    "ffmpeg", "-y", "-i", path,
                    "-acodec", "pcm_s16le",
                    "-ar", str(target_sr),
                    "-ac", str(target_channels),
                    str(tmp_wav)
                ], capture_output=True, timeout=60)
            
            if tmp_wav.exists() and os.path.getsize(tmp_wav) > 100:
                with wave.open(str(tmp_wav), 'r') as wf:
                    n_channels = wf.getnchannels()
                    sr = wf.getframerate()
                    frames = wf.getnframes()
                    raw = wf.readframes(frames)
                
                import array
                data = array.array('h', raw)
                floats = [max(-1.0, min(1.0, d / 32768.0)) for d in data]
                
                # If mono, duplicate to stereo
                if n_channels == 1:
                    floats = [s for s in floats for _ in range(2)]
                
                return floats
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            print(f"  ⚠️ load_audio error: {e}", flush=True)
        
        return [0.0] * (target_sr * 2)

    def _load_wav(self, path):
        """Load WAV file into float array."""
        return self._load_audio(path)

    def create_broadcast_segment(self, music_path=None, voice_intro_wav=None, voice_outro_wav=None):
        """Mix voice intro + music + voice outro into one WAV."""
        # Load audio
        intro = self._load_wav(voice_intro_wav) if voice_intro_wav else []
        music = self._load_audio(music_path) if music_path else []
        outro = self._load_wav(voice_outro_wav) if voice_outro_wav else []
        
        fade = int(self.sr * 0.3)  # 300ms fade
        gap = int(self.sr * 0.5)   # 500ms gap
        
        total = len(intro) + gap + len(music) + gap + len(outro)
        if total < self.sr * 10:  # Minimum 10 seconds
            total = self.sr * 10
        
        out = [0.0] * total
        pos = 0
        
        # Add intro voice
        for i, s in enumerate(intro):
            if pos + i >= len(out):
                break
            fade_out = 1.0 if len(intro) - i >= fade else (len(intro) - i) / fade
            out[pos + i] += s * fade_out * 0.85
        pos += len(intro) + gap
        
        # Add music (crossfade)
        for i, s in enumerate(music):
            if pos + i >= len(out):
                break
            fade_in = i / fade if i < fade else 1.0
            fade_out = 1.0 if len(music) - i >= fade else (len(music) - i) / fade
            out[pos + i] += s * fade_in * fade_out * 0.75
        pos += len(music) + gap
        
        # Add outro voice
        for i, s in enumerate(outro):
            if pos + i >= len(out):
                break
            fade_in = i / fade if i < fade else 1.0
            out[pos + i] += s * fade_in * 0.85
        
        # Normalize
        peak = max(max(abs(s) for s in out), 0.01)
        gain = min(0.98, 0.92 / peak)
        
        # Write WAV
        h = hashlib.md5(f"{music_path}:{voice_intro_wav}:{voice_outro_wav}".encode()).hexdigest()[:12]
        out_path = str(self.work_dir / f"seg_{h}.wav")
        
        with wave.open(out_path, 'w') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(self.sr)
            for s in out:
                si = max(-32768, min(32767, int(s * gain * 32767)))
                wf.writeframes(struct.pack('<hh', si, si))
        
        return out_path

    def wav_to_mp3(self, wav_path, bitrate=128):
        """Convert WAV to MP3 using lame."""
        mp3_path = wav_path.replace('.wav', '.mp3')
        try:
            subprocess.run([
                'lame', '--quiet', '-h', '-b', str(bitrate),
                wav_path, mp3_path
            ], capture_output=True, timeout=60)
            if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 100:
                return mp3_path
        except:
            pass
        return wav_path
