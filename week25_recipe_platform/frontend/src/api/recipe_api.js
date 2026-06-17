const API_BASE_URL = 'http://127.0.0.1:5000/api';

export async function fetchRecipes() {
    const response = await fetch(`${API_BASE_URL}/recipes`);
    if (!response.ok) throw new Error('Failed to fetch recipes');
    return await response.json();
}

export async function createRecipe(formData) {
    const response = await fetch(`${API_BASE_URL}/recipes`, {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP Error: ${response.status}`);
    return data;
}

export async function deleteRecipe(id) {
    const response = await fetch(`${API_BASE_URL}/recipes/${id}`, {
        method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete recipe');
    return await response.json();
}