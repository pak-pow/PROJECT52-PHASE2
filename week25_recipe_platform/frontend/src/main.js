import { fetchRecipes, createRecipe, updateRecipe, deleteRecipe } from './api/recipe_api.js';
import { API_BASE } from './config.js';

// ============================================================
// State
// ============================================================
let currentPage = 1;
const PER_PAGE   = 12;

// ============================================================
// DOM References
// ============================================================
const grid       = document.getElementById('recipe-grid');
const pagination = document.getElementById('pagination');

// Add modal
const modal     = document.getElementById('recipe-modal');
const addBtn    = document.getElementById('add-recipe-btn');
const closeBtn  = document.getElementById('close-modal-btn');
const form      = document.getElementById('add-recipe-form');
const submitBtn = document.getElementById('submit-recipe-btn');

// Edit modal
const editModal     = document.getElementById('edit-modal');
const closeEditBtn  = document.getElementById('close-edit-modal-btn');
const editForm      = document.getElementById('edit-recipe-form');
const submitEditBtn = document.getElementById('submit-edit-btn');

// View modal
const viewModal        = document.getElementById('view-modal');
const closeViewBtn     = document.getElementById('close-view-modal-btn');
const viewModalTitle   = document.getElementById('view-modal-title');
const viewModalImg     = document.getElementById('view-modal-img');
const viewModalDesc    = document.getElementById('view-modal-description');
const viewModalIngred  = document.getElementById('view-modal-ingredients');
const viewModalInstruct= document.getElementById('view-modal-instructions');
const viewEditBtn      = document.getElementById('view-edit-btn');
const viewDeleteBtn    = document.getElementById('view-delete-btn');

// Toast
const toast = document.getElementById('toast');

// ============================================================
// Utilities
// ============================================================

/**
 * Escapes HTML special characters to prevent XSS when inserting
 * untrusted data into innerHTML.
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = String(str ?? '');
    return div.innerHTML;
}

let toastTimer = null;
/**
 * Shows a non-blocking toast notification.
 * @param {string} message
 * @param {'success'|'error'} type
 */
function showToast(message, type = 'success') {
    if (toastTimer) clearTimeout(toastTimer);

    toast.textContent = message;
    toast.className = `toast toast-${type}`;  // removes 'hidden' and old type

    // Fade out after 3 seconds
    toastTimer = setTimeout(() => {
        toast.classList.add('toast-fade-out');
        setTimeout(() => {
            toast.className = 'toast hidden';
        }, 300);
    }, 3000);
}

// ============================================================
// Modal helpers
// ============================================================

function openModal(modalEl) {
    modalEl.classList.remove('hidden');
    // Focus the first input for accessibility
    const first = modalEl.querySelector('input, textarea');
    if (first) setTimeout(() => first.focus(), 50);
}

function closeModal(modalEl, formEl) {
    modalEl.classList.add('hidden');
    if (formEl) formEl.reset();
}

// Close any open modal on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        if (!modal.classList.contains('hidden'))     closeModal(modal, form);
        if (!editModal.classList.contains('hidden')) closeModal(editModal, editForm);
        if (!viewModal.classList.contains('hidden')) closeModal(viewModal, null);
    }
});

// ============================================================
// View Modal
// ============================================================

// Keeps a reference to the recipe currently shown in the view modal
// so the Edit/Delete buttons inside it can act on the right recipe.
let _viewRecipe = null;

function openViewModal(recipe) {
    _viewRecipe = recipe;

    const imgSrc = recipe.image_filename
        ? `${API_BASE}/uploads/${recipe.image_filename}`
        : 'https://placehold.co/680x300/0f172a/334155?text=No+Image';

    viewModalTitle.textContent    = recipe.title;
    viewModalImg.src              = imgSrc;
    viewModalImg.alt              = recipe.title;
    viewModalDesc.textContent     = recipe.description;
    viewModalIngred.textContent   = recipe.ingredients;
    viewModalInstruct.textContent = recipe.instructions;

    // onerror fallback
    viewModalImg.onerror = () => {
        viewModalImg.src = 'https://placehold.co/680x300/0f172a/334155?text=No+Image';
    };

    openModal(viewModal);
}

closeViewBtn.addEventListener('click', () => closeModal(viewModal, null));

// Edit from view modal: close view, open edit pre-filled
viewEditBtn.addEventListener('click', () => {
    if (!_viewRecipe) return;
    closeModal(viewModal, null);
    document.getElementById('edit-recipe-id').value        = _viewRecipe.id;
    document.getElementById('edit-title').value            = _viewRecipe.title;
    document.getElementById('edit-description').value      = _viewRecipe.description;
    document.getElementById('edit-ingredients').value      = _viewRecipe.ingredients;
    document.getElementById('edit-instructions').value     = _viewRecipe.instructions;
    openModal(editModal);
});

// Delete from view modal
viewDeleteBtn.addEventListener('click', async () => {
    if (!_viewRecipe) return;
    if (!confirm(`Delete "${_viewRecipe.title}"?`)) return;
    try {
        await deleteRecipe(_viewRecipe.id);
        closeModal(viewModal, null);
        showToast('Recipe deleted successfully.', 'success');
        loadGrid();
    } catch (err) {
        showToast(`Delete failed: ${err.message}`, 'error');
    }
});

// ============================================================
// Card Builder
// ============================================================

function buildCard(recipe) {
    const card = document.createElement('div');
    card.className = 'card';

    const imgSrc = recipe.image_filename
        ? `${API_BASE}/uploads/${recipe.image_filename}`
        : 'https://placehold.co/600x400/1e293b/94a3b8?text=No+Image';

    // All recipe fields are escaped before inserting into innerHTML (XSS fix)
    card.innerHTML = `
        <div class="card-actions">
            <button class="edit-btn"   data-id="${recipe.id}" aria-label="Edit ${escapeHtml(recipe.title)}">Edit</button>
            <button class="delete-btn" data-id="${recipe.id}" aria-label="Delete ${escapeHtml(recipe.title)}">Delete</button>
        </div>
        <img
            src="${escapeHtml(imgSrc)}"
            alt="${escapeHtml(recipe.title)}"
            class="card-img"
            onerror="this.src='https://placehold.co/600x400/1e293b/94a3b8?text=No+Image'"
        >
        <div class="card-title">${escapeHtml(recipe.title)}</div>
        <p class="card-desc">${escapeHtml(recipe.description)}</p>
    `;

    // Clicking the card body (not the action buttons) opens the view modal
    card.addEventListener('click', (e) => {
        if (e.target.closest('.card-actions')) return; // don't intercept Edit/Delete
        openViewModal(recipe);
    });

    // Delete handler
    card.querySelector('.delete-btn').addEventListener('click', async (e) => {
        e.stopPropagation(); // prevent card click
        const id = e.currentTarget.getAttribute('data-id');
        if (!confirm('Are you sure you want to delete this recipe?')) return;
        try {
            await deleteRecipe(id);
            showToast('Recipe deleted successfully.', 'success');
            loadGrid();
        } catch (err) {
            showToast(`Delete failed: ${err.message}`, 'error');
        }
    });

    // Edit handler — populate edit modal with current values
    card.querySelector('.edit-btn').addEventListener('click', (e) => {
        e.stopPropagation(); // prevent card click
        document.getElementById('edit-recipe-id').value        = recipe.id;
        document.getElementById('edit-title').value            = recipe.title;
        document.getElementById('edit-description').value      = recipe.description;
        document.getElementById('edit-ingredients').value      = recipe.ingredients;
        document.getElementById('edit-instructions').value     = recipe.instructions;
        openModal(editModal);
    });

    return card;
}

// ============================================================
// Pagination Builder
// ============================================================

function buildPagination(page, pages) {
    if (pages <= 1) {
        pagination.classList.add('hidden');
        return;
    }

    pagination.classList.remove('hidden');
    pagination.innerHTML = `
        <button class="pagination-btn" id="prev-btn" ${page <= 1 ? 'disabled' : ''}>← Prev</button>
        <span class="pagination-info">Page ${page} of ${pages}</span>
        <button class="pagination-btn" id="next-btn" ${page >= pages ? 'disabled' : ''}>Next →</button>
    `;

    pagination.querySelector('#prev-btn').addEventListener('click', () => {
        currentPage--;
        loadGrid();
    });
    pagination.querySelector('#next-btn').addEventListener('click', () => {
        currentPage++;
        loadGrid();
    });
}

// ============================================================
// Grid Loader
// ============================================================

async function loadGrid() {
    grid.innerHTML = '<p class="text-muted">Loading recipes...</p>';
    pagination.classList.add('hidden');

    try {
        const data = await fetchRecipes(currentPage, PER_PAGE);
        // data = { recipes, total, page, pages }
        grid.innerHTML = '';

        if (data.recipes.length === 0) {
            grid.innerHTML = '<p class="text-muted">No recipes found. Add one!</p>';
            return;
        }

        data.recipes.forEach(recipe => grid.appendChild(buildCard(recipe)));
        buildPagination(data.page, data.pages);

    } catch (error) {
        console.error(error);
        grid.innerHTML = '<p class="text-danger">Failed to load server data. Is Flask running?</p>';
    }
}

// ============================================================
// Add Modal Events
// ============================================================

addBtn.addEventListener('click', () => openModal(modal));
closeBtn.addEventListener('click', () => closeModal(modal, form));

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitBtn.textContent = 'Uploading...';
    submitBtn.disabled    = true;

    try {
        await createRecipe(new FormData(form));
        closeModal(modal, form);
        currentPage = 1; // jump to first page to see new recipe
        loadGrid();
        showToast('Recipe added successfully! 🎉', 'success');
    } catch (error) {
        console.error('Upload failed:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        submitBtn.textContent = 'Save Recipe';
        submitBtn.disabled    = false;
    }
});

// ============================================================
// Edit Modal Events
// ============================================================

closeEditBtn.addEventListener('click', () => closeModal(editModal, editForm));

editForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitEditBtn.textContent = 'Saving...';
    submitEditBtn.disabled    = true;

    const id = document.getElementById('edit-recipe-id').value;

    try {
        await updateRecipe(id, new FormData(editForm));
        closeModal(editModal, editForm);
        loadGrid();
        showToast('Recipe updated successfully! ✏️', 'success');
    } catch (error) {
        console.error('Update failed:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        submitEditBtn.textContent = 'Update Recipe';
        submitEditBtn.disabled    = false;
    }
});

// ============================================================
// Init
// ============================================================

document.addEventListener('DOMContentLoaded', () => loadGrid());