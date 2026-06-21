const API_BASE = 'http://127.0.0.1:5000/api';

async function fetchAPI(endpoint, options = {}) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        }
    });

    if(!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || `API Error: ${res.status}`)
    }

    if (res.status == 200) return null
    return res.json();
}