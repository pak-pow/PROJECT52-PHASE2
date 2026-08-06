const API_BASE = "http://127.0.0.1:5000/api";

export async function fetchHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return await res.json();
}

export async function issueApiKey(tier = "free") {
    const res = await fetch(`${API_BASE}/auth/api-key`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tier })
    });
    return await res.json();
}

export async function sendBurstRequest(endpoint = "/data/burst-test", apiKey = "", queryParams = {}) {
    const headers = {};
    if (apiKey) headers["X-API-Key"] = apiKey;

    let url = `${API_BASE}${endpoint}`;
    const params = new URLSearchParams(queryParams).toString();
    if (params) url += `?${params}`;

    const res = await fetch(url, { method: "GET", headers });
    const data = await res.json().catch(() => ({}));
    
    return {
        status: res.status,
        ok: res.ok,
        data,
        headers: {
            limit: res.headers.get("X-RateLimit-Limit"),
            remaining: res.headers.get("X-RateLimit-Remaining"),
            reset: res.headers.get("X-RateLimit-Reset"),
            retryAfter: res.headers.get("Retry-After")
        }
    };
}
