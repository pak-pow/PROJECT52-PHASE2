import time
import logging
from app.services.storage_adapter import storage as memory_storage

logger = logging.getLogger(__name__)

class RedisStorageAdapter:
    """Distributed Redis Storage Adapter with In-Memory Fallback."""
    def __init__(self, redis_url: str = None):
        self.redis_client = None
        self.is_connected = False
        if redis_url:
            self._connect(redis_url)

    def _connect(self, redis_url: str):
        try:
            import redis
            client = redis.Redis.from_url(redis_url, socket_timeout=2.0)
            client.ping()
            self.redis_client = client
            self.is_connected = True
            logger.info("Connected to Redis Rate Limiter Store.")
        except Exception as e:
            self.is_connected = False
            logger.warning(f"Redis unavailable ({e}). Falling back to In-Memory store.")

    def get_token_bucket(self, key: str, capacity: int, fill_rate: float):
        if self.is_connected and self.redis_client:
            # Future Redis Lua Script execution
            pass
        return memory_storage.get_token_bucket(key, capacity, fill_rate)

    def get_sliding_window(self, key: str, limit: int, window_seconds: float):
        if self.is_connected and self.redis_client:
            # Future Redis ZADD/ZREMRANGEBYSCORE execution
            pass
        return memory_storage.get_sliding_window(key, limit, window_seconds)

redis_storage = RedisStorageAdapter()
