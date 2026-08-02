import time
import threading

class SlidingWindowLog:
    """Thread-safe Sliding Window Log Rate Limiting Algorithm.
    
    Attributes:
        limit (int): Maximum allowed requests in window.
        window_seconds (float): Window duration in seconds.
        timestamps (list): Sorted list of request timestamps.
    """
    def __init__(self, limit: int, window_seconds: float):
        self.limit = limit
        self.window_seconds = float(window_seconds)
        self.timestamps = []
        self._lock = threading.Lock()

    def is_allowed(self) -> tuple[bool, int, float]:
        """Evaluate request against sliding window log.
        
        Returns:
            tuple: (allowed: bool, remaining_requests: int, retry_after: float)
        """
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            # Evict timestamps outside current sliding window
            self.timestamps = [ts for ts in self.timestamps if ts > cutoff]

            if len(self.timestamps) < self.limit:
                self.timestamps.append(now)
                remaining = self.limit - len(self.timestamps)
                return True, remaining, 0.0
            else:
                oldest_in_window = self.timestamps[0]
                retry_after = max(0.0, (oldest_in_window + self.window_seconds) - now)
                return False, 0, retry_after
