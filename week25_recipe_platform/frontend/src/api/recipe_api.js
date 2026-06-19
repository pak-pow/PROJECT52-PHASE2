import { API_BASE } from '../config.js';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Centralized fetch wrapper. Throws a descriptive Error on non-OK responses.
 * @param {string} url
 * @param {RequestInit} options
 * @returns {Promise<any>}
 */
async function apiFetch(url, options = {}) {
    const res = await fetch(url, options);
    if (!res.ok) {
        let msg = `HTTP ${res.status}`;
        try {
            const json = await res.json();
            msg = json.error || msg;
        } catch (_) {/* body wasn't JSON */}
        throw new Error(msg);
    }
    return res.json();
}

// ---------------------------------------------------------------------------
// Recipes
// ---------------------------------------------------------------------------

/**
 * Fetches a paginated list of recipes with optional filters.
 * @param {number} page
 * @param {number} perPage
 * @param {string|null} category  — null or 'all' to fetch all categories
 * @param {string|null} search    — search term for title/description
 * @returns {Promise<{recipes, total, page, per_page, pages}>}
 */
export async function fetchRecipes(page = 1, perPage = 12, category = null, search = null) {
    const params = new URLSearchParams({ page, per_page: perPage });
    if (category && category.toLowerCase() !== 'all') params.set('category', category);
    if (search)    params.set('search', search);
    return apiFetch(`${API_BASE}/api/recipes?${params}`);
}

/**
 * Fetches a single recipe by ID.
 * @param {number|string} id
 */
export async function fetchRecipeById(id) {
    return apiFetch(`${API_BASE}/api/recipes/${id}`);
}

/**
 * Creates a new recipe. Expects a FormData object.
 * @param {FormData} formData
 */
export async function createRecipe(formData) {
    return apiFetch(`${API_BASE}/api/recipes`, { method: 'POST', body: formData });
}

/**
 * Updates an existing recipe. Expects a FormData object.
 * @param {number|string} id
 * @param {FormData} formData
 */
export async function updateRecipe(id, formData) {
    return apiFetch(`${API_BASE}/api/recipes/${id}`, { method: 'PUT', body: formData });
}

/**
 * Deletes a recipe by ID.
 * @param {number|string} id
 */
export async function deleteRecipe(id) {
    return apiFetch(`${API_BASE}/api/recipes/${id}`, { method: 'DELETE' });
}

// ---------------------------------------------------------------------------
// Categories
// ---------------------------------------------------------------------------

/**
 * Fetches the list of distinct categories that have at least one recipe.
 * @returns {Promise<string[]>}
 */
export async function fetchCategories() {
    const data = await apiFetch(`${API_BASE}/api/categories`);
    return data.categories;
}