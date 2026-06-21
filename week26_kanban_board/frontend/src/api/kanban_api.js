const API_BASE_URL = 'http://127.0.0.1:5000/api';

/**
 * Helper to execute fetch requests and handle response errors cleanly.
 */
async function request(path, options = {}) {
    const url = `${API_BASE_URL}${path}`;
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    try {
        const response = await fetch(url, config);
        
        if (response.status === 204) {
            return null;
        }

        const data = await response.get_json ? await response.get_json() : await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! Status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error(`API Request Failed on ${url}:`, error);
        throw error;
    }
}

export const api = {
    // ----------------------------------------------------
    // Board Endpoints
    // ----------------------------------------------------
    async getBoards() {
        return request('/boards');
    },

    async getBoard(id) {
        return request(`/boards/${id}`);
    },

    async createBoard(boardData) {
        return request('/boards', {
            method: 'POST',
            body: boardData,
        });
    },

    async updateBoard(id, boardData) {
        return request(`/boards/${id}`, {
            method: 'PUT',
            body: boardData,
        });
    },

    async deleteBoard(id) {
        return request(`/boards/${id}`, {
            method: 'DELETE',
        });
    },

    // ----------------------------------------------------
    // Column Endpoints
    // ----------------------------------------------------
    async getColumns(boardId) {
        return request(`/boards/${boardId}/columns`);
    },

    async createColumn(boardId, title) {
        return request(`/boards/${boardId}/columns`, {
            method: 'POST',
            body: { title },
        });
    },

    async updateColumn(columnId, title) {
        return request(`/columns/${columnId}`, {
            method: 'PUT',
            body: { title },
        });
    },

    async deleteColumn(columnId) {
        return request(`/columns/${columnId}`, {
            method: 'DELETE',
        });
    },

    async reorderColumns(boardId, updates) {
        return request(`/boards/${boardId}/columns/reorder`, {
            method: 'PATCH',
            body: { updates },
        });
    },

    // ----------------------------------------------------
    // Card Endpoints
    // ----------------------------------------------------
    async getCards(columnId) {
        return request(`/columns/${columnId}/cards`);
    },

    async getCard(cardId) {
        return request(`/cards/${cardId}`);
    },

    async createCard(columnId, cardData) {
        return request(`/columns/${columnId}/cards`, {
            method: 'POST',
            body: cardData,
        });
    },

    async updateCard(cardId, cardData) {
        return request(`/cards/${cardId}`, {
            method: 'PUT',
            body: cardData,
        });
    },

    async deleteCard(cardId) {
        return request(`/cards/${cardId}`, {
            method: 'DELETE',
        });
    },

    async reorderCards(columnId, updates) {
        return request(`/columns/${columnId}/cards/reorder`, {
            method: 'PATCH',
            body: { updates },
        });
    },

    async moveCard(cardId, columnId, position) {
        return request(`/cards/${cardId}/move`, {
            method: 'PATCH',
            body: { column_id: columnId, position },
        });
    },
};