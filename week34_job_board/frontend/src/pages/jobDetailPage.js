import { renderNavbar } from "../components/navbar.js";
import { fetchJobById } from "../api/jobApi.js";
import { submitApplication, toggleSavedJob } from "../api/applicationApi.js";
import { getStoredUser } from "../utils/authCheck.js";
import { escapeHtml, formatSalary, showToast } from "../utils/helpers.js";

document.addEventListener("DOMContentLoaded", async () => {
    renderNavbar("catalog");

    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get("id");

    const jobDetailCard = document.getElementById("job-detail-card");
    const modal = document.getElementById("application-modal");
    const modalCloseBtn = document.getElementById("modal-close-btn");
    const appForm = document.getElementById("application-form");

    if (!jobId) {
        if (jobDetailCard) {
            jobDetailCard.innerHTML = `<p style="text-align: center; color: var(--danger);">No job ID specified in URL.</p>`;
        }
        return;
    }

    const currentUser = getStoredUser();

    try {
        const job = await fetchJobById(jobId);
        const salaryText = formatSalary(job.salary_min, job.salary_max);

        jobDetailCard.innerHTML = `
            <div class="detail-header">
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <div class="detail-company-icon">${escapeHtml(job.company.charAt(0).toUpperCase())}</div>
                    <div class="detail-title-group">
                        <h1>${escapeHtml(job.title)}</h1>
                        <span class="detail-company-name">${escapeHtml(job.company)}</span>
                    </div>
                </div>
            </div>

            <div class="detail-badges-row">
                <span class="detail-badge">📍 ${escapeHtml(job.location)}</span>
                <span class="detail-badge">💰 ${salaryText}</span>
                <span class="detail-badge">🏷️ ${escapeHtml(job.category)}</span>
                <span class="detail-badge">⏱️ ${escapeHtml(job.job_type)}</span>
            </div>

            <div>
                <h3 class="detail-section-title">Job Description</h3>
                <p class="detail-description">${escapeHtml(job.description)}</p>
            </div>

            ${job.requirements ? `
                <div>
                    <h3 class="detail-section-title">Requirements & Skills</h3>
                    <p class="detail-description">${escapeHtml(job.requirements)}</p>
                </div>
            ` : ''}

            <div class="detail-actions-bar">
                <button id="open-app-modal-btn" class="btn-primary" style="padding: 0.75rem 1.5rem; font-size: 1rem;">
                    🚀 Apply for Position
                </button>
                <button id="bookmark-job-btn" class="btn-sm-outline" style="padding: 0.75rem 1.2rem;">
                    🔖 Bookmark Job
                </button>
            </div>
        `;

        // Pre-fill modal user info if logged in
        const nameInput = document.getElementById("applicant-name");
        const emailInput = document.getElementById("applicant-email");
        if (currentUser) {
            if (nameInput) nameInput.value = currentUser.username || "";
            if (emailInput) emailInput.value = currentUser.email || "";
        }

        // Handle Modal Toggle
        document.getElementById("open-app-modal-btn")?.addEventListener("click", () => {
            modal.classList.add("active");
            document.getElementById("modal-job-title").textContent = `Apply for ${job.title}`;
            document.getElementById("modal-job-id").value = job.id;
        });

        modalCloseBtn?.addEventListener("click", () => {
            modal.classList.remove("active");
        });

        // Handle Bookmark Toggle
        document.getElementById("bookmark-job-btn")?.addEventListener("click", async () => {
            if (!currentUser) {
                showToast("Please sign in to bookmark jobs.", "warning");
                return;
            }
            try {
                const res = await toggleSavedJob(currentUser.id, job.id);
                showToast(res.saved ? "Job saved to bookmarks! 🔖" : "Job removed from bookmarks", "info");
            } catch (err) {
                showToast("Failed to save job.", "error");
            }
        });

    } catch (err) {
        jobDetailCard.innerHTML = `<p style="text-align: center; color: var(--danger);">Failed to load job details.</p>`;
    }

    // Handle Application Form Submit (Multipart Resume Upload)
    appForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById("submit-app-btn");
        if (submitBtn) submitBtn.disabled = true;

        const formData = new FormData();
        formData.append("job_id", jobId);
        formData.append("applicant_name", document.getElementById("applicant-name").value.trim());
        formData.append("applicant_email", document.getElementById("applicant-email").value.trim());
        if (currentUser) formData.append("applicant_id", currentUser.id);

        const resumeFile = document.getElementById("applicant-resume").files[0];
        if (resumeFile) formData.append("resume", resumeFile);
        formData.append("cover_letter", document.getElementById("applicant-cover-letter").value.trim());

        try {
            showToast("Uploading resume & submitting application...", "info");
            await submitApplication(formData);
            showToast("Application submitted successfully! 🎉", "success");
            modal.classList.remove("active");
            appForm.reset();
        } catch (err) {
            showToast(err.message || "Failed to submit application.", "error");
        } finally {
            if (submitBtn) submitBtn.disabled = false;
        }
    });
});
