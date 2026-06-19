/**
 * toast.js — shared toast notification component.
 * Expects a <div id="toast"> in the page HTML.
 */

const ICON = {
    success: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
    error:   `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
};

let _toastEl = null;
let _timer   = null;

function getToast() {
    if (!_toastEl) _toastEl = document.getElementById('toast');
    return _toastEl;
}

/**
 * Shows a non-blocking toast notification at the bottom of the screen.
 * @param {string} message
 * @param {'success'|'error'} type
 * @param {number} durationMs
 */
export function showToast(message, type = 'success', durationMs = 3000) {
    const toast = getToast();
    if (!toast) { console.warn('showToast: no #toast element found'); return; }

    if (_timer) clearTimeout(_timer);

    toast.innerHTML = `${ICON[type] ?? ''} <span>${message}</span>`;
    toast.className = `toast toast-${type}`;

    _timer = setTimeout(() => {
        toast.classList.add('toast-fade-out');
        setTimeout(() => { toast.className = 'toast hidden'; }, 300);
    }, durationMs);
}
