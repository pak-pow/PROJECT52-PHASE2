from flask import request

def get_client_identifier() -> str:
    """Resolve client identifier from request headers (API key, Bearer token, or IP).
    
    Priority:
    1. Header `X-API-Key`
    2. Bearer Authorization token
    3. Header `X-Forwarded-For` (first proxy IP, sanitized)
    4. Remote Addr IP fallback
    """
    api_key = request.headers.get("X-API-Key")
    if api_key and api_key.strip():
        return f"apikey:{api_key.strip()}"

    auth_header = request.headers.get("Authorization", "")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if token:
            return f"token:{token}"

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded and forwarded.strip():
        # Handle multi-proxy chains "client_ip, proxy1_ip, proxy2_ip"
        client_ip = forwarded.split(",")[0].strip()
        if client_ip:
            return f"ip:{client_ip}"

    remote = request.remote_addr
    if remote and remote.strip():
        return f"ip:{remote.strip()}"

    return "ip:127.0.0.1"
