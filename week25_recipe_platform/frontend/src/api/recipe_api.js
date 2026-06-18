import { API_URL } from '../config.js';

export async function fetchRecipes(page = 1, perPage = 12) {
    const response = await fetch(`${API_URL}/recipes?page=${page}&per_page=${perPage}`);
    if (!response.ok) throw new Error('Failed to fetch recipes');
    return await response.json(); // Returns { recipes, total, page, pages }
}

export async function createRecipe(formData) {
    const response = await fetch(`${API_URL}/recipes`, {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP Error: ${response.status}`);
    return data;
}

export async function updateRecipe(id, formData) {
    const response = await fetch(`${API_URL}/recipes/${id}`, {
        method: 'PUT',
        body: formData
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP Error: ${response.status}`);
    return data;
}

export async function deleteRecipe(id) {
    const response = await fetch(`${API_URL}/recipes/${id}`, {
        method: 'DELETE'
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Failed to delete recipe');
    return data;
}