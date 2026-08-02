import time
import threading

class TokenBucket:
    """Thread-safe Token Bucket Rate Limiting Algorithm.
    
    Attributes:
        capacity (int): Maximum token capacity of the bucket.
        refill_rate (float): Tokens added per second.
        tokens (float): Current available tokens in the bucket.
        last_refill (float): Timestamp of last token refill.
    """
    def __init__(self, capacity: int, fill_rate: float):
        self.capacity = float(capacity)
        self.refill_rate = float(fill_rate)
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self._lock = threading.Lock()

    def _refill(self):
        now = time.time()
        delta = now - self.last_refill
        if delta > 0:
            added_tokens = delta * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + added_tokens)
            self.last_refill = now

    def consume(self, tokens: int = 1) -> tuple[bool, float, float]:
        """Attempt to consume tokens from the bucket.
        
        Returns:
            tuple: (allowed: bool, remaining_tokens: float, time_to_reset: float)
        """
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                time_to_reset = (self.capacity - self.tokens) / self.refill_rate if self.refill_rate > 0 else 0
                return True, self.tokens, time_to_reset
            else:
                needed = tokens - self.tokens
                wait_time = needed / self.refill_rate if self.refill_rate > 0 else 0
                return False, self.tokens, wait_time
