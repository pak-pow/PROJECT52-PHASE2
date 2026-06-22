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