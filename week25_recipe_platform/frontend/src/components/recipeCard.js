/**
 * recipeCard.js — shared recipe card builder used by all three pages.
 * Requires: API_BASE from config.js, escapeHtml from utils/dom.js
 */

import { API_BASE } from '../config.js';
import { escapeHtml } from '../utils/dom.js';
import { truncate }   from '../utils/formatters.js';

const ICON = {
    pencil: `<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>`,
    trash:  `<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>`,
};

const PLACEHOLDER = 'https://placehold.co/600x400/1e293b/94a3b8?text=No+Image';

/**
 * Builds a recipe card element.
 *
 * @param {object} recipe   — recipe data object from the API
 * @param {object} options
 * @param {boolean} options.showActions  — show Edit/Delete buttons (default: false)
 * @param {function} options.onView      — called with (recipe) when card body is clicked
 * @param {function} options.onEdit      — called with (recipe) when Edit is clicked
 * @param {function} options.onDelete    — called with (recipe) when Delete is clicked
 * @returns {HTMLElement}
 */
export function buildCard(recipe, options = {}) {
    const { showActions = false, onView = null, onEdit = null, onDelete = null } = options;

    const imgSrc = recipe.image_filename
        ? `${API_BASE}/uploads/${recipe.image_filename}`
        : PLACEHOLDER;

    const card = document.createElement('div');
    card.className = 'card';

    card.innerHTML = `
        ${showActions ? `
        <div class="card-actions">
            <button class="edit-btn"   data-id="${recipe.id}">${ICON.pencil} Edit</button>
            <button class="delete-btn" data-id="${recipe.id}">${ICON.trash} Delete</button>
        </div>` : ''}
        <img
            src="${escapeHtml(imgSrc)}"
            alt="${escapeHtml(recipe.title)}"
            class="card-img"
            onerror="this.src='${PLACEHOLDER}'"
        >
        <div class="card-meta">
            <span class="card-category">${escapeHtml(recipe.category || 'Uncategorised')}</span>
        </div>
        <div class="card-title">${escapeHtml(recipe.title)}</div>
        <p class="card-desc">${escapeHtml(truncate(recipe.description, 110))}</p>
    `;

    // Card body click → view modal
    if (onView) {
        card.addEventListener('click', (e) => {
            if (e.target.closest('.card-actions')) return;
            onView(recipe);
        });
        card.style.cursor = 'pointer';
    }

    if (showActions) {
        card.querySelector('.edit-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            if (onEdit) onEdit(recipe);
        });
        card.querySelector('.delete-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            if (onDelete) onDelete(recipe);
        });
    }

    return card;
}
