FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PORT=5050

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip lame vorbis-tools curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip3 install --break-system-packages --no-cache-dir edge-tts

# Copy app
WORKDIR /app
COPY . .

# Generate audio assets if possible
RUN python3 -c "from ai_dj.mixer import AudioMixer; m=AudioMixer(); print('Mixer OK')" 2>/dev/null || true
RUN python3 -c "from ai_dj.music import TRACKS; print(f'Track DB: {len(TRACKS)} tracks')"

# Run API server with AI DJ broadcaster
CMD python3 -u run.py
