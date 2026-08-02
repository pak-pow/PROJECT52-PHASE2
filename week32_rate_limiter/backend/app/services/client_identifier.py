from flask import request

def get_client_identifier() -> str:
    """Resolve client identifier from request headers (API key, Bearer token, or IP).
    
    Priority:
    1. Header `X-API-Key`
    2. Bearer Authorization token
    3. Header `X-Forwarded-For` (first proxy IP)
    4. Remote Addr IP fallback
    """
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"apikey:{api_key.strip()}"

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if token:
            return f"token:{token}"

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
        return f"ip:{client_ip}"

    return f"ip:{request.remote_addr or '127.0.0.1'}"
