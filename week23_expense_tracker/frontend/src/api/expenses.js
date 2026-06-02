import { apiClient } from './client.js';

export const ExpenseService = {
    getAll: async (page = 1, limit = 50) => {
        return await apiClient(`/expenses/?page=${page}&limit=${limit}`);
    },

    getSummary: async (month = null, year = null) => {
        let url = '/expenses/summary';
        const params = new URLSearchParams();
        if (month) params.append('month', month);
        if (year) params.append('year', year);
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }
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