import uuid
import threading

# Tier Definitions: (Limit, Window Seconds)
TIER_LIMITS = {
    "free": (5, 60.0),         # 5 requests / 60 seconds
    "pro": (30, 60.0),        # 30 requests / 60 seconds
    "enterprise": (100, 60.0)  # 100 requests / 60 seconds
}

class APIKeyManager:
    """Thread-safe API Key & Tier Manager."""
    def __init__(self):
        self._keys = {
            "demo-free-key": "free",
            "demo-pro-key": "pro",
            "demo-enterprise-key": "enterprise"
        }
        self._lock = threading.Lock()

    def generate_key(self, tier: str = "free") -> str:
        tier = tier.lower()
        if tier not in TIER_LIMITS:
            tier = "free"
        
        new_key = f"key_{uuid.uuid4().hex[:12]}"
        with self._lock:
            self._keys[new_key] = tier
        return new_key

    def get_tier(self, api_key: str) -> str:
        with self._lock:
            return self._keys.get(api_key, "free")

    def get_tier_limit(self, api_key: str) -> tuple[int, float]:
        tier = self.get_tier(api_key)
        return TIER_LIMITS.get(tier, TIER_LIMITS["free"])

api_key_manager = APIKeyManager()
