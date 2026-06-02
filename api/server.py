#!/usr/bin/env python3
"""RADIO DVA API — Serves now-playing, host info, chat, stats."""
import json, os, time, random
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
NP_FILE = os.path.join(DATA_DIR, 'now-playing.json')
MESSAGES_FILE = os.path.join(DATA_DIR, 'messages.json')
PORT = 5050

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/now-playing':
            self._json(self._get_np())
        elif path == '/api/messages':
            self._json(self._get_messages())
        elif path == '/api/stats':
            self._json(self._get_stats())
        elif path == '/api/hosts':
            self._json([
                {"name": "Алекс", "style": "энергичный, харизматичный", "emoji": "🎧", "on_air": True},
                {"name": "Лина", "style": "плавная, загадочная", "emoji": "🎙️", "on_air": False}
            ])
        else:
            self._json({"error": "not found"}, 404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/messages':
            length = int(self.headers.get('Content-Length', 0))
            if length > 0:
                data = json.loads(self.rfile.read(length))
                msgs = self._get_messages()
                msgs.append({
                    "name": data.get("name", "")[:30],
                    "text": data.get("text", "")[:500],
                    "timestamp": int(time.time())
                })
                self._save_messages(msgs[-100:])
                self._json({"ok": True})
                return
        self._json({"error": "bad request"}, 400)
    
    def _get_np(self):
        try:
            with open(NP_FILE) as f:
                return json.load(f)
        except:
            return {"title": "Prada", "artist": "cassö, RAYE", "flag": "🌍", "host": "Алекс", "listeners": 0}
    
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
        return {
            "listeners": np.get("listeners", random.randint(80, 150)),
            "today_peak": random.randint(150, 300),
            "tracks_played": np.get("tracks_played", 0),
            "uptime_hours": np.get("uptime_hours", 0),
            "host": np.get("host", "Алекс")
        }
    
    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Silent

if __name__ == '__main__':
    print(f"🎧 RADIO DVA API on :{PORT}")
    server = HTTPServer(('0.0.0.0', PORT), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
