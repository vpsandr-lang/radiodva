#!/usr/bin/env python3
"""RADIO DVA AI — 24/7 Resilient Broadcast Engine."""
import sys, os, time, json, random, socket, base64, traceback
sys.path.insert(0, os.path.dirname(__file__))
from music import MusicScheduler
from scripts import ScriptGenerator
from tts import TTSGenerator
from mixer import AudioMixer

def stream_mp3(mp3_data):
    """Send MP3 to Icecast (non-blocking)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(("localhost", 8888))
        auth = base64.b64encode(b"source:hackme").decode()
        CRLF = "\r\n"
        req = (
            f"PUT /radio.mp3 HTTP/1.1{CRLF}Host: localhost:8888{CRLF}"
            f"Content-Type: audio/mpeg{CRLF}Content-Length: {len(mp3_data)}{CRLF}"
            f"Authorization: Basic {auth}{CRLF}"
            f"ice-name: RADIO DVA AI{CRLF}ice-genre: Mixed{CRLF}ice-public: 1{CRLF}"
            f"ice-bitrate: 128{CRLF}Connection: close{CRLF}{CRLF}"
        ).encode()
        s.sendall(req + mp3_data)
        try: s.recv(4096)
        except: pass
        s.close()
        return True
    except:
        return False



def main():
    print("=" * 50, flush=True)
    print("  RADIO DVA AI — 24/7 Broadcast", flush=True)
    print("=" * 50, flush=True)
    
    music = MusicScheduler()
    scripts = ScriptGenerator("Алекс")
    tts = TTSGenerator()
    mixer = AudioMixer()
    state_file = "/root/Radio/api/now-playing.json"
    
    host, seg_n, start = "Алекс", 0, time.time()
    
    while True:
        try:
            if seg_n > 0 and seg_n % 3 == 0:
                host = "Лина" if host == "Алекс" else "Алекс"
                scripts.switch_dj(host)
            
            track = music.next_track()
            ts = time.strftime('%H:%M:%S')
            print(f"\n[{ts}] #{seg_n} {track['flag']} {track['title']} [{host}]", flush=True)
            
            # Scripts
            intro, outro = scripts.generate_show_segment(track, hour=time.localtime().tm_hour)
            
            # TTS
            iw = tts.generate(intro, host, f"s{seg_n}_i.wav")
            ow = tts.generate(outro, host, f"s{seg_n}_o.wav")
            
            # Music + Mix
            style = "rus" if track["flag"] == "🇷🇺" else "world"
            mw = mixer.get_music(style)
            seg = mixer.create_broadcast_segment(mw, iw, ow)
            mp3 = mixer.wav_to_mp3(seg)
            
            with open(mp3, 'rb') as f:
                data = f.read()
            
            ok = stream_mp3(data)
            print(f"  {'📡' if ok else '❌'} {len(data)//1024}KB", flush=True)
            
            # State
            with open(state_file, 'w') as f:
                json.dump({
                    "title": track["title"], "artist": track["artist"],
                    "flag": track["flag"], "host": host,
                    "intro": intro[:80], "tracks_played": seg_n + 1,
                    "listeners": random.randint(80, 150),
                    "uptime_hours": int((time.time()-start)/3600),
                }, f, ensure_ascii=False)
            
            seg_n += 1
            time.sleep(0.3)
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    main()
