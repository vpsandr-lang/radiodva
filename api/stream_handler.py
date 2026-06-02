"""Simple file-based MP3 streaming handler."""
import os
import time

STREAM_FILE = "/tmp/radio/current_broadcast.mp3"

def generate_mp3_stream():
    """Generator that yields MP3 data, looping the current file."""
    chunk_size = 16384
    last_mtime = 0
    data = b""
    
    while True:
        try:
            mtime = os.path.getmtime(STREAM_FILE)
            if mtime != last_mtime:
                with open(STREAM_FILE, 'rb') as f:
                    data = f.read()
                last_mtime = mtime
                if data:
                    print(f"Loaded stream file: {len(data)//1024}KB", flush=True)
        except (FileNotFoundError, OSError):
            data = b""
        
        if data:
            pos = 0
            while pos < len(data):
                chunk = data[pos:pos+chunk_size]
                yield chunk
                pos += chunk_size
                time.sleep(len(chunk) / (64000/8))
            time.sleep(0.1)
        else:
            time.sleep(2)
            yield b""
