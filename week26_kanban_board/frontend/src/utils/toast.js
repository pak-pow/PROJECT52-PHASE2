import { escapeHtml } from './dom.js';

function getToastContainer() {
    let container = document.getElementById('toast-container');
    if(!container){
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container)
    }
    return container;
}

export function showToast(message, type = 'error'){
    const container = getToastContainer();
    const toast = document.createElement('div')

    const icon = type === 'error' ? 'alert-circle' : 'check-circle';
    const color = type === 'error' ? 'var(--danger)' : 'var(--accent)';

    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i data-lucide="${icon}" style="color: ${color}"></i>
        <span>${escapeHtml(message)}</span>    
    `;

    container.appendChild(toast)

    if (window.lucide) window.lucide.createIcons();
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}; 