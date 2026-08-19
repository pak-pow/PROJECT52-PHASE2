import { renderNavbar } from "../components/navbar.js";
import { createJobPosting, deleteJobPosting } from "../api/jobApi.js";
import { updateApplicationStatus } from "../api/applicationApi.js";
import { getStoredUser } from "../utils/authCheck.js";
import { escapeHtml, formatSalary, showToast } from "../utils/helpers.js";

const API_BASE_URL = "http://127.0.0.1:5000/api";

document.addEventListener("DOMContentLoaded", async () => {
    renderNavbar("employer");

    const currentUser = getStoredUser();

    // Employer Role Auth Guard
    if (!currentUser || currentUser.role !== "employer") {
        showToast("Please sign in as an Employer to access this dashboard.", "warning");
        setTimeout(() => {
            window.location.href = "login.html";
        }, 1000);
        return;
    }

    const companySubtitle = document.getElementById("company-subtitle");
    if (companySubtitle) {
        companySubtitle.textContent = `Recruitment portal for ${currentUser.company_name || currentUser.username}.`;
    }

    const postModal = document.getElementById("post-job-modal");
    const openPostModalBtn = document.getElementById("open-post-modal-btn");
    const closePostModalBtn = document.getElementById("post-modal-close-btn");
    const postJobForm = document.getElementById("post-job-form");

    // Modal Toggles
    openPostModalBtn?.addEventListener("click", () => {
        postModal?.classList.add("active");
        const companyInput = document.getElementById("post-company");
        if (companyInput && currentUser.company_name) {
            companyInput.value = currentUser.company_name;
        }
    });

    closePostModalBtn?.addEventListener("click", () => {
        postModal?.classList.remove("active");
    });

    // Handle Create Job Submission
    postJobForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById("submit-post-btn");
        if (submitBtn) submitBtn.disabled = true;

        const newJob = {
            employer_id: currentUser.id,
            title: document.getElementById("post-title").value.trim(),
            company: document.getElementById("post-company").value.trim(),
            location: document.getElementById("post-location").value.trim(),
            job_type: document.getElementById("post-type").value,
            category: document.getElementById("post-category").value,
            salary_min: parseInt(document.getElementById("post-salary-min").value || 0),
            salary_max: parseInt(document.getElementById("post-salary-max").value || 0),
            description: document.getElementById("post-description").value.trim(),
            requirements: document.getElementById("post-requirements").value.trim()
        };

        try {
            await createJobPosting(newJob);
            showToast("Job posting published successfully! ✨", "success");
            postModal?.classList.remove("active");
            postJobForm.reset();
            loadEmployerDashboard();
        } catch (err) {
            showToast(err.message || "Failed to publish job posting.", "error");
        } finally {
            if (submitBtn) submitBtn.disabled = false;
        }
    });

    async function loadEmployerDashboard() {
        const employerJobList = document.getElementById("employer-job-list");
        const metricActiveJobs = document.getElementById("metric-active-jobs");
        const metricTotalApps = document.getElementById("metric-total-apps");
        const metricPendingApps = document.getElementById("metric-pending-apps");

        try {
            // 1. Fetch all jobs created by employer
            const res = await fetch(`${API_BASE_URL}/jobs`);
            const allJobs = await res.json();
            const employerJobs = allJobs.filter(j => j.employer_id === currentUser.id);

            if (metricActiveJobs) metricActiveJobs.textContent = employerJobs.length;

            if (!employerJobs || employerJobs.length === 0) {
                if (employerJobList) {
                    employerJobList.innerHTML = `
                        <div style="text-align: center; padding: 3rem; background-color: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg);">
                            <p style="font-size: 1.1rem; font-weight: 700; color: var(--text-secondary);">No job postings created yet 💼</p>
                            <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1rem;">Click 'Post New Job' to start receiving candidate applications.</p>
                        </div>
                    `;
                }
                if (metricTotalApps) metricTotalApps.textContent = "0";
                if (metricPendingApps) metricPendingApps.textContent = "0";
                return;
            }

            // 2. Fetch applications for each job
            let totalAppsCount = 0;
            let pendingAppsCount = 0;

            const jobsWithApps = await Promise.all(employerJobs.map(async (job) => {
                const appRes = await fetch(`${API_BASE_URL}/jobs/${job.id}/applications`);
                const apps = await appRes.json();
                totalAppsCount += apps.length;
                pendingAppsCount += apps.filter(a => a.status === "Pending").length;
                return { job, apps };
            }));

            if (metricTotalApps) metricTotalApps.textContent = totalAppsCount;
            if (metricPendingApps) metricPendingApps.textContent = pendingAppsCount;

            // 3. Render Job Cards and Received Applications
            if (employerJobList) {
                employerJobList.innerHTML = jobsWithApps.map(({ job, apps }) => {
                    const salaryText = formatSalary(job.salary_min, job.salary_max);

                    const applicantCardsHtml = apps.length > 0 ? apps.map(app => {
                        let statusClass = "status-pending";
                        if (app.status === "Reviewing") statusClass = "status-reviewing";
                        if (app.status === "Interviewing") statusClass = "status-interviewing";
                        if (app.status === "Accepted") statusClass = "status-accepted";
                        if (app.status === "Rejected") statusClass = "status-rejected";

                        return `
                            <div class="applicant-card" data-app-id="${app.id}">
                                <div class="applicant-info">
                                    <h4>${escapeHtml(app.applicant_name)} <span class="status-badge ${statusClass}">${escapeHtml(app.status)}</span></h4>
                                    <p>✉️ ${escapeHtml(app.applicant_email)} &nbsp;•&nbsp; 📅 Applied ${new Date(app.applied_at).toLocaleDateString()}</p>
                                    ${app.cover_letter ? `<div class="cover-letter-box">" ${escapeHtml(app.cover_letter)} "</div>` : ''}
                                </div>

                                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem;">
                                    ${app.resume_path ? `
                                        <a href="http://127.0.0.1:5000${app.resume_path}" target="_blank" class="btn-sm-outline">
                                            📄 Download Resume
                                        </a>
                                    ` : '<span style="font-size: 0.8rem; color: var(--text-muted);">No resume attached</span>'}

                                    <select class="status-select" data-app-id="${app.id}">
                                        <option value="Pending" ${app.status === "Pending" ? "selected" : ""}>⏳ Pending</option>
                                        <option value="Reviewing" ${app.status === "Reviewing" ? "selected" : ""}>🔍 Reviewing</option>
                                        <option value="Interviewing" ${app.status === "Interviewing" ? "selected" : ""}>🎯 Interviewing</option>
                                        <option value="Accepted" ${app.status === "Accepted" ? "selected" : ""}>✅ Accepted</option>
                                        <option value="Rejected" ${app.status === "Rejected" ? "selected" : ""}>❌ Rejected</option>
                                    </select>
                                </div>
                            </div>
                        `;
                    }).join("") : `<p style="font-size: 0.85rem; color: var(--text-muted); font-style: italic;">No candidates have applied for this position yet.</p>`;

                    return `
                        <div class="employer-job-card" data-job-id="${job.id}">
                            <div class="employer-job-header">
                                <div>
                                    <h3 style="font-size: 1.15rem; font-weight: 700;">${escapeHtml(job.title)}</h3>
                                    <span style="font-size: 0.85rem; color: var(--text-secondary);">📍 ${escapeHtml(job.location)} &nbsp;•&nbsp; 💰 ${salaryText}</span>
                                </div>

                                <button class="delete-job-btn btn-sm-outline" data-job-id="${job.id}" style="color: var(--danger); border-color: rgba(239,68,68,0.3);">
                                    🗑️ Delete Listing
                                </button>
                            </div>

                            <div>
                                <h4 style="font-size: 0.9rem; font-weight: 700; margin-bottom: 0.5rem; color: var(--text-muted); text-transform: uppercase;">
                                    Candidate Applications (${apps.length})
                                </h4>
                                <div class="applicant-list">
                                    ${applicantCardsHtml}
                                </div>
                            </div>
                        </div>
                    `;
                }).join("");
            }

            // Attach Status Dropdown Change Handlers
            document.querySelectorAll(".status-select").forEach(select => {
                select.addEventListener("change", async (e) => {
                    const appId = e.target.getAttribute("data-app-id");
                    const newStatus = e.target.value;
                    try {
                        await updateApplicationStatus(appId, newStatus);
                        showToast(`Candidate status updated to '${newStatus}'!`, "success");
                        loadEmployerDashboard();
                    } catch (err) {
                        showToast("Failed to update candidate status.", "error");
                    }
                });
            });

            // Attach Delete Job Handlers
            document.querySelectorAll(".delete-job-btn").forEach(btn => {
                btn.addEventListener("click", async (e) => {
                    const jobId = e.target.getAttribute("data-job-id");
                    if (confirm("Are you sure you want to delete this job listing?")) {
                        try {
                            await deleteJobPosting(jobId);
                            showToast("Job listing deleted.", "info");
                            loadEmployerDashboard();
                        } catch (err) {
                            showToast("Failed to delete job listing.", "error");
                        }
                    }
                });
            });

        } catch (err) {
            showToast("Failed to load employer dashboard data.", "error");
        }
    }

    loadEmployerDashboard();
});
