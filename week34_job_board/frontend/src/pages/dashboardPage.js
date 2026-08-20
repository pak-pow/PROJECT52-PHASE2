import { renderNavbar } from "../components/navbar.js";
import { renderJobCard } from "../components/jobCard.js";
import { fetchApplicantApplications, fetchSavedJobs, toggleSavedJob } from "../api/applicationApi.js";
import { getStoredUser } from "../utils/authCheck.js";
import { escapeHtml, showToast } from "../utils/helpers.js";

document.addEventListener("DOMContentLoaded", async () => {
    renderNavbar("dashboard");

    const currentUser = getStoredUser();

    // Applicant Role Auth Guard
    if (!currentUser) {
        showToast("Please sign in to access your applicant dashboard.", "warning");
        setTimeout(() => {
            window.location.href = "login.html";
        }, 1000);
        return;
    }

    const welcomeHeading = document.getElementById("welcome-heading");
    if (welcomeHeading) {
        welcomeHeading.textContent = `Welcome, ${currentUser.username}!`;
    }

    async function loadDashboard() {
        const appListContainer = document.getElementById("applicant-app-list");
        const savedJobsContainer = document.getElementById("saved-jobs-grid");

        const metricAppsSubmitted = document.getElementById("metric-apps-submitted");
        const metricInterviews = document.getElementById("metric-interviews");
        const metricSavedJobs = document.getElementById("metric-saved-jobs");

        try {
            // 1. Fetch submitted applications
            const apps = await fetchApplicantApplications(currentUser.id);
            if (metricAppsSubmitted) metricAppsSubmitted.textContent = apps.length;

            const activeReviews = apps.filter(a => ["Reviewing", "Interviewing", "Accepted"].includes(a.status));
            if (metricInterviews) metricInterviews.textContent = activeReviews.length;

            if (!apps || apps.length === 0) {
                if (appListContainer) {
                    appListContainer.innerHTML = `
                        <div style="text-align: center; padding: 2.5rem; background-color: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg);">
                            <p style="font-size: 1.05rem; font-weight: 700; color: var(--text-secondary);">No job applications submitted yet 📑</p>
                            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">Browse active tech jobs and submit your resume to start tracking your progress.</p>
                            <a href="index.html" class="btn-primary-sm">Browse Tech Jobs →</a>
                        </div>
                    `;
                }
            } else {
                if (appListContainer) {
                    appListContainer.innerHTML = apps.map(app => {
                        let statusClass = "status-pending";
                        if (app.status === "Reviewing") statusClass = "status-reviewing";
                        if (app.status === "Interviewing") statusClass = "status-interviewing";
                        if (app.status === "Accepted") statusClass = "status-accepted";
                        if (app.status === "Rejected") statusClass = "status-rejected";

                        return `
                            <div class="employer-job-card" style="margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <h3 style="font-size: 1.1rem; font-weight: 700;">
                                            <a href="job-detail.html?id=${app.job_id}">${escapeHtml(app.job_title)}</a>
                                        </h3>
                                        <p style="font-size: 0.85rem; color: var(--text-secondary);">
                                            🏢 ${escapeHtml(app.job_company)} &nbsp;•&nbsp; 📍 ${escapeHtml(app.job_location || 'Remote')}
                                        </p>
                                    </div>
                                    <span class="status-badge ${statusClass}">${escapeHtml(app.status)}</span>
                                </div>

                                <div style="font-size: 0.82rem; color: var(--text-muted); border-top: 1px solid var(--border); padding-top: 0.65rem; display: flex; justify-content: space-between;">
                                    <span>📅 Applied on ${new Date(app.applied_at).toLocaleDateString()}</span>
                                    ${app.resume_path ? `
                                        <a href="http://127.0.0.1:5000${app.resume_path}" target="_blank" style="color: var(--accent-light); font-weight: 600;">
                                            📄 View Submitted Resume
                                        </a>
                                    ` : ''}
                                </div>
                            </div>
                        `;
                    }).join("");
                }
            }

            // 2. Fetch saved job bookmarks
            const savedJobs = await fetchSavedJobs(currentUser.id);
            if (metricSavedJobs) metricSavedJobs.textContent = savedJobs.length;

            if (!savedJobs || savedJobs.length === 0) {
                if (savedJobsContainer) {
                    savedJobsContainer.innerHTML = `
                        <div style="text-align: center; padding: 2rem; background-color: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); width: 100%;">
                            <p style="font-size: 0.95rem; color: var(--text-muted);">No bookmarked jobs saved. Click 🔖 Bookmark on any job listing to save it here!</p>
                        </div>
                    `;
                }
            } else {
                if (savedJobsContainer) {
                    savedJobsContainer.innerHTML = savedJobs.map(job => renderJobCard(job)).join("");
                }
            }

        } catch (err) {
            showToast("Failed to load applicant dashboard.", "error");
        }
    }

    loadDashboard();
});
