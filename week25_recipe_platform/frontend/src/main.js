import { fetchRecipes, deleteRecipe } from './api/recipe_api.js';
import { fetchRecipes, createRecipe, deleteRecipe } from './api/recipe_api.js';

document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('recipe-grid');

    async function loadGrid() {
        grid.innerHTML = '<p class="text-muted">Loading recipes...</p>';
        try {
            const recipes = await fetchRecipes();
            grid.innerHTML = ''; // Clear loading state

            if (recipes.length === 0) {
                grid.innerHTML = '<p class="text-muted">No recipes found. Add one!</p>';
                return;
            }

            recipes.forEach(recipe => {
                const card = document.createElement('div');
                card.className = 'card';
                
                const imgSrc = recipe.image_filename 
                    ? `http://127.0.0.1:5000/uploads/${recipe.image_filename}` 
                    : 'https://placehold.co/600x400/1e293b/94a3b8?text=No+Image';

                card.innerHTML = `
                    <button class="delete-btn" data-id="${recipe.id}">Delete</button>
                    <img src="${imgSrc}" alt="${recipe.title}" class="card-img">
                    <div class="card-title">${recipe.title}</div>
                    <p class="card-desc">${recipe.description}</p>
                `;
                
                grid.appendChild(card);
            });

            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = e.target.getAttribute('data-id');
                    if (confirm('Are you sure you want to delete this recipe?')) {
                        await deleteRecipe(id);
                        loadGrid(); 
                    }
                });
            });

        } catch (error) {
            console.error(error);
            grid.innerHTML = '<p class="text-danger">Failed to load server data. Is Flask running?</p>';
        }
    }

    loadGrid();
    const modal = document.getElementById('recipe-modal');
    const addBtn = document.getElementById('add-recipe-btn');
    const closeBtn = document.getElementById('close-modal-btn');
    const form = document.getElementById('add-recipe-form');
    const submitBtn = document.getElementById('submit-recipe-btn');

    addBtn.addEventListener('click', () => {
        modal.classList.remove('hidden');
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
        form.reset(); 
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        submitBtn.textContent = 'Uploading...';
        submitBtn.disabled = true;

        try {
            const payload = new FormData(form);
            await createRecipe(payload);
            
            modal.classList.add('hidden');
            form.reset();
            loadGrid();
            
        } catch (error) {
            console.error("Upload failed:", error);
            alert(`Error: ${error.message}`);
        } finally {
            submitBtn.textContent = 'Save Recipe';
            submitBtn.disabled = false;
        }
    });
});