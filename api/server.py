#!/usr/bin/env python3
"""RADIO DVA API — HTTP server with streaming."""
import json, os, time, random, mimetypes, pathlib, hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DATA_DIR)
NP_FILE = os.path.join(DATA_DIR, 'now-playing.json')
MESSAGES_FILE = os.path.join(DATA_DIR, 'messages.json')
PORT = int(os.environ.get('PORT', 5050))


class APIHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/') or '/'

        try:
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
                return self._serve_json({"status": "ok"})
            elif path.startswith('/api/'):
                return self._serve_json({"error": "not found"}, 404)

            return self._serve_static(path)

        except Exception as e:
            print(f"Error: {e}", flush=True)
            try: self._serve_error(500, str(e))
            except: pass

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
        self._cors()
        self.send_response(200)
        self.end_headers()

    def _serve_static(self, path):
        if path == '/':
            path = '/index.html'
        safe_path = path.lstrip('/')
        filepath = os.path.normpath(os.path.join(ROOT_DIR, safe_path))
        if not filepath.startswith(ROOT_DIR):
            return self._serve_error(403, "Forbidden")
        if not os.path.isfile(filepath):
            index_path = os.path.join(ROOT_DIR, 'index.html')
            if os.path.isfile(index_path):
                filepath = index_path
            else:
                return self._serve_error(404, "Not Found")
        content_type, _ = mimetypes.guess_type(filepath)
        ext = pathlib.Path(filepath).suffix.lower()
        mime_map = {
            '.js': 'application/javascript', '.css': 'text/css',
            '.html': 'text/html; charset=utf-8', '.svg': 'image/svg+xml',
            '.json': 'application/json', '.mp3': 'audio/mpeg',
            '.ogg': 'audio/ogg', '.wav': 'audio/wav',
            '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.ico': 'image/x-icon', '.webp': 'image/webp',
        }
        content_type = mime_map.get(ext, content_type if content_type else 'application/octet-stream')
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'public, max-age=3600')
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._serve_error(500, str(e))

    def _serve_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self._cors()
        self.end_headers()
        self.wfile.write(str(message).encode())

    def _serve_stream(self):
        """Serve the latest MP3 segment."""
        from api.file_broadcaster import get_stream_data
        data = get_stream_data()
        if not data:
            self._serve_error(503, "Stream not ready")
            return
        self.send_response(200)
        self.send_header('Content-Type', 'audio/mpeg')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        try:
            self.wfile.write(data)
        except:
            pass

    def _get_np(self):
        try:
            with open(NP_FILE) as f:
                return json.load(f)
        except:
            return {"title": "RADIO DVA", "artist": "Двойная Волна", "flag": "🎵", "host": "Алекс", "listeners": 0, "status": "broadcasting"}

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
        np = self._get_np()
        return {"listeners": 0, "today_peak": random.randint(5, 30), "tracks_played": np.get("tracks_played", 0), "uptime_hours": np.get("uptime_hours", 0), "host": np.get("host", "Алекс"), "status": np.get("status", "broadcasting")}

    def _get_hosts(self):
        np = self._get_np()
        ch = np.get("host", "Алекс")
        return [{"name": "Алекс", "style": "энергичный", "emoji": "🎧", "on_air": ch == "Алекс"}, {"name": "Лина", "style": "плавная", "emoji": "🎙️", "on_air": ch == "Лина"}]

    def _serve_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

    def log_message(self, format, *args):
        pass


def run_server():
    print(f"API on :{PORT}", flush=True)
    server = HTTPServer(('0.0.0.0', PORT), APIHandler)
    server.socket.settimeout(None)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping...", flush=True)
        server.shutdown()

if __name__ == '__main__':
    run_server()
