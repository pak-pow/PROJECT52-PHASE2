const API_BASE_URL = 'http://127.0.0.1:5000/api';

export async function createShortLink(payload) {
    const response = await fetch(`${API_BASE_URL}/shorten`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || `HTTP Error: ${response.status}`);
    }

    return data;
}

export async function getStats() {
    const response = await fetch(`${API_BASE_URL}/stats`);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || `HTTP Error: ${response.status}`);
    }

    return data;
}

/**
 * Pings the backend health endpoint.
 * Returns true if the server is reachable, false otherwise.
 */
export async function checkHealth() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/health', {
            method: 'GET',
            // Short timeout so the banner appears quickly
            signal: AbortSignal.timeout(3000),
        });
        return response.ok;
    } catch {
        return false;
    }
}