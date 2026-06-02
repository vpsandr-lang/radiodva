FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    icecast2 python3 python3-pip lame vorbis-tools curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip3 install --break-system-packages edge-tts

# Copy app
WORKDIR /app
COPY . .

# Generate audio assets
RUN python3 ai-dj/tts_test.py 2>/dev/null || true
RUN bash -c "cd ai-dj/tracks && for w in ../../tmp/radio/*.ogg; do test -f \"\$w\" && cp \"\$w\" .; done" 2>/dev/null || true

# Icecast config
COPY icecast.xml /etc/icecast2/icecast.xml
RUN sed -i 's/ENABLE=false/ENABLE=true/' /etc/default/icecast2

# Start script
CMD bash -c "\
    su -s /bin/sh -c 'icecast2 -c /etc/icecast2/icecast.xml' nobody & \
    python3 api/server.py & \
    python3 -m http.server 8000 --directory /app & \
    python3 /tmp/radio/simple_live.py & \
    wait \
"
