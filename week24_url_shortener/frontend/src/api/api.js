const API_BASE_URL = 'http://127.0.0.1:5000/api';

export async function createShortLink(payload) {
    const response = await fetch(`${API_BASE_URL}/shorten`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || `HTTP Error: ${response.status}`);
    }

    return data;
}