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

export const api = {
    getBoards: () => fetchAPI('/boards'),
    getBoard: (id) => fetchAPI(`/boards/${id}`),
    createBoard: (data) => fetchAPI('/boards', { method: 'POST', body: JSON.stringify(data) }),
    deleteBoard: (id) => fetchAPI(`/boards/${id}`, { method: 'DELETE' }),

    createColumn: (boardId, title) => fetchAPI(`/boards/${boardId}/columns`, { method: 'POST', body: JSON.stringify({ title }) }),
    updateColumn: (id, title) => fetchAPI(`/columns/${id}`, { method: 'PUT', body: JSON.stringify({ title }) }),
    deleteColumn: (id) => fetchAPI(`/columns/${id}`, { method: 'DELETE' }),
    reorderColumns: (boardId, updates) => fetchAPI(`/boards/${boardId}/columns/reorder`, { method: 'PATCH', body: JSON.stringify({ updates }) }),

    createCard: (columnId, data) => fetchAPI(`/columns/${columnId}/cards`, { method: 'POST', body: JSON.stringify(data) }),
    updateCard: (id, data) => fetchAPI(`/cards/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    deleteCard: (id) => fetchAPI(`/cards/${id}`, { method: 'DELETE' }),
    reorderCards: (columnId, updates) => fetchAPI(`/columns/${columnId}/cards/reorder`, { method: 'PATCH', body: JSON.stringify({ updates }) }),
    moveCard: (id, columnId, position) => fetchAPI(`/cards/${id}/move`, { method: 'PATCH', body: JSON.stringify({ columnId, position }) })
};