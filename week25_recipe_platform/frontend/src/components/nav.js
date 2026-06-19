/**
 * nav.js — builds and injects the shared top navigation bar.
 * Call initNav() once per page, passing the current page identifier.
 *
 * Usage:
 *   import { initNav } from '../components/nav.js';
 *   initNav('home');   // 'home' | 'browse' | 'manage'
 */

const PAGES = [
    { id: 'home',   label: 'Home',   href: 'home.html'   },
    { id: 'browse', label: 'Browse', href: 'browse.html' },
    { id: 'manage', label: 'Manage', href: 'manage.html' },
];

const NAV_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>`;

/**
 * Builds the shared nav and prepends it to <body>.
 * @param {'home'|'browse'|'manage'} activePage
 */
export function initNav(activePage) {
    const navLinks = PAGES.map(({ id, label, href }) => {
        const isActive = id === activePage;
        return `<a href="${href}" class="nav-link ${isActive ? 'nav-link-active' : ''}">${label}</a>`;
    }).join('');

    const nav = document.createElement('nav');
    nav.className = 'app-nav';
    nav.innerHTML = `
        <div class="nav-inner">
            <a href="home.html" class="nav-brand">
                ${NAV_ICON}
                <span>Recipe Hub</span>
            </a>
            <div class="nav-links">${navLinks}</div>
            <form class="nav-search-form" action="browse.html" method="get">
                <input
                    type="search"
                    name="search"
                    class="nav-search-input"
                    placeholder="Search recipes…"
                    aria-label="Search recipes"
                >
                <button type="submit" class="nav-search-btn" aria-label="Search">
                    <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                </button>
            </form>
        </div>
    `;

    // Insert at the very top of body
    document.body.prepend(nav);
}
