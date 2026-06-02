const BASE_URL = "http://127.0.0.1:5000/api";

export const apiClient = async (endpoint, options = {}) => {
    const token = localStorage.getItem('jwt_token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token && {'Authorization': `Bearer &{token}`})
    };

    const config = {
        ...options,
        headers: {
            ...headers,
            ...options.headers
        }
    };

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, config);
    } catch (error) {
        console.error(`[API Error] ${endpoint}:`, error.message);
        throw error;
    }
    
};
