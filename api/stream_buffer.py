"""RADIO DVA — Thread-safe audio stream broadcast buffer."""

import threading
import time
import collections
import os
import struct
import hashlib
import json
import random

class StreamBuffer:
    """In-memory circular buffer for live audio streaming.
    
    The AI DJ thread appends MP3 segments.
    HTTP streaming threads read segments and send to clients.
    """

    def __init__(self, max_chunks=2000):
        self.chunks = collections.deque(maxlen=max_chunks)
        self.lock = threading.Lock()
        self._next_id = 0
        self._listeners = {}  # listener_id -> cursor position
        self._metadata = {
            "title": "RADIO DVA",
            "artist": "Двойная Волна",
            "flag": "🎵",
            "host": "Алекс",
            "status": "initializing",
            "listeners": 0,
            "tracks_played": 0,
            "uptime_hours": 0,
        }
        self._start_time = time.time()

    def append(self, mp3_data: bytes):
        """Append an MP3 chunk to the buffer."""
        with self.lock:
            self.chunks.append(mp3_data)

    def register_listener(self) -> int:
        """Register a new HTTP streaming listener. Returns listener_id."""
        with self.lock:
            self._next_id += 1
            lid = self._next_id
            self._listeners[lid] = len(self.chunks)
            return lid

    def unregister_listener(self, listener_id: int):
        with self.lock:
            self._listeners.pop(listener_id, None)

    def get_metadata(self) -> dict:
        with self.lock:
            return dict(self._metadata)

    def update_metadata(self, **kwargs):
        with self.lock:
            self._metadata.update(kwargs)
            self._metadata["uptime_hours"] = int((time.time() - self._start_time) / 3600)
            self._metadata["listeners"] = len(self._listeners)

    def get_new_chunks(self, listener_id: int, max_chunks=10):
        """Get new chunks since last read for a listener."""
        with self.lock:
            if listener_id not in self._listeners:
                return []
            cursor = self._listeners[listener_id]
            total = len(self.chunks)
            if cursor >= total:
                return []
            result = []
            for i in range(cursor, min(cursor + max_chunks, total)):
                result.append(self.chunks[i])
            self._listeners[listener_id] = min(cursor + max_chunks, total)
            return result

    def get_all_chunks(self):
        """Get all chunks currently in buffer."""
        with self.lock:
            return list(self.chunks)

    def listener_count(self):
        with self.lock:
            return len(self._listeners)


# Global instance
STREAM = StreamBuffer()
