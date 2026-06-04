import { apiClient } from './client.js';

export const ExpenseService = {
    getAll: async (filters = {}) => {
        // Build the query string (e.g., ?start_date=2026-06-01&category=Food)
        const queryParams = new URLSearchParams(filters).toString();
        const url = queryParams ? `/expenses/?${queryParams}` : '/expenses/';
        return await apiClient(url);
    },

    getSummary: async (filters = {}) => {
        const queryParams = new URLSearchParams({
            ...(filters.start_date && { start_date: filters.start_date }),
            ...(filters.end_date && { end_date: filters.end_date })
        }).toString();
        
        const url = queryParams ? `/expenses/summary?${queryParams}` : '/expenses/summary';
        return await apiClient(url);
    },

    create: async (expenseData) => {
        return await apiClient('/expenses/', {
            method: 'POST',
            body: JSON.stringify(expenseData)
        });
    },

    update: async (id, expenseData) => {
        return await apiClient(`/expenses/${id}`, {
            method: 'PUT',
            body: JSON.stringify(expenseData)
        });
    },

    delete: async (id) => {
        return await apiClient(`/expenses/${id}`, {
            method: 'DELETE'
        });
    }
};