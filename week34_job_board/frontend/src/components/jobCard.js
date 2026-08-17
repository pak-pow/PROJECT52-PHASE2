import { escapeHtml, formatSalary } from "../utils/helpers.js";

export function renderJobCard(job, onBookmarkToggle = null) {
    const salaryText = formatSalary(job.salary_min, job.salary_max);
    
    let typeClass = "type-fulltime";
    if (job.job_type === "Remote") typeClass = "type-remote";
    if (job.job_type === "Contract") typeClass = "type-contract";
    if (job.job_type === "Part-time") typeClass = "type-parttime";

    return `
        <div class="job-card" data-id="${job.id}">
            <div class="job-card-header">
                <div class="company-badge-icon">${escapeHtml(job.company.charAt(0).toUpperCase())}</div>
                <div class="job-card-title-group">
                    <h3 class="job-title"><a href="job-detail.html?id=${job.id}">${escapeHtml(job.title)}</a></h3>
                    <span class="job-company">${escapeHtml(job.company)}</span>
                </div>
                <span class="job-type-pill ${typeClass}">${escapeHtml(job.job_type)}</span>
            </div>

            <p class="job-description-snippet">${escapeHtml(job.description)}</p>

            <div class="job-card-footer">
                <div class="job-meta-item">
                    <span>📍 ${escapeHtml(job.location)}</span>
                </div>
                <div class="job-meta-item">
                    <span>💰 ${salaryText}</span>
                </div>
                <div class="job-card-actions">
                    <a href="job-detail.html?id=${job.id}" class="btn-primary-sm">View & Apply →</a>
                </div>
            </div>
        </div>
    `;
}
