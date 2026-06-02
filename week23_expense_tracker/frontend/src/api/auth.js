import { apiClient } from './client.js';

export const AuthService = {
    login: async (username, password) => {
        const data = await apiClient('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        
        if (data && data.access_token) {
            localStorage.setItem('jwt_token', data.access_token);
        }
        return data;
    },

    register: async (username, password) => {
        return await apiClient('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    },

    getMe: async () => {
        return await apiClient('/auth/me');
    },

    logout: () => {
        localStorage.removeItem('jwt_token');
        window.location.href = '/login.html';
    },

    isAuthenticated: () => {
        return !!localStorage.getItem('jwt_token');
    }
};