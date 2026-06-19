/**
 * manage.js — Manage page controller (Add / Edit / Delete recipes).
 * This is the evolved version of the original main.js.
 * Uses shared components: nav, recipeCard, toast, dom utils.
 */

import { fetchRecipes, createRecipe, updateRecipe, deleteRecipe } from '../api/recipe_api.js';
import { API_BASE }     from '../config.js';
import { initNav }      from '../components/nav.js';
import { buildCard }    from '../components/recipeCard.js';
import { showToast }    from '../components/toast.js';
import { escapeHtml, openModal, closeModal } from '../utils/dom.js';

// ============================================================
// State
// ============================================================
let currentPage = 1;
const PER_PAGE  = 12;
let _viewRecipe = null;

// ============================================================
// DOM refs
// ============================================================
const grid = document.getElementById('recipe-grid');
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
const viewModal         = document.getElementById('view-modal');
const closeViewBtn      = document.getElementById('close-view-modal-btn');
const viewModalTitle    = document.getElementById('view-modal-title');
const viewModalImg      = document.getElementById('view-modal-img');
const viewModalDesc     = document.getElementById('view-modal-description');
const viewModalIngred   = document.getElementById('view-modal-ingredients');
const viewModalInstruct = document.getElementById('view-modal-instructions');
const viewEditBtn       = document.getElementById('view-edit-btn');
const viewDeleteBtn     = document.getElementById('view-delete-btn');

// ============================================================
// Escape key closes any open modal
// ============================================================
document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (!modal.classList.contains('hidden'))     closeModal(modal, form);
    if (!editModal.classList.contains('hidden')) closeModal(editModal, editForm);
    if (!viewModal.classList.contains('hidden')) closeModal(viewModal);
});

// Close on backdrop click
[modal, editModal, viewModal].forEach(m => {
    m.addEventListener('click', (e) => { if (e.target === m) closeModal(m); });
});

// ============================================================
// View Modal
// ============================================================
function openViewModal(recipe) {
    _viewRecipe = recipe;
    const imgSrc = recipe.image_filename
        ? `${API_BASE}/uploads/${recipe.image_filename}`
        : 'https://placehold.co/680x300/0f172a/334155?text=No+Image';

    viewModalTitle.textContent     = recipe.title;
    viewModalImg.src               = imgSrc;
    viewModalImg.alt               = recipe.title;
    viewModalDesc.textContent      = recipe.description;
    viewModalIngred.textContent    = recipe.ingredients;
    viewModalInstruct.textContent  = recipe.instructions;
    viewModalImg.onerror = () => { viewModalImg.src = 'https://placehold.co/680x300/0f172a/334155?text=No+Image'; };

    openModal(viewModal);
    if (window.lucide) window.lucide.createIcons();
}

closeViewBtn.addEventListener('click', () => closeModal(viewModal));

// Edit from view modal
viewEditBtn.addEventListener('click', () => {
    if (!_viewRecipe) return;
    closeModal(viewModal);
    prefillEditModal(_viewRecipe);
    openModal(editModal);
});

// Delete from view modal
viewDeleteBtn.addEventListener('click', async () => {
    if (!_viewRecipe) return;
    if (!confirm(`Delete "${_viewRecipe.title}"?`)) return;
    try {
        await deleteRecipe(_viewRecipe.id);
        closeModal(viewModal);
        showToast('Recipe deleted.', 'success');
        loadGrid();
    } catch (err) {
        showToast(`Delete failed: ${err.message}`, 'error');
    }
});

// ============================================================
// Pagination
// ============================================================
const CHEV_L = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>`;
const CHEV_R = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>`;

function buildPagination(page, pages) {
    if (pages <= 1) { pagination.classList.add('hidden'); return; }
    pagination.classList.remove('hidden');
    pagination.innerHTML = `
        <button class="pagination-btn" id="prev-btn" ${page <= 1 ? 'disabled' : ''}>${CHEV_L} Prev</button>
        <span class="pagination-info">Page ${page} of ${pages}</span>
        <button class="pagination-btn" id="next-btn" ${page >= pages ? 'disabled' : ''}>Next ${CHEV_R}</button>
    `;
    pagination.querySelector('#prev-btn').addEventListener('click', () => { currentPage--; loadGrid(); });
    pagination.querySelector('#next-btn').addEventListener('click', () => { currentPage++; loadGrid(); });
}

// ============================================================
// Grid Loader
// ============================================================
async function loadGrid() {
    grid.innerHTML = '<p class="text-muted">Loading…</p>';
    pagination.classList.add('hidden');

    try {
        const data = await fetchRecipes(currentPage, PER_PAGE);
        grid.innerHTML = '';

        if (data.recipes.length === 0) {
            grid.innerHTML = '<p class="text-muted">No recipes yet. Add your first one!</p>';
            return;
        }

        data.recipes.forEach(recipe => grid.appendChild(
            buildCard(recipe, {
                showActions: true,
                onView:   (r) => openViewModal(r),
                onEdit:   (r) => { prefillEditModal(r); openModal(editModal); },
                onDelete: (r) => handleDelete(r),
            })
        ));
        buildPagination(data.page, data.pages);

    } catch (err) {
        console.error(err);
        grid.innerHTML = '<p class="text-danger">Could not load recipes. Is Flask running?</p>';
    }
}

// ============================================================
// Add Modal
// ============================================================
addBtn.addEventListener('click', () => openModal(modal));
closeBtn.addEventListener('click', () => closeModal(modal, form));

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitBtn.textContent = 'Uploading…';
    submitBtn.disabled    = true;

    try {
        await createRecipe(new FormData(form));
        closeModal(modal, form);
        currentPage = 1;
        loadGrid();
        showToast('Recipe added successfully!', 'success');
    } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
    } finally {
        submitBtn.textContent = 'Save Recipe';
        submitBtn.disabled    = false;
    }
});

// ============================================================
// Edit Modal
// ============================================================
function prefillEditModal(recipe) {
    document.getElementById('edit-recipe-id').value    = recipe.id;
    document.getElementById('edit-title').value        = recipe.title;
    document.getElementById('edit-description').value  = recipe.description;
    document.getElementById('edit-ingredients').value  = recipe.ingredients;
    document.getElementById('edit-instructions').value = recipe.instructions;
    // Set category dropdown
    const catSelect = document.getElementById('edit-category');
    if (catSelect) catSelect.value = recipe.category || 'Uncategorised';
}

closeEditBtn.addEventListener('click', () => closeModal(editModal, editForm));

editForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitEditBtn.textContent = 'Saving…';
    submitEditBtn.disabled    = true;

    const id = document.getElementById('edit-recipe-id').value;

    try {
        await updateRecipe(id, new FormData(editForm));
        closeModal(editModal, editForm);
        loadGrid();
        showToast('Recipe updated!', 'success');
    } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
    } finally {
        submitEditBtn.textContent = 'Update Recipe';
        submitEditBtn.disabled    = false;
    }
});

// ============================================================
// Delete
// ============================================================
async function handleDelete(recipe) {
    if (!confirm(`Delete "${recipe.title}"?`)) return;
    try {
        await deleteRecipe(recipe.id);
        showToast('Recipe deleted.', 'success');
        loadGrid();
    } catch (err) {
        showToast(`Delete failed: ${err.message}`, 'error');
    }
}

// ============================================================
// Init
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initNav('manage');
    if (window.lucide) window.lucide.createIcons();
    loadGrid();
});
