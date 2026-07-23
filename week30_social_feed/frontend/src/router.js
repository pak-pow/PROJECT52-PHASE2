/**
 * router.js — Page navigation and view routing.
 */
import { getCurrentUser } from "./utils/state.js";

const pages = ["feed", "explore", "profile", "post-detail"];

export function showPage(name) {
    pages.forEach(p => {
        const el = document.getElementById(`page-${p}`);
        if (el) {
            el.classList.toggle("hidden", p !== name);
            el.classList.toggle("active", p === name);
        }
    });
    document.querySelectorAll(".nav-item").forEach(el => {
        el.classList.toggle("active", el.dataset.page === name);
    });
}

export function initRouter({ onNavigate }) {
    document.querySelectorAll(".nav-item").forEach(el => {
        el.addEventListener("click", (e) => {
            e.preventDefault();
            const page = el.dataset.page;
            const alreadyOnPage = document.getElementById(`page-${page}`)?.classList.contains("active");
            
            onNavigate({ page, alreadyOnPage, user: getCurrentUser() });
        });
    });

    const backBtn = document.getElementById("back-btn");
    if (backBtn) {
        backBtn.addEventListener("click", () => {
            showPage("feed");
        });
    }
}
