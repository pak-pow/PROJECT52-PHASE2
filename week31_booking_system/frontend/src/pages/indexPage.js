import { renderNavbar } from "../components/navbar.js";
import { apiFetchServices } from "../api/serviceApi.js";
import { escapeHtml, formatCurrency, showToast } from "../utils/helpers.js";

let currentCategory = "";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar();
    initFilters();
    loadServices();
});

function initFilters() {
    const filterBar = document.getElementById("filter-bar");
    if (!filterBar) return;

    filterBar.addEventListener("click", (e) => {
        const btn = e.target.closest(".filter-btn");
        if (!btn) return;

        document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        currentCategory = btn.dataset.category || "";
        loadServices();
    });
}

async function loadServices() {
    const grid = document.getElementById("services-grid");
    if (!grid) return;

    grid.innerHTML = `
        <div class="service-card skeleton" style="height: 220px;"></div>
        <div class="service-card skeleton" style="height: 220px;"></div>
        <div class="service-card skeleton" style="height: 220px;"></div>
    `;

    try {
        const services = await apiFetchServices(currentCategory);
        if (services.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</div>
                    <p>No services found in this category.</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = services.map(s => `
            <div class="service-card" data-service-id="${s.id}">
                <div>
                    <span class="card-badge">${escapeHtml(s.category)}</span>
                    <h3 class="service-title">${escapeHtml(s.title)}</h3>
                    <p class="service-desc">${escapeHtml(s.description)}</p>
                </div>
                <div class="service-meta">
                    <div>
                        <div class="service-price">${formatCurrency(s.price)}</div>
                        <div class="service-duration">⏱️ ${s.duration_minutes} mins</div>
                    </div>
                    <a href="book.html?service_id=${s.id}" class="btn-primary">Book Now ➔</a>
                </div>
            </div>
        `).join("");
    } catch (err) {
        showToast(err.message, "error");
        grid.innerHTML = `<p style="color: var(--danger);">Failed to load services.</p>`;
    }
}
