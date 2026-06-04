"""RADIO DVA AI — FFmpeg Concatenation Mixer
Concatenates: voice_intro (alone) → music (full) → voice_outro (alone).
No simultaneous mixing — true radio format.
"""
import os, subprocess, hashlib, random
from pathlib import Path

class AudioMixer:
    def __init__(self):
        self.work = "/tmp/radio/mixer"
        os.makedirs(self.work, exist_ok=True)

    def get_music(self, style):
        return None

    def create_broadcast_segment(self, music_wav, voice_intro_wav=None, voice_outro_wav=None):
        """Create a segment by concatenating intro → music → outro sequentially.
        Standard radio format: DJ speaks, song plays, DJ speaks again.
        """
        h = hashlib.md5(f"{music_wav}:{voice_intro_wav}:{voice_outro_wav}:{random.random()}".encode()).hexdigest()[:10]
        out = f"/tmp/radio/segments/seg_{h}"
        os.makedirs("/tmp/radio/segments", exist_ok=True)

        # Build list of valid inputs
        inputs = []
        input_labels = []

        if voice_intro_wav and os.path.exists(voice_intro_wav) and os.path.getsize(voice_intro_wav) > 100:
            inputs.append(voice_intro_wav)
            input_labels.append("intro")

        if music_wav and os.path.exists(music_wav) and os.path.getsize(music_wav) > 100:
            inputs.append(music_wav)
            input_labels.append("music")

        if voice_outro_wav and os.path.exists(voice_outro_wav) and os.path.getsize(voice_outro_wav) > 100:
            inputs.append(voice_outro_wav)
            input_labels.append("outro")

        if not inputs:
            # Generate 10 seconds of silence
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-t", "10", "-acodec", "pcm_s16le",
                f"{out}.wav"
            ], capture_output=True, timeout=30)
            return f"{out}.wav"

        # For single input, just copy it
        if len(inputs) == 1:
            try:
                subprocess.run([
                    "ffmpeg", "-y", "-i", inputs[0],
                    "-acodec", "pcm_s16le", "-ac", "2", "-ar", "44100",
                    f"{out}.wav"
                ], capture_output=True, timeout=30)
                if os.path.exists(f"{out}.wav") and os.path.getsize(f"{out}.wav") > 100:
                    return f"{out}.wav"
            except:
                pass
            return None

        # For multiple inputs, concatenate sequentially
        # Create concat filter: all inputs → concat
        filter_parts = []
        for i in range(len(inputs)):
            filter_parts.append(f"[{i}:a]")
        
        concat_filter = "".join(filter_parts) + f"concat=n={len(inputs)}:v=0:a=1[out]"

        try:
            cmd = ["ffmpeg", "-y"]
            for inp in inputs:
                cmd.extend(["-i", inp])
            cmd.extend([
                "-filter_complex", concat_filter,
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
