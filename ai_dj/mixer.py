"""RADIO DVA AI — Real Audio Mixer for MP3/WAV tracks."""
import os, wave, struct, math, hashlib, subprocess, random, array
from pathlib import Path

SR = 44100


class AudioMixer:
    def __init__(self):
        self.dir = Path("/root/Radio/ai_dj/tracks")
        self.dir.mkdir(parents=True, exist_ok=True)

    def get_music(self, style):
        """Fallback: get a pre-generated music file for a style."""
        files = sorted(self.dir.glob(f"pre_{style}_*.mp3"))
        if not files:
            files = sorted(self.dir.glob(f"pre_{style}_*.wav"))
        if files:
            return str(random.choice(files))
        return self._gen_emergency()

    def _gen_emergency(self):
        """Generate emergency tone when no music available."""
        sr, dur = SR, 3
        path = str(self.dir / "emergency.wav")
        with wave.open(path, 'w') as wf:
            wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr)
            for i in range(sr * dur):
                t = i / sr
                v = int(math.sin(2 * math.pi * 220 * t) * 5000)
                wf.writeframes(struct.pack('<hh', v, v))
        return path

    def _load_audio_to_floats(self, path):
        """Load any audio file (mp3/wav) into list of floats (stereo)."""
        if not path or not os.path.exists(path):
            return 0, []

        path_str = str(path)
        
        # Convert to WAV first if MP3
        if path_str.endswith('.mp3'):
            wav_path = path_str.replace('.mp3', '_conv.wav')
            try:
                subprocess.run([
                    'ffmpeg', '-y', '-i', path_str,
                    '-ac', '2', '-ar', str(SR),
                    '-sample_fmt', 's16', wav_path
                ], capture_output=True, timeout=60)
                if os.path.exists(wav_path) and os.path.getsize(wav_path) > 100:
                    path_str = wav_path
                else:
                    return 0, []
            except:
                return 0, []

        try:
            with wave.open(path_str, 'r') as wf:
                n_channels = wf.getnchannels()
                sr = wf.getframerate()
                frames = wf.getnframes()
                raw = wf.readframes(frames)

            data = array.array('h', raw)
            floats = [max(-1.0, min(1.0, d / 32768.0)) for d in data]

            # If mono, duplicate to stereo
            if n_channels == 1:
                stereo = []
                for s in floats:
                    stereo.extend([s, s])
                floats = stereo

            # Clean up temp file
            if '_conv.wav' in path_str and os.path.exists(path_str):
                try: os.remove(path_str)
                except: pass

            return frames, floats
        except Exception as e:
            if '_conv.wav' in path_str and os.path.exists(path_str):
                try: os.remove(path_str)
                except: pass
            return 0, []

    def create_broadcast_segment(self, music_wav, voice_intro_wav=None, voice_outro_wav=None):
        """Mix voice intro + music + voice outro into one WAV."""
        music_frames, music = self._load_audio_to_floats(music_wav)
        intro_frames, intro = self._load_audio_to_floats(voice_intro_wav)
        outro_frames, outro = self._load_audio_to_floats(voice_outro_wav)

        if music_frames == 0:
            print("  ⚠️ No music loaded, using silence", flush=True)
            music = [0.0] * (SR * 2 * 2)  # 2 sec silence
            music_frames = SR * 2

        gap = int(SR * 0.3)  # 300ms gap
        total = intro_frames + gap + music_frames + gap + outro_frames
        out = [0.0] * (total * 2)
        pos = 0

        # Intro
        for i in range(intro_frames):
            if pos + i >= total: break
            fade = 1.0 if intro_frames - i >= 200 else (intro_frames - i) / 200
            out[(pos + i) * 2] += intro[i * 2] * fade * 0.90
            out[(pos + i) * 2 + 1] += intro[i * 2 + 1] * fade * 0.90
        pos += intro_frames + gap

        # Music with crossfade
        fade_len = min(int(SR * 0.1), music_frames // 2)
        for i in range(music_frames):
            if pos + i >= total: break
            fade = 1.0
            if i < fade_len: fade = i / fade_len
            if music_frames - i < fade_len: fade = min(fade, (music_frames - i) / fade_len)
            out[(pos + i) * 2] += music[i * 2] * 0.7 * fade
            out[(pos + i) * 2 + 1] += music[i * 2 + 1] * 0.7 * fade
        pos += music_frames + gap

        # Outro
        for i in range(outro_frames):
            if pos + i >= total: break
            fade = i / fade_len if i < fade_len else 1.0
            out[(pos + i) * 2] += outro[i * 2] * fade * 0.90
            out[(pos + i) * 2 + 1] += outro[i * 2 + 1] * fade * 0.90

        # Normalize
        peak = max(max(abs(s) for s in out), 0.001)
        gain = min(1.0, 0.95 / peak)

        # Write WAV
        h = hashlib.md5(
            f"{music_wav}:{voice_intro_wav}:{voice_outro_wav}:{random.random()}".encode()
        ).hexdigest()[:10]
        wav_path = f"/tmp/radio/segments/seg_{h}.wav"
        os.makedirs("/tmp/radio/segments", exist_ok=True)

        with wave.open(wav_path, 'w') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            for i in range(total):
                l = max(-32768, min(32767, int(out[i * 2] * gain * 32767)))
                r = max(-32768, min(32767, int(out[i * 2 + 1] * gain * 32767)))
                wf.writeframes(struct.pack('<hh', l, r))

        # Apply loudnorm
        try:
            mastered = wav_path.replace('.wav', '_m.wav')
            subprocess.run([
                'ffmpeg', '-y', '-i', wav_path,
                '-af', 'loudnorm=I=-14:LRA=10:TP=-2',
                '-ac', '2', '-ar', '44100', '-sample_fmt', 's16', mastered
            ], capture_output=True, timeout=30)
            if os.path.exists(mastered) and os.path.getsize(mastered) > 1000:
                os.replace(mastered, wav_path)
        except:
            pass

        return wav_path

    def wav_to_mp3(self, wav_path):
        """Convert WAV to MP3."""
        if not wav_path or not os.path.exists(wav_path):
            return None
        mp3 = wav_path.replace('.wav', '.mp3')
        try:
            subprocess.run([
                'lame', '--quiet', '-h', '-b', '128', wav_path, mp3
            ], capture_output=True, timeout=60)
            if os.path.exists(mp3) and os.path.getsize(mp3) > 100:
                try: os.remove(wav_path)
                except: pass
                return mp3
        except:
            pass
        return wav_path
