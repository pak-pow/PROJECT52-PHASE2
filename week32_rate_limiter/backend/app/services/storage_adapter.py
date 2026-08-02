import threading
from app.services.token_bucket import TokenBucket
from app.services.sliding_window import SlidingWindowLog

class InMemoryStorage:
    """Thread-safe In-Memory Storage Adapter for Rate Limiters."""
    def __init__(self):
        self._buckets = {}
        self._windows = {}
        self._lock = threading.Lock()

    def get_token_bucket(self, key: str, capacity: int, fill_rate: float) -> TokenBucket:
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = TokenBucket(capacity, fill_rate)
            return self._buckets[key]

    def get_sliding_window(self, key: str, limit: int, window_seconds: float) -> SlidingWindowLog:
        with self._lock:
            if key not in self._windows:
                self._windows[key] = SlidingWindowLog(limit, window_seconds)
            return self._windows[key]

    def clear(self):
        with self._lock:
            self._buckets.clear()
            self._windows.clear()

storage = InMemoryStorage()
