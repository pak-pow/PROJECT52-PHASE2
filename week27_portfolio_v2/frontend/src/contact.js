/**
 * contact.js — Contact form AJAX handler + Projects renderer
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
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

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

// ── Projects Grid ──────────────────────────────────────────────────────────

const grid = document.getElementById("projects-grid");

if (grid) {
    loadProjects();
}

async function loadProjects() {
    try {
        const projects = await getProjects();
        renderProjects(projects);
    } catch {
        grid.innerHTML = `
            <div class="backend-offline-msg">
                <p>⚠️ Could not connect to backend.</p>
                <p class="backend-hint">Run <code>python run.py</code> in <code>backend/</code> then refresh.</p>
            </div>`;
    }
}

function renderProjects(projects) {
    if (!projects.length) {
        grid.innerHTML = `<p class="empty-state">No projects yet — add some from the admin panel.</p>`;
        return;
    }

    grid.innerHTML = projects.map((p) => `
        <div class="project-card glass-card">
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
