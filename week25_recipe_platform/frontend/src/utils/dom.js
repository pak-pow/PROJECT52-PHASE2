/**
 * dom.js — shared DOM helpers used across all pages.
 */

/**
 * Escapes HTML special characters to prevent XSS when inserting
 * untrusted data into innerHTML.
 * @param {any} str
 * @returns {string}
 */
export function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = String(str ?? '');
    return div.innerHTML;
}

/**
 * Shows a modal overlay and focuses the first input.
 * @param {HTMLElement} modalEl
 */
export function openModal(modalEl) {
    modalEl.classList.remove('hidden');
    const first = modalEl.querySelector('input, textarea, select');
    if (first) setTimeout(() => first.focus(), 50);
}

/**
 * Hides a modal overlay and resets its form if provided.
 * @param {HTMLElement} modalEl
 * @param {HTMLFormElement|null} formEl
 */
export function closeModal(modalEl, formEl = null) {
    modalEl.classList.add('hidden');
    if (formEl) formEl.reset();
}
