/**
 * contact.js — Contact form AJAX handler + Projects renderer with filtering & spotlight
 * Handles the public-facing index.html page.
 */

// ── All imports MUST be at the top of an ES module ────────────────────────
import { submitContact, getProjects } from "./api.js";

// ── Contact Form ───────────────────────────────────────────────────────────

const form       = document.getElementById("contact-form");
const submitBtn  = document.getElementById("contact-submit");
const submitText = document.getElementById("submit-text");
const spinner    = document.getElementById("submit-spinner");
const toast      = document.getElementById("contact-toast");

if (form) {
    setupFormValidation(form);

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // NEW: Check form validity before submission
        let isFormValid = true;
        const inputs = form.querySelectorAll("input, textarea");
        inputs.forEach((input) => {
            if (!validateField(input)) {
                isFormValid = false;
            }
        });

        if (!isFormValid) {
            showToast("Please fill in all fields correctly.", "error");
            return;
        }

        const data = {
            name:    form.name.value.trim(),
            email:   form.email.value.trim(),
            subject: form.subject.value.trim(),
            message: form.message.value.trim(),
        };

        submitBtn.disabled = true;
        submitText.textContent = "Sending...";
        spinner.classList.remove("hidden");

        try {
            const result = await submitContact(data);
            showToast(result.message, "success");
            form.reset();
            resetFormValidation(form);
        } catch (err) {
            showToast(err.message || "Something went wrong. Please try again.", "error");
        } finally {
            submitBtn.disabled = false;
            submitText.textContent = "Send Message";
            spinner.classList.add("hidden");
        }
    });
}

// NEW: Live input validation logic
function setupFormValidation(formEl) {
    if (!formEl) return;
    const inputs = formEl.querySelectorAll("input, textarea");
    inputs.forEach((input) => {
        input.addEventListener("blur", () => validateField(input));
        input.addEventListener("input", () => {
            if (input.classList.contains("is-invalid") || input.classList.contains("is-valid")) {
                validateField(input);
            }
        });
    });
}

function validateField(input) {
    let isValid = input.checkValidity();
    if (input.type === "email" && input.value.trim() !== "") {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input.value.trim())) {
            isValid = false;
        }
    }
    if (isValid) {
        input.classList.add("is-valid");
        input.classList.remove("is-invalid");
    } else {
        input.classList.add("is-invalid");
        input.classList.remove("is-valid");
    }
    return isValid;
}

function resetFormValidation(formEl) {
    if (!formEl) return;
    const inputs = formEl.querySelectorAll("input, textarea");
    inputs.forEach((input) => {
        input.classList.remove("is-valid", "is-invalid");
    });
}

function showToast(message, type = "success") {
    toast.textContent = message;
    toast.className = `toast toast-${type}`;
    toast.classList.remove("hidden");

    setTimeout(() => {
        toast.classList.add("toast-fade");
        setTimeout(() => {
            toast.classList.add("hidden");
            toast.classList.remove("toast-fade");
        }, 500);
    }, 4000);
}

// ── Projects Rendering & Filtering ──────────────────────────────────────────

const grid = document.getElementById("projects-grid");
const featuredContainer = document.getElementById("featured-project-container");
const techFilters = document.getElementById("tech-filters");
const statusFilter = document.getElementById("status-filter");

let allProjects = [];
let currentTech = "all";
let currentStatus = "all";

if (grid) {
    loadProjects();
}

async function loadProjects() {
    try {
        allProjects = await getProjects();
        
        // Build tech filters dynamically
        buildTechFilters();
        
        // Setup filter listeners
        setupFilterListeners();
        
        // Initial render
        renderFilteredProjects();
    } catch (err) {
        console.error(err);
        grid.innerHTML = `
            <div class="backend-offline-msg">
                <p>⚠️ Could not connect to backend.</p>
                <p class="backend-hint">Run <code>python run.py</code> in <code>backend/</code> then refresh.</p>
            </div>`;
    }
}

/** Dynamic extraction of top tech tags */
function buildTechFilters() {
    if (!techFilters) return;
    
    // Count tech frequency
    const techCounts = {};
    allProjects.forEach((p) => {
        if (!p.tech_stack) return;
        p.tech_stack.split(",").forEach((t) => {
            const tech = t.trim();
            if (tech) {
                techCounts[tech] = (techCounts[tech] || 0) + 1;
            }
        });
    });

    // Sort by count descending
    const sortedTechs = Object.keys(techCounts).sort((a, b) => techCounts[b] - techCounts[a]);
    
    // Take top 6 technologies
    const topTechs = sortedTechs.slice(0, 6);

    // Render pills
    let html = `<button class="filter-btn active" data-tech="all">All</button>`;
    topTechs.forEach((tech) => {
        html += `<button class="filter-btn" data-tech="${escHtml(tech)}">${escHtml(tech)}</button>`;
    });
    techFilters.innerHTML = html;
}

function setupFilterListeners() {
    if (techFilters) {
        techFilters.addEventListener("click", (e) => {
            const btn = e.target.closest(".filter-btn");
            if (!btn) return;
            
            // Toggle active class
            techFilters.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            
            currentTech = btn.dataset.tech;
            renderFilteredProjects();
        });
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", (e) => {
            currentStatus = e.target.value;
            renderFilteredProjects();
        });
    }
}

function renderFilteredProjects() {
    // 1. Filter the list
    const filtered = allProjects.filter((p) => {
        const matchesStatus = (currentStatus === "all") || (p.status === currentStatus);
        
        let matchesTech = false;
        if (currentTech === "all") {
            matchesTech = true;
        } else if (p.tech_stack) {
            matchesTech = p.tech_stack.split(",").map(t => t.trim()).includes(currentTech);
        }
        
        return matchesStatus && matchesTech;
    });

    // 2. Render Featured Spotlight (only shown when no filter is active, and if a project is featured)
    const featuredProj = allProjects.find((p) => p.featured === 1);
    
    if (featuredProj && currentTech === "all" && currentStatus === "all") {
        featuredContainer.innerHTML = `
            <div class="featured-card card-entrance">
                <span class="featured-badge"><span class="featured-star">★</span> Spotlight</span>
                <div class="featured-left">
                    <p class="hero-label">// Featured Project</p>
                    <h3>${escHtml(featuredProj.title)}</h3>
                    <p>${escHtml(featuredProj.description)}</p>
                </div>
                <div class="featured-right">
                    <div class="featured-status-row">
                        <span class="filter-label">Status:</span>
                        <span class="status-badge status-${slugify(featuredProj.status)}">${escHtml(featuredProj.status)}</span>
                    </div>
                    <div>
                        <span class="filter-label" style="display:block; margin-bottom:0.5rem;">Tech Stack:</span>
                        <div class="featured-tech-list">
                            ${featuredProj.tech_stack.split(",").map(t =>
                                `<span class="tech-tag">${escHtml(t.trim())}</span>`
                            ).join("")}
                        </div>
                    </div>
                    <div class="featured-links">
                        ${featuredProj.github_url ? `<a href="${escHtml(featuredProj.github_url)}" target="_blank" rel="noopener" class="btn btn-outline btn-sm">GitHub ↗</a>` : ""}
                        ${featuredProj.live_url   ? `<a href="${escHtml(featuredProj.live_url)}"   target="_blank" rel="noopener" class="btn btn-primary btn-sm">Live ↗</a>` : ""}
                    </div>
                </div>
            </div>`;
    } else {
        featuredContainer.innerHTML = "";
    }

    // 3. Render General Grid (if not filtering, exclude the spotlight project so it doesn't duplicate)
    let gridProjects = filtered;
    if (featuredProj && currentTech === "all" && currentStatus === "all") {
        gridProjects = filtered.filter((p) => p.id !== featuredProj.id);
    }

    if (!gridProjects.length) {
        grid.innerHTML = `<p class="empty-state">No matching projects found.</p>`;
        return;
    }

    // Render grid with staggered delay styling
    grid.innerHTML = gridProjects.map((p, index) => `
        <div class="project-card glass-card card-entrance" style="animation-delay: ${index * 75}ms">
            <div class="project-card-header">
                <h3>
                    ${p.featured === 1 ? `<span class="admin-featured-star" title="Featured project">★</span>` : ""}
                    ${escHtml(p.title)}
                </h3>
                <span class="status-badge status-${slugify(p.status)}">${escHtml(p.status)}</span>
            </div>
            <p class="project-desc">${escHtml(p.description)}</p>
            <div class="tech-tags">
                ${p.tech_stack.split(",").map(t =>
                    `<span class="tech-tag">${escHtml(t.trim())}</span>`
                ).join("")}
            </div>
            <div class="project-links">
                ${p.github_url ? `<a href="${escHtml(p.github_url)}" target="_blank" rel="noopener" class="btn btn-outline btn-sm">GitHub ↗</a>` : ""}
                ${p.live_url   ? `<a href="${escHtml(p.live_url)}"   target="_blank" rel="noopener" class="btn btn-primary btn-sm">Live ↗</a>` : ""}
            </div>
        </div>
    `).join("");
}

function escHtml(str) {
    return String(str ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function slugify(str) {
    return str.toLowerCase().replace(/\s+/g, "-");
}

// ── Scroll-reveal via IntersectionObserver ─────────────────────────────────
// Immediately reveal elements already visible on page load,
// observe the rest as the user scrolls.

const revealEls = document.querySelectorAll(".section-reveal");

const observer = new IntersectionObserver(
    (entries) => {
        entries.forEach((e) => {
            if (e.isIntersecting) {
                e.target.classList.add("revealed");
                observer.unobserve(e.target);
            }
        });
    },
    { threshold: 0.08 }
);

revealEls.forEach((el) => {
    const rect = el.getBoundingClientRect();
    const alreadyVisible = rect.top < window.innerHeight && rect.bottom > 0;
    if (alreadyVisible) {
        el.classList.add("revealed");
    } else {
        observer.observe(el);
    }
});
