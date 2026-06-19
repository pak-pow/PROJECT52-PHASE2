/**
 * home.js — Home page controller.
 * Features:
 *   - Shared nav bar
 *   - Rotating hero (3 newest recipes, auto-advances every 5 s)
 *   - Category pills to filter the recipe grid
 *   - Paginated recipe grid with view modal
 */

import { fetchRecipes, fetchCategories } from '../api/recipe_api.js';
import { API_BASE }     from '../config.js';
import { initNav }      from '../components/nav.js';
import { buildCard }    from '../components/recipeCard.js';
import { showToast }    from '../components/toast.js';
import { escapeHtml, openModal, closeModal } from '../utils/dom.js';

// ============================================================
// State
// ============================================================
let currentPage     = 1;
const PER_PAGE      = 12;
let activeCategory  = 'all';
let heroRecipes     = [];
let heroIndex       = 0;
let heroTimer       = null;

// ============================================================
// DOM refs
// ============================================================
const hero        = document.getElementById('hero');
const indicators  = document.getElementById('hero-indicators');
const pillsRow    = document.getElementById('category-pills');
const grid        = document.getElementById('recipe-grid');
const pagination  = document.getElementById('pagination');

// View modal
const viewModal        = document.getElementById('view-modal');
const closeViewBtn     = document.getElementById('close-view-modal-btn');
const viewModalTitle   = document.getElementById('view-modal-title');
const viewModalImg     = document.getElementById('view-modal-img');
const viewModalDesc    = document.getElementById('view-modal-description');
const viewModalIngred  = document.getElementById('view-modal-ingredients');
const viewModalInstruct= document.getElementById('view-modal-instructions');

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
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !viewModal.classList.contains('hidden')) closeModal(viewModal);
});
// Close on backdrop click
viewModal.addEventListener('click', (e) => {
    if (e.target === viewModal) closeModal(viewModal);
});

// ============================================================
// Hero
// ============================================================
function buildHeroSlide(recipe, index) {
    const imgSrc = recipe.image_filename
        ? `${API_BASE}/uploads/${recipe.image_filename}`
        : null;

    const slide = document.createElement('div');
    slide.className = `hero-slide${index === 0 ? ' active' : ''}`;
    slide.innerHTML = `
        ${imgSrc
            ? `<img src="${escapeHtml(imgSrc)}" alt="${escapeHtml(recipe.title)}" class="hero-bg" onerror="this.parentElement.style.background='var(--surface-color)'">`
            : `<div class="hero-bg" style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%)"></div>`
        }
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <span class="hero-category">${escapeHtml(recipe.category || 'Recipe')}</span>
            <h2 class="hero-title">${escapeHtml(recipe.title)}</h2>
            <p class="hero-desc">${escapeHtml(recipe.description.slice(0, 140))}${recipe.description.length > 140 ? '…' : ''}</p>
            <button class="hero-btn" data-recipe-id="${recipe.id}">
                View Recipe
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </button>
        </div>
    `;
    slide.querySelector('.hero-btn').addEventListener('click', () => openViewModal(recipe));
    return slide;
}

function buildIndicatorDot(index) {
    const btn = document.createElement('button');
    btn.className = `hero-dot${index === 0 ? ' active' : ''}`;
    btn.setAttribute('aria-label', `Go to slide ${index + 1}`);
    btn.addEventListener('click', () => goToSlide(index));
    return btn;
}

function goToSlide(index) {
    const slides = hero.querySelectorAll('.hero-slide');
    const dots   = indicators.querySelectorAll('.hero-dot');
    slides[heroIndex]?.classList.remove('active');
    dots[heroIndex]?.classList.remove('active');
    heroIndex = index;
    slides[heroIndex]?.classList.add('active');
    dots[heroIndex]?.classList.add('active');
    resetHeroTimer();
}

function advanceHero() {
    goToSlide((heroIndex + 1) % heroRecipes.length);
}

function resetHeroTimer() {
    if (heroTimer) clearInterval(heroTimer);
    if (heroRecipes.length > 1) heroTimer = setInterval(advanceHero, 5000);
}

function buildHero(recipes) {
    heroRecipes = recipes.slice(0, 3);
    heroIndex   = 0;

    heroRecipes.forEach((r, i) => hero.insertBefore(buildHeroSlide(r, i), indicators));
    heroRecipes.forEach((_, i) => indicators.appendChild(buildIndicatorDot(i)));

    resetHeroTimer();
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
        btn.addEventListener('click', () => {
            pillsRow.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            activeCategory = cat;
            currentPage = 1;
            loadGrid();
        });
        pillsRow.appendChild(btn);
    });

    // "All" pill click
    pillsRow.querySelector('[data-category="all"]').addEventListener('click', (e) => {
        pillsRow.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
        e.currentTarget.classList.add('active');
        activeCategory = 'all';
        currentPage = 1;
        loadGrid();
    });
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

    try {
        const cat  = activeCategory === 'all' ? null : activeCategory;
        const data = await fetchRecipes(currentPage, PER_PAGE, cat);

        grid.innerHTML = '';
        if (data.recipes.length === 0) {
            grid.innerHTML = '<p class="text-muted">No recipes found in this category yet.</p>';
            return;
        }

        data.recipes.forEach(recipe =>
            grid.appendChild(buildCard(recipe, { onView: openViewModal }))
        );
        buildPagination(data.page, data.pages);

    } catch (err) {
        console.error(err);
        grid.innerHTML = '<p class="text-danger">Could not load recipes. Is Flask running?</p>';
    }
}

// ============================================================
// Init
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
    initNav('home');
    if (window.lucide) window.lucide.createIcons();

    // Load newest 3 recipes for hero
    try {
        const data = await fetchRecipes(1, 3);
        if (data.recipes.length) buildHero(data.recipes);
    } catch (_) { /* hero is optional */ }

    await buildPills();
    loadGrid();
});
