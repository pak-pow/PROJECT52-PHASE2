/**
 * contact.js — Contact form AJAX handler
 * Intercepts the contact form submit, calls the API, shows toast feedback.
 */

import { submitContact } from "./api.js";

const form    = document.getElementById("contact-form");
const submitBtn   = document.getElementById("contact-submit");
const submitText  = document.getElementById("submit-text");
const spinner     = document.getElementById("submit-spinner");
const toast       = document.getElementById("contact-toast");

if (form) {
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            name:    form.name.value.trim(),
            email:   form.email.value.trim(),
            subject: form.subject.value.trim(),
            message: form.message.value.trim(),
        };

        // Show loading state
        submitBtn.disabled = true;
        submitText.textContent = "Sending...";
        spinner.classList.remove("hidden");

        try {
            const result = await submitContact(data);
            showToast(result.message, "success");
            form.reset();
        } catch (err) {
            showToast(err.message || "Something went wrong. Please try again.", "error");
        } finally {
            submitBtn.disabled = false;
            submitText.textContent = "Send Message";
            spinner.classList.add("hidden");
        }
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

// ── Projects grid on index.html ────────────────────────────────────────────
import { getProjects } from "./api.js";

const grid = document.getElementById("projects-grid");

if (grid) {
    loadProjects();
}

async function loadProjects() {
    try {
        const projects = await getProjects();
        renderProjects(projects);
    } catch {
        grid.innerHTML = `<p class="error-state">Could not load projects. Is the backend running?</p>`;
    }
}

function renderProjects(projects) {
    if (!projects.length) {
        grid.innerHTML = `<p class="empty-state">No projects yet.</p>`;
        return;
    }

    grid.innerHTML = projects.map((p) => `
        <div class="project-card glass-card section-reveal">
            <div class="project-card-header">
                <h3>${escHtml(p.title)}</h3>
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
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function slugify(str) {
    return str.toLowerCase().replace(/\s+/g, "-");
}

// ── Scroll-reveal via IntersectionObserver ─────────────────────────────────
const revealEls = document.querySelectorAll(".section-reveal");
const observer  = new IntersectionObserver(
    (entries) => entries.forEach((e) => {
        if (e.isIntersecting) {
            e.target.classList.add("revealed");
            observer.unobserve(e.target);
        }
    }),
    { threshold: 0.1 }
);
revealEls.forEach((el) => observer.observe(el));
