/**
 * Safely escapes strings to prevent XSS attacks in template literals.
 * @param {string} str 
 * @returns {string}
 */
export function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Helper to show an HTML dialog element by ID
 * @param {string} id 
 */
export function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.add('active');
    }
}

/**
 * Helper to hide an HTML dialog element by ID
 * @param {string} id 
 */
export function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Displays a non-blocking toast message.
 * @param {string} message 
 * @param {string} type - 'info' | 'error' | 'success'
 */
export function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type === 'error' ? 'toast-error' : ''}`;
    toast.innerHTML = `
        <i data-lucide="${type === 'error' ? 'alert-triangle' : 'info'}" style="width: 18px; height: 18px;"></i>
        <span>${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);

    if (window.lucide) {
        window.lucide.createIcons({
            attrs: { class: 'lucide-icon' },
            nameAttr: 'data-lucide',
            container: toast
        });
    }

    // Trigger visual slide-in
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Slide-out and remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}