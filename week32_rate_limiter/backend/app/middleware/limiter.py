import time
from functools import wraps
from flask import jsonify, make_response, request
from app.services.client_identifier import get_client_identifier
from app.services.storage_adapter import storage

def rate_limit(limit: int = 10, window: float = 60.0, algorithm: str = "token_bucket"):
    """Flask decorator enforcing API rate limits per client.
    
    Args:
        limit (int): Max allowed requests in window.
        window (float): Window duration in seconds.
        algorithm (str): 'token_bucket' or 'sliding_window'.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client_id = get_client_identifier()
            key = f"limiter:{f.__name__}:{client_id}"
            now = time.time()

            if algorithm == "token_bucket":
                fill_rate = float(limit) / float(window)
                bucket = storage.get_token_bucket(key, capacity=limit, fill_rate=fill_rate)
                allowed, remaining, time_to_wait = bucket.consume(1)

                reset_epoch = int(now + time_to_wait)
                remaining_int = int(max(0, remaining))

                if not allowed:
                    resp = make_response(jsonify({
                        "error": "Too Many Requests",
                        "message": f"API rate limit exceeded. Retry in {int(time_to_wait)} seconds.",
                        "retry_after": int(time_to_wait)
                    }), 429)
                    resp.headers["X-RateLimit-Limit"] = str(limit)
                    resp.headers["X-RateLimit-Remaining"] = "0"
                    resp.headers["X-RateLimit-Reset"] = str(reset_epoch)
                    resp.headers["Retry-After"] = str(int(max(1, time_to_wait)))
                    return resp

                response = make_response(f(*args, **kwargs))
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining_int)
                response.headers["X-RateLimit-Reset"] = str(reset_epoch)
                return response

            elif algorithm == "sliding_window":
                window_log = storage.get_sliding_window(key, limit=limit, window_seconds=window)
                allowed, remaining, retry_after = window_log.is_allowed()

                reset_epoch = int(now + retry_after) if not allowed else int(now + window)

                if not allowed:
                    resp = make_response(jsonify({
                        "error": "Too Many Requests",
                        "message": f"API rate limit exceeded. Retry in {int(retry_after)} seconds.",
                        "retry_after": int(retry_after)
                    }), 429)
                    resp.headers["X-RateLimit-Limit"] = str(limit)
                    resp.headers["X-RateLimit-Remaining"] = "0"
                    resp.headers["X-RateLimit-Reset"] = str(reset_epoch)
                    resp.headers["Retry-After"] = str(int(max(1, retry_after)))
                    return resp

                response = make_response(f(*args, **kwargs))
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(reset_epoch)
                return response

            return f(*args, **kwargs)
        return decorated
    return decorator
