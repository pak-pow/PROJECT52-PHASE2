/**
 * browse.js — Browse/Discover page controller.
 * Features:
 *   - Pre-fills search from URL ?search= param (from nav search)
 *   - Category pills (loaded from API)
 *   - Sort dropdown (newest / oldest / A-Z — client-side after fetch)
 *   - Paginated recipe grid with view modal
 *   - Live results count
 */

import { fetchRecipes, fetchCategories } from '../api/recipe_api.js';
import { API_BASE }     from '../config.js';
import { initNav }      from '../components/nav.js';
import { buildCard }    from '../components/recipeCard.js';
import { escapeHtml, openModal, closeModal } from '../utils/dom.js';

// ============================================================
// State
// ============================================================
let currentPage    = 1;
const PER_PAGE     = 12;
let activeCategory = 'all';
let activeSearch   = '';
let activeSort     = 'newest';

// ============================================================
// DOM refs
// ============================================================
const pillsRow      = document.getElementById('category-pills');
const searchForm    = document.getElementById('browse-search-form');
const searchInput   = document.getElementById('browse-search-input');
const sortSelect    = document.getElementById('sort-select');
const grid          = document.getElementById('recipe-grid');
const pagination    = document.getElementById('pagination');
const resultsCount  = document.getElementById('results-count');

// View modal
const viewModal         = document.getElementById('view-modal');
const closeViewBtn      = document.getElementById('close-view-modal-btn');
const viewModalTitle    = document.getElementById('view-modal-title');
const viewModalImg      = document.getElementById('view-modal-img');
const viewModalDesc     = document.getElementById('view-modal-description');
const viewModalIngred   = document.getElementById('view-modal-ingredients');
const viewModalInstruct = document.getElementById('view-modal-instructions');

// ============================================================
// View Modal
// ============================================================
function openViewModal(recipe) {
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
viewModal.addEventListener('click', (e) => { if (e.target === viewModal) closeModal(viewModal); });
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !viewModal.classList.contains('hidden')) closeModal(viewModal);
});

// ============================================================
// Sorting (client-side, applied after fetch)
// ============================================================
function sortRecipes(recipes, sort) {
    const clone = [...recipes];
    if (sort === 'oldest') return clone.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    if (sort === 'az')     return clone.sort((a, b) => a.title.localeCompare(b.title));
    return clone; // 'newest' is default API order
}

// ============================================================
// Category Pills
// ============================================================
async function buildPills() {
    const categories = await fetchCategories();
    categories.forEach(cat => {
        const btn = document.createElement('button');
        btn.className = 'pill';
        btn.dataset.category = cat;
        btn.textContent = cat;
        btn.setAttribute('role', 'tab');
        btn.addEventListener('click', () => selectPill(btn, cat));
        pillsRow.appendChild(btn);
    });

    pillsRow.querySelector('[data-category="all"]').addEventListener('click', (e) => {
        selectPill(e.currentTarget, 'all');
    });
}

function selectPill(pillEl, category) {
    pillsRow.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
    pillEl.classList.add('active');
    activeCategory = category;
    currentPage = 1;
    loadGrid();
}

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
    resultsCount.textContent = '';

    try {
        const cat    = activeCategory === 'all' ? null : activeCategory;
        const search = activeSearch.trim() || null;

        const data = await fetchRecipes(currentPage, PER_PAGE, cat, search);
        const sorted = sortRecipes(data.recipes, activeSort);

        grid.innerHTML = '';

        if (sorted.length === 0) {
            const noun = search ? `"${search}"` : 'this category';
            grid.innerHTML = `<p class="text-muted">No recipes found for ${escapeHtml(noun)}. Try a different search.</p>`;
            resultsCount.textContent = '0 results';
            return;
        }

        sorted.forEach(recipe => grid.appendChild(buildCard(recipe, { onView: openViewModal })));
        buildPagination(data.page, data.pages);

        const from = (data.page - 1) * data.per_page + 1;
        const to   = Math.min(data.page * data.per_page, data.total);
        resultsCount.textContent = `Showing ${from}–${to} of ${data.total} recipe${data.total !== 1 ? 's' : ''}`;

    } catch (err) {
        console.error(err);
        grid.innerHTML = '<p class="text-danger">Could not load recipes. Is Flask running?</p>';
    }
}

// ============================================================
// Event Listeners
// ============================================================
searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    activeSearch = searchInput.value.trim();
    currentPage  = 1;
    // Update URL without page reload for shareability
    const url = new URL(window.location.href);
    if (activeSearch) url.searchParams.set('search', activeSearch);
    else url.searchParams.delete('search');
    window.history.replaceState({}, '', url.toString());
    loadGrid();
});

sortSelect.addEventListener('change', (e) => {
    activeSort = e.target.value;
    loadGrid();
});

// ============================================================
// Init
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
    initNav('browse');
    if (window.lucide) window.lucide.createIcons();

    // Pre-fill search from URL param (set by nav search form)
    const urlSearch = new URLSearchParams(window.location.search).get('search') || '';
    if (urlSearch) {
        activeSearch        = urlSearch;
        searchInput.value   = urlSearch;
    }

    await buildPills();
    loadGrid();
});
