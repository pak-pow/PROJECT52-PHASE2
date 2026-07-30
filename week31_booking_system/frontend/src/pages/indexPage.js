import { renderNavbar } from "../components/navbar.js";
import { apiFetchServices } from "../api/serviceApi.js";
import { escapeHtml, formatCurrency, showToast } from "../utils/helpers.js";

let allServices = [];
let currentCategory = "";
let searchQuery = "";
let sortOrder = "default";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar();
    initControls();
    loadServices();
});

function initControls() {
    // Category filter bar
    const filterBar = document.getElementById("filter-bar");
    if (filterBar) {
        filterBar.addEventListener("click", (e) => {
            const btn = e.target.closest(".filter-btn");
            if (!btn) return;

            document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            currentCategory = btn.dataset.category || "";
            loadServices();
        });
    }

    // Real-time Search Input
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            searchQuery = e.target.value.toLowerCase().trim();
            renderFilteredServices();
        });
    }

    // Sort Dropdown
    const sortSelect = document.getElementById("sort-select");
    if (sortSelect) {
        sortSelect.addEventListener("change", (e) => {
            sortOrder = e.target.value;
            renderFilteredServices();
        });
    }
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
        allServices = await apiFetchServices(currentCategory);
        renderFilteredServices();
    } catch (err) {
        showToast(err.message, "error");
        grid.innerHTML = `<p style="color: var(--danger);">Failed to load services.</p>`;
    }
}

function renderFilteredServices() {
    const grid = document.getElementById("services-grid");
    if (!grid) return;

    let filtered = [...allServices];

    // Apply text search
    if (searchQuery) {
        filtered = filtered.filter(s => 
            s.title.toLowerCase().includes(searchQuery) ||
            s.description.toLowerCase().includes(searchQuery) ||
            s.category.toLowerCase().includes(searchQuery)
        );
    }

    // Apply sorting
    if (sortOrder === "price-asc") {
        filtered.sort((a, b) => a.price - b.price);
    } else if (sortOrder === "price-desc") {
        filtered.sort((a, b) => b.price - a.price);
    } else if (sortOrder === "duration-asc") {
        filtered.sort((a, b) => a.duration_minutes - b.duration_minutes);
    }

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3.5rem 1rem; color: var(--text-muted);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</div>
                <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.25rem;">No Matching Services Found</h3>
                <p style="font-size: 0.9rem;">Try adjusting your keyword search or category filter.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = filtered.map(s => `
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
}
