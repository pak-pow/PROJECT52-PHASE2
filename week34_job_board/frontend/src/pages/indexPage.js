import { renderNavbar } from "../components/navbar.js";
import { renderJobCard } from "../components/jobCard.js";
import { fetchJobs } from "../api/jobApi.js";
import { showToast } from "../utils/helpers.js";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar("catalog");

    const keywordInput = document.getElementById("search-keyword");
    const searchBtn = document.getElementById("search-btn");

    const locationSelect = document.getElementById("filter-location");
    const typeSelect = document.getElementById("filter-type");
    const categorySelect = document.getElementById("filter-category");
    const salarySelect = document.getElementById("filter-salary");
    const resetBtn = document.getElementById("reset-filters-btn");

    const jobGrid = document.getElementById("job-grid");
    const jobCountBadge = document.getElementById("job-count-badge");

    async function loadJobs() {
        if (jobCountBadge) jobCountBadge.textContent = "Searching job opportunities...";

        const filters = {
            keyword: keywordInput?.value.trim() || "",
            location: locationSelect?.value || "",
            type: typeSelect?.value || "",
            category: categorySelect?.value || "",
            min_salary: salarySelect?.value || "0"
        };

        try {
            const jobs = await fetchJobs(filters);

            if (jobCountBadge) {
                jobCountBadge.textContent = `Showing ${jobs.length} tech ${jobs.length === 1 ? 'job' : 'jobs'}`;
            }

            if (!jobs || jobs.length === 0) {
                jobGrid.innerHTML = `
                    <div style="text-align: center; padding: 3rem; background-color: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg);">
                        <p style="font-size: 1.1rem; font-weight: 700; color: var(--text-secondary);">No matching tech jobs found 🔍</p>
                        <p style="font-size: 0.9rem; color: var(--text-muted);">Try adjusting your search keywords or resetting your filters.</p>
                    </div>
                `;
                return;
            }

            jobGrid.innerHTML = jobs.map(job => renderJobCard(job)).join("");
        } catch (err) {
            showToast("Failed to load jobs from backend server.", "error");
            if (jobCountBadge) jobCountBadge.textContent = "Error loading jobs.";
        }
    }

    // Trigger Search & Filter Listeners
    searchBtn?.addEventListener("click", loadJobs);
    keywordInput?.addEventListener("keypress", (e) => {
        if (e.key === "Enter") loadJobs();
    });

    locationSelect?.addEventListener("change", loadJobs);
    typeSelect?.addEventListener("change", loadJobs);
    categorySelect?.addEventListener("change", loadJobs);
    salarySelect?.addEventListener("change", loadJobs);

    resetBtn?.addEventListener("click", () => {
        if (keywordInput) keywordInput.value = "";
        if (locationSelect) locationSelect.value = "";
        if (typeSelect) typeSelect.value = "";
        if (categorySelect) categorySelect.value = "";
        if (salarySelect) salarySelect.value = "0";
        loadJobs();
        showToast("Search filters reset", "info");
    });

    // Initial Load
    loadJobs();
});
