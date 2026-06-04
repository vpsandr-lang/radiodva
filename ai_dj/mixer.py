"""RADIO DVA AI — FFmpeg-based Mixer (zero memory overhead)."""
import os, subprocess, hashlib, random
from pathlib import Path

class AudioMixer:
    def __init__(self):
        self.work = "/tmp/radio/mixer"
        os.makedirs(self.work, exist_ok=True)

    def get_music(self, style):
        return None

    def create_broadcast_segment(self, music_wav, voice_intro_wav=None, voice_outro_wav=None):
        """Mix intro + music + outro using ffmpeg (no Python memory)."""
        h = hashlib.md5(f"{music_wav}:{voice_intro_wav}:{voice_outro_wav}:{random.random()}".encode()).hexdigest()[:10]
        out = f"/tmp/radio/segments/seg_{h}"
        os.makedirs("/tmp/radio/segments", exist_ok=True)

        # Build ffmpeg filter for mixing intro + music + outro
        # Use amix filter to combine up to 3 audio streams
        
        inputs = []
        filter_parts = []
        stream_idx = 0
        
        # Input files that actually exist
        files = []
        if voice_intro_wav and os.path.exists(voice_intro_wav):
            files.append(("intro", voice_intro_wav))
        if music_wav and os.path.exists(music_wav):
            files.append(("music", music_wav))
        if voice_outro_wav and os.path.exists(voice_outro_wav):
            files.append(("outro", voice_outro_wav))
        
        if not files:
            # Generate silence
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-t", "10", "-acodec", "pcm_s16le",
                f"{out}.wav"
            ], capture_output=True, timeout=30)
            return f"{out}.wav"
        
        # Build filter graph
        input_parts = []
        for name, path in files:
            input_parts.extend(["-i", path])
        
        # amix: mix all inputs
        nb_inputs = len(files)
        filter_str = f"amix=inputs={nb_inputs}:duration=first:dropout_transition=2"
        
        # Volume adjustments
        # Intro/outro: 0.9, music: 0.65
        vol_parts = []
        for i, (name, _) in enumerate(files):
            vol = "0.65" if name == "music" else "0.85"
            vol_parts.append(f"[{i}:a]volume={vol}[a{i}]")
        
        vol_filter = ";".join(vol_parts)
        mix_inputs = "".join(f"[a{i}]" for i in range(nb_inputs))
        full_filter = f"{vol_filter};{mix_inputs}{filter_str}[out]"
        
        try:
            cmd = (["ffmpeg", "-y"] + input_parts + [
                "-filter_complex", full_filter,
                "-map", "[out]",
                "-ac", "2", "-ar", "44100",
                "-sample_fmt", "s16",
                f"{out}.wav"
            ])
            subprocess.run(cmd, capture_output=True, timeout=120)
        except subprocess.TimeoutExpired:
            pass
        
        if os.path.exists(f"{out}.wav") and os.path.getsize(f"{out}.wav") > 100:
            return f"{out}.wav"
        return None

    def wav_to_mp3(self, wav_path):
        """Convert WAV to MP3."""
        if not wav_path or not os.path.exists(wav_path):
            return None
        mp3 = wav_path.replace('.wav', '.mp3')
        try:
            subprocess.run([
                'lame', '--quiet', '-h', '-b', '64', wav_path, mp3
            ], capture_output=True, timeout=60)
            if os.path.exists(mp3) and os.path.getsize(mp3) > 100:
                try: os.remove(wav_path)
                except: pass
                return mp3
        except:
            pass
        return wav_path
