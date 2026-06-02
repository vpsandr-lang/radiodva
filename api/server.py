#!/usr/bin/env python3
"""RADIO DVA API — Serves now-playing, chat, stats, hosts, audio stream, and static files."""

import json
import os
import time
import random
import select
import socket
import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DATA_DIR)  # /root/Radio
NP_FILE = os.path.join(DATA_DIR, 'now-playing.json')
MESSAGES_FILE = os.path.join(DATA_DIR, 'messages.json')
PORT = int(os.environ.get('PORT', 5050))

from api.stream_buffer import STREAM


class APIHandler(BaseHTTPRequestHandler):
    """HTTP handler for API endpoints, audio streaming, and static files."""

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/') or '/'

        try:
            # API endpoints
            if path == '/api/now-playing':
                return self._serve_json(self._get_np())
            elif path == '/api/messages':
                return self._serve_json(self._get_messages())
            elif path == '/api/stats':
                return self._serve_json(self._get_stats())
            elif path == '/api/hosts':
                return self._serve_json(self._get_hosts())
            elif path in ('/api/stream', '/api/stream.mp3'):
                return self._serve_stream()
            elif path == '/api/health':
                return self._serve_json({"status": "ok", "listeners": STREAM.listener_count()})
            elif path.startswith('/api/'):
                return self._serve_json({"error": "not found"}, 404)

            # Static files
            return self._serve_static(path)

        except Exception as e:
            print(f"⚠️ Error handling {path}: {e}", flush=True)
            try:
                if path.startswith('/api/'):
                    self._serve_json({"error": str(e)}, 500)
                else:
                    self._serve_error(500, str(e))
            except:
                pass

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/messages':
            try:
                length = int(self.headers.get('Content-Length', 0))
                if length > 0:
                    data = json.loads(self.rfile.read(length))
                    msgs = self._get_messages()
                    msgs.append({
                        "name": data.get("name", "User")[:30],
                        "text": data.get("text", "")[:500],
                        "timestamp": int(time.time())
                    })
                    self._save_messages(msgs[-100:])
                    return self._serve_json({"ok": True})
            except Exception as e:
                return self._serve_json({"error": str(e)}, 400)
        self._serve_json({"error": "bad request"}, 400)

    def do_OPTIONS(self):
        self._cors_headers()
        self.send_response(200)
        self.end_headers()

    # ---- Static File Serving ----

    def _serve_static(self, path):
        """Serve static files from ROOT_DIR."""
        if path == '/':
            path = '/index.html'

        # Security: prevent directory traversal
        safe_path = path.lstrip('/')
        filepath = os.path.normpath(os.path.join(ROOT_DIR, safe_path))
        if not filepath.startswith(ROOT_DIR):
            return self._serve_error(403, "Forbidden")

        if not os.path.isfile(filepath):
            # Try index.html for SPA routing
            index_path = os.path.join(ROOT_DIR, 'index.html')
            if os.path.isfile(index_path):
                filepath = index_path
            else:
                return self._serve_error(404, "Not Found")

        # Guess MIME type
        content_type, _ = mimetypes.guess_type(filepath)
        if content_type is None:
            content_type = 'application/octet-stream'

        # Special handling for common web types
        ext = pathlib.Path(filepath).suffix.lower()
        mime_map = {
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.html': 'text/html; charset=utf-8',
            '.svg': 'image/svg+xml',
            '.json': 'application/json',
            '.mp3': 'audio/mpeg',
            '.ogg': 'audio/ogg',
            '.wav': 'audio/wav',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.ico': 'image/x-icon',
            '.webp': 'image/webp',
        }
        content_type = mime_map.get(ext, content_type)

        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'public, max-age=3600')
            self._cors_headers()
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._serve_error(500, str(e))

    def _serve_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self._cors_headers()
        self.end_headers()
        self.wfile.write(str(message).encode())

    # ---- API Methods ----

    def _get_np(self):
        meta = STREAM.get_metadata()
        if meta.get("title") and meta.get("title") != "RADIO DVA":
            return {
                "title": meta.get("title", "RADIO DVA"),
                "artist": meta.get("artist", "Двойная Волна"),
                "flag": meta.get("flag", "🎵"),
                "host": meta.get("host", "Алекс"),
                "intro": meta.get("intro", ""),
                "listeners": STREAM.listener_count(),
                "tracks_played": meta.get("tracks_played", 0),
                "uptime_hours": meta.get("uptime_hours", 0),
                "status": meta.get("status", "broadcasting"),
            }
        try:
            with open(NP_FILE) as f:
                return json.load(f)
        except:
            return {
                "title": "RADIO DVA",
                "artist": "Двойная Волна",
                "flag": "🎵",
                "host": "Алекс",
                "listeners": 0,
                "status": "initializing",
            }

    def _get_messages(self):
        try:
            with open(MESSAGES_FILE) as f:
                return json.load(f)
        except:
            return []

    def _save_messages(self, msgs):
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(msgs, f, ensure_ascii=False)

    def _get_stats(self):
        meta = STREAM.get_metadata()
        return {
            "listeners": STREAM.listener_count(),
            "today_peak": max(STREAM.listener_count(), random.randint(5, 30)),
            "tracks_played": meta.get("tracks_played", 0),
            "uptime_hours": meta.get("uptime_hours", 0),
            "host": meta.get("host", "Алекс"),
            "status": meta.get("status", "broadcasting"),
        }

    def _get_hosts(self):
        meta = STREAM.get_metadata()
        current_host = meta.get("host", "Алекс")
        return [
            {"name": "Алекс", "style": "энергичный, харизматичный", "emoji": "🎧", "on_air": current_host == "Алекс"},
            {"name": "Лина", "style": "плавная, загадочная", "emoji": "🎙️", "on_air": current_host == "Лина"}
        ]

    # ---- Audio Streaming ----

    def _serve_stream(self):
        """Serve continuous audio stream via chunked transfer encoding."""
        listener_id = STREAM.register_listener()
        print(f"📻 Listener #{listener_id} connected", flush=True)

        try:
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Transfer-Encoding', 'chunked')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()

            # Send initial chunks for fast startup
            initial = STREAM.get_all_chunks()
            for chunk in initial[:20]:
                self._send_chunk(chunk)

            # Streaming loop
            empty_count = 0
            while True:
                chunks = STREAM.get_new_chunks(listener_id, max_chunks=5)
                if chunks:
                    for chunk in chunks:
                        self._send_chunk(chunk)
                    empty_count = 0
                else:
                    empty_count += 1
                    if empty_count > 600:  # ~5 min silence → disconnect
                        break
                    time.sleep(0.5)

        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass
        except Exception as e:
            print(f"⚠️ Stream error #{listener_id}: {e}", flush=True)
        finally:
            STREAM.unregister_listener(listener_id)
            print(f"📻 Listener #{listener_id} disconnected", flush=True)

    def _send_chunk(self, data):
        if not data:
            return
        self.wfile.write(f"{len(data):x}\r\n".encode())
        self.wfile.write(data)
        self.wfile.write(b"\r\n")
        self.wfile.flush()

    # ---- Helpers ----

    def _serve_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

    def log_message(self, format, *args):
        pass


def run_server():
    """Start the API server."""
    print(f"🎧 RADIO DVA API on :{PORT}", flush=True)
    server = HTTPServer(('0.0.0.0', PORT), APIHandler)
    server.socket.settimeout(None)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Server stopping...", flush=True)
        server.shutdown()


if __name__ == '__main__':
    run_server()
