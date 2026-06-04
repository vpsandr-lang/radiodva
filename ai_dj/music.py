"""RADIO DVA AI — Top hits music library. 50% Russia, 50% World.
No classical, no jazz — only what 80% of people listen to.
"""
import json, os, random
from pathlib import Path

TRACKS_REAL_DIR = "/root/Radio/ai_dj/tracks_real"

# Only top hits — what people actually listen to
TRACKS = [
    # Russian top hits (50%)
    {"id": "rus01", "title": "Поначалу", "artist": "Баста", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus02", "title": "Я твоя", "artist": "Anna Asti", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus03", "title": "Плакала", "artist": "Kazka", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus04", "title": "Малиновая Лада", "artist": "Gayazovs Brothers", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus05", "title": "Squad", "artist": "Miyagi & Andy Panda", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus06", "title": "Зацепила", "artist": "Artik & Asti", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus07", "title": "На часах ноль", "artist": "Feduk", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus08", "title": "Венера-Юпитер", "artist": "Ваня Дмитриенко", "flag": "🇷🇺", "genre": "rus"},
    {"id": "rus09", "title": "Не вдвоём", "artist": "Zivert", "flag": "🇷🇺", "genre": "rus"},
    # World top hits (50%)
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
]

# Pure 50/50 split: Russian and World hits
GENRE_RATIOS = [
    ("rus", 50),
    ("world", 50),
]

GENRE_FLAGS = {
    "rus": "🇷🇺",
    "world": "🌍",
}


def get_track_path(track_id):
    """Get the actual file path for a track by its ID."""
    path = os.path.join(TRACKS_REAL_DIR, f"{track_id}.mp3")
    if os.path.exists(path):
        return path
    path = os.path.join(TRACKS_REAL_DIR, f"{track_id}.wav")
    if os.path.exists(path):
        return path
    return None


class MusicScheduler:
    """Schedules tracks with 50/50 genre rotation."""

    def __init__(self):
        self.history = []
        self.current_playlist = []
        self.genre_queue = []
        self._build_playlist()

    def _build_playlist(self):
        tracks_by_genre = {}
        for t in TRACKS:
            g = t.get("genre", "world")
            if g not in tracks_by_genre:
                tracks_by_genre[g] = []
            tracks_by_genre[g].append(t)

        for g in tracks_by_genre:
            random.shuffle(tracks_by_genre[g])

        # 50/50 genre rotation
        self.genre_queue = []
        for genre, ratio in GENRE_RATIOS:
            count = max(1, ratio // 10)
            self.genre_queue.extend([genre] * count)
        random.shuffle(self.genre_queue)

        genre_pointers = {g: 0 for g in tracks_by_genre}
        self.current_playlist = []
        for genre in self.genre_queue:
            pool = tracks_by_genre.get(genre, [])
            if not pool:
                continue
            idx = genre_pointers[genre] % len(pool)
            genre_pointers[genre] = idx + 1
            track = pool[idx].copy()
            track["file_path"] = get_track_path(track["id"])
            track["style"] = genre
            if track["file_path"]:
                self.current_playlist.append(track)

        if not self.current_playlist:
            for t in TRACKS:
                fp = get_track_path(t["id"])
                if fp:
                    track = t.copy()
                    track["file_path"] = fp
                    track["style"] = t["genre"]
                    self.current_playlist.append(track)
                    break

    def next_track(self):
        if not self.current_playlist:
            self._build_playlist()
        track = self.current_playlist.pop(0)
        self.history.append(track["id"])
        if len(self.history) > 50:
            self.history.pop(0)
        return track

    def get_history(self, n=10):
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
