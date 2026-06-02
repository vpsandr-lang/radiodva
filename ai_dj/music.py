"""
RADIO DVA AI — Music Library & Scheduler
Handles 50/50 Russian/World music rotation.
"""
import json, os, random
from pathlib import Path

# Demo track database (synthetic placeholder tracks)
# In production, replace with real MP3 files
TRACKS = [
    # Russian hits
    {"id": "rus01", "title": "Поначалу", "artist": "Баста", "flag": "🇷🇺", "lang": "ru"},
    {"id": "rus02", "title": "Я твоя", "artist": "Anna Asti", "flag": "🇷🇺", "lang": "ru"},
    {"id": "rus03", "title": "Плакала", "artist": "Kazka", "flag": "🇷🇺", "lang": "ru"},
    {"id": "rus04", "title": "Малиновая Лада", "artist": "Gayazovs Brothers", "flag": "🇷🇺", "lang": "ru"},
    {"id": "rus05", "title": "Squad", "artist": "Miyagi & Andy Panda", "flag": "🇷🇺", "lang": "ru"},
    {"id": "rus06", "title": "Зацепила", "artist": "Artik & Asti", "flag": "🇷🇺", "lang": "ru"},
    {"id": "rus07", "title": "На часах ноль", "artist": "Feduk", "flag": "🇷🇺", "lang": "ru"},
    {"id": "rus08", "title": "Венера-Юпитер", "artist": "Ваня Дмитриенко", "flag": "🇷🇺", "lang": "ru"},
    {"id": "rus09", "title": "Не вдвоём", "artist": "Zivert", "flag": "🇷🇺", "lang": "ru"},
    {"id": "rus10", "title": "Veni Vidi Vici", "artist": "Blizkey", "flag": "🇷🇺", "lang": "ru"},
    # World hits
    {"id": "wld01", "title": "Blinding Lights", "artist": "The Weeknd", "flag": "🌍", "lang": "en"},
    {"id": "wld02", "title": "Flowers", "artist": "Miley Cyrus", "flag": "🌍", "lang": "en"},
    {"id": "wld03", "title": "As It Was", "artist": "Harry Styles", "flag": "🌍", "lang": "en"},
    {"id": "wld04", "title": "Shape of You", "artist": "Ed Sheeran", "flag": "🌍", "lang": "en"},
    {"id": "wld05", "title": "Starboy", "artist": "The Weeknd", "flag": "🌍", "lang": "en"},
    {"id": "wld06", "title": "Cruel Summer", "artist": "Taylor Swift", "flag": "🌍", "lang": "en"},
    {"id": "wld07", "title": "Lose Control", "artist": "Teddy Swims", "flag": "🌍", "lang": "en"},
    {"id": "wld08", "title": "Beautiful Things", "artist": "Benson Boone", "flag": "🌍", "lang": "en"},
    {"id": "wld09", "title": "Prada", "artist": "cassö, RAYE, D-Block Europe", "flag": "🌍", "lang": "en"},
    {"id": "wld10", "title": "Good Luck, Babe!", "artist": "Chappell Roan", "flag": "🌍", "lang": "en"},
]

class MusicScheduler:
    """Schedules 50/50 Russian/World tracks with no repeat."""

    def __init__(self):
        self.history = []  # Track IDs that have been played
        self.current_playlist = []
        self._build_playlist()

    def _build_playlist(self):
        """Build 50/50 alternating playlist."""
        rus = [t for t in TRACKS if t["flag"] == "🇷🇺"]
        wld = [t for t in TRACKS if t["flag"] == "🌍"]
        random.shuffle(rus)
        random.shuffle(wld)
        # Interleave 50/50
        self.current_playlist = []
        while rus or wld:
            if rus:
                self.current_playlist.append(rus.pop())
            if wld:
                self.current_playlist.append(wld.pop())

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
        """Get currently playing track."""
        if self.history:
            tid = self.history[-1]
            for t in TRACKS:
                if t["id"] == tid:
                    return t
        return TRACKS[0]
