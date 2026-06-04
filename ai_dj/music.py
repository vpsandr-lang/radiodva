"""RADIO DVA AI — Music Library & Scheduler with genre rotation.
Uses real MP3 files from tracks_real directory.
"""
import json, os, random
from pathlib import Path

TRACKS_REAL_DIR = "/root/Radio/ai_dj/tracks_real"
NEW_TRACKS_DIR = "/root/Radio/new_tracks"

# Track database — all real MP3 files
TRACKS = [
    # Russian hits
    {"id": "rus01", "title": "Поначалу", "artist": "Баста", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus02", "title": "Я твоя", "artist": "Anna Asti", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus03", "title": "Плакала", "artist": "Kazka", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus04", "title": "Малиновая Лада", "artist": "Gayazovs Brothers", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus05", "title": "Squad", "artist": "Miyagi & Andy Panda", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus06", "title": "Зацепила", "artist": "Artik & Asti", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus07", "title": "На часах ноль", "artist": "Feduk", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus08", "title": "Венера-Юпитер", "artist": "Ваня Дмитриенко", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus09", "title": "Не вдвоём", "artist": "Zivert", "flag": "🇷🇺", "genre": "rus"},
    # World hits
    {"id": "wld01", "title": "Blinding Lights", "artist": "The Weeknd", "flag": "🌍", "genre": "world"},
    {"id": "wld02", "title": "Flowers", "artist": "Miley Cyrus", "flag": "🌍", "genre": "world"},
    {"id": "wld03", "title": "As It Was", "artist": "Harry Styles", "flag": "🌍", "genre": "world"},
    {"id": "wld04", "title": "Shape of You", "artist": "Ed Sheeran", "flag": "🌍", "genre": "world"},
    {"id": "wld05", "title": "Starboy", "artist": "The Weeknd", "flag": "🌍", "genre": "world"},
    {"id": "wld06", "title": "Cruel Summer", "artist": "Taylor Swift", "flag": "🌍", "genre": "world"},
    {"id": "wld07", "title": "Lose Control", "artist": "Teddy Swims", "flag": "🌍", "genre": "world"},
    {"id": "wld08", "title": "Beautiful Things", "artist": "Benson Boone", "flag": "🌍", "genre": "world"},
    {"id": "wld09", "title": "Prada", "artist": "cassö, RAYE, D-Block Europe", "flag": "🌍", "genre": "world"},
    {"id": "wld10", "title": "Good Luck, Babe!", "artist": "Chappell Roan", "flag": "🌍", "genre": "world"},
    # Hip-hop
    {"id": "hh01", "title": "Hip Hop Beat", "artist": "Free Music", "flag": "🎤", "genre": "hiphop"},
    {"id": "hh02", "title": "Hip Hop Flow", "artist": "Free Music", "flag": "🎤", "genre": "hiphop"},
    # Classical
    {"id": "cl01", "title": "Classical Piece", "artist": "Классика", "flag": "🎻", "genre": "classical"},
    # Jazz / Blues
    {"id": "jz01", "title": "Jazz Mood", "artist": "Jazz Ensemble", "flag": "🎷", "genre": "jazz"},
]

# Genre rotation: 40% Russian, 40% World, 10% Hip-hop, 5% Classical, 5% Jazz/Blues
GENRE_RATIOS = [
    ("rus", 40),
    ("world", 40),
    ("hiphop", 10),
    ("classical", 5),
    ("jazz", 5),
]

GENRE_FLAGS = {
    "rus": "🇷🇺",
    "world": "🌍",
    "hiphop": "🎤",
    "classical": "🎻",
    "jazz": "🎷",
}


def get_track_path(track_id):
    """Get the actual file path for a track by its ID."""
    # Try tracks_real first
    path = os.path.join(TRACKS_REAL_DIR, f"{track_id}.mp3")
    if os.path.exists(path):
        return path
    # Try with .wav extension
    path = os.path.join(TRACKS_REAL_DIR, f"{track_id}.wav")
    if os.path.exists(path):
        return path
    return None


class MusicScheduler:
    """Schedules tracks with genre-based rotation."""

    def __init__(self):
        self.history = []
        self.current_playlist = []
        self.genre_queue = []
        self._build_playlist()

    def _build_playlist(self):
        """Build playlist respecting genre ratios."""
        tracks_by_genre = {}
        for t in TRACKS:
            g = t.get("genre", "world")
            if g not in tracks_by_genre:
                tracks_by_genre[g] = []
            tracks_by_genre[g].append(t)

        # Shuffle each genre pool
        for g in tracks_by_genre:
            random.shuffle(tracks_by_genre[g])

        # Build genre queue based on ratios
        self.genre_queue = []
        for genre, ratio in GENRE_RATIOS:
            count = max(1, ratio // 10)
            self.genre_queue.extend([genre] * count)
        random.shuffle(self.genre_queue)

        # Assign tracks from genre pools
        genre_pointers = {g: 0 for g in tracks_by_genre}
        self.current_playlist = []
        for genre in self.genre_queue:
            pool = tracks_by_genre.get(genre, [])
            if not pool:
                continue
            idx = genre_pointers[genre] % len(pool)
            genre_pointers[genre] = idx + 1
            track = pool[idx].copy()
            # Set file path
            track["file_path"] = get_track_path(track["id"])
            track["style"] = genre
            if track["file_path"]:
                self.current_playlist.append(track)
            else:
                print(f"  ⚠️ Track file not found: {track['id']}", flush=True)

        if not self.current_playlist:
            # Fallback
            for t in TRACKS:
                fp = get_track_path(t["id"])
                if fp:
                    track = t.copy()
                    track["file_path"] = fp
                    track["style"] = t["genre"]
                    self.current_playlist.append(track)
                    break

    def next_track(self):
        """Get next track and update history."""
        if not self.current_playlist:
            self._build_playlist()
        track = self.current_playlist.pop(0)
        self.history.append(track["id"])
        if len(self.history) > 50:
            self.history.pop(0)
        return track

    def get_history(self, n=10):
        """Get last N played tracks."""
        result = []
        for tid in reversed(self.history[-n:]):
            for t in TRACKS:
                if t["id"] == tid:
                    result.append(t)
                    break
        return result

    def current_track(self):
        if self.history:
            tid = self.history[-1]
            for t in TRACKS:
                if t["id"] == tid:
                    return t
        return TRACKS[0] if TRACKS else {"id": "none", "title": "RADIO DVA", "artist": "", "flag": "🎵", "genre": "world"}
