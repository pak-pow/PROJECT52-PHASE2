import time
from functools import wraps
from flask import jsonify, make_response, request
from app.services.client_identifier import get_client_identifier
from app.services.storage_adapter import storage
from app.services.api_key_service import api_key_manager

def rate_limit(limit: int = 10, window: float = 60.0, algorithm: str = "token_bucket", use_tier: bool = False):
    """Flask decorator enforcing API rate limits per client.
    
    Args:
        limit (int): Default max allowed requests in window.
        window (float): Default window duration in seconds.
        algorithm (str): 'token_bucket' or 'sliding_window'.
        use_tier (bool): If True, dynamically resolves limit from API Key tier.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client_id = get_client_identifier()
            
            effective_limit = limit
            effective_window = window

            if use_tier and client_id.startswith("apikey:"):
                raw_key = client_id.split(":", 1)[1]
                t_limit, t_window = api_key_manager.get_tier_limit(raw_key)
                effective_limit = t_limit
                effective_window = t_window

            key = f"limiter:{f.__name__}:{client_id}"
            now = time.time()

            if algorithm == "token_bucket":
                fill_rate = float(effective_limit) / float(effective_window)
                bucket = storage.get_token_bucket(key, capacity=effective_limit, fill_rate=fill_rate)
                allowed, remaining, time_to_wait = bucket.consume(1)

                reset_epoch = int(now + time_to_wait)
                remaining_int = int(max(0, remaining))

                if not allowed:
                    resp = make_response(jsonify({
                        "error": "Too Many Requests",
                        "message": f"API rate limit exceeded. Retry in {int(time_to_wait)} seconds.",
                        "retry_after": int(time_to_wait)
                    }), 429)
                    resp.headers["X-RateLimit-Limit"] = str(effective_limit)
                    resp.headers["X-RateLimit-Remaining"] = "0"
                    resp.headers["X-RateLimit-Reset"] = str(reset_epoch)
                    resp.headers["Retry-After"] = str(int(max(1, time_to_wait)))
                    return resp

                response = make_response(f(*args, **kwargs))
                response.headers["X-RateLimit-Limit"] = str(effective_limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining_int)
                response.headers["X-RateLimit-Reset"] = str(reset_epoch)
                return response

            elif algorithm == "sliding_window":
                window_log = storage.get_sliding_window(key, limit=effective_limit, window_seconds=effective_window)
                allowed, remaining, retry_after = window_log.is_allowed()

                reset_epoch = int(now + retry_after) if not allowed else int(now + effective_window)

                if not allowed:
                    resp = make_response(jsonify({
                        "error": "Too Many Requests",
                        "message": f"API rate limit exceeded. Retry in {int(retry_after)} seconds.",
                        "retry_after": int(retry_after)
                    }), 429)
                    resp.headers["X-RateLimit-Limit"] = str(effective_limit)
                    resp.headers["X-RateLimit-Remaining"] = "0"
                    resp.headers["X-RateLimit-Reset"] = str(reset_epoch)
                    resp.headers["Retry-After"] = str(int(max(1, retry_after)))
                    return resp

                response = make_response(f(*args, **kwargs))
                response.headers["X-RateLimit-Limit"] = str(effective_limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(reset_epoch)
                return response

            return f(*args, **kwargs)
        return decorated
    return decorator
