/* ═══════════════════════════════════════════════════════════════
   Dashboard Page — File Gallery
   ═══════════════════════════════════════════════════════════════ */

import { listFiles, deleteFile, thumbnailUrl } from "../api/fileApi.js";
import { formatBytes, formatDate, getCategoryIcon } from "../utils/helpers.js";
import { openPreview } from "../components/preview.js";

/**
 * Render the file gallery into a container element.
 * @param {HTMLElement} container
 * @param {string} category - category filter (or "all")
 */
export async function renderDashboard(container, category = "all", layout = "grid") {
    container.innerHTML = `<p style="color:var(--text-muted)">Loading files…</p>`;

    try {
        const files = await listFiles(category);

        if (!files.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="empty-state-icon">📂</span>
                    <p>No files yet. Upload some files to get started!</p>
                </div>
            `;
            return;
        }

        const grid = document.createElement("div");
        grid.className = `file-${layout}`;

        for (const file of files) {
            const card = createFileCard(file);
            grid.appendChild(card);
        }

        container.innerHTML = "";
        container.appendChild(grid);
    } catch (err) {
        container.innerHTML = `<p class="error-msg">Failed to load files.</p>`;
    }
}


function createFileCard(file) {
    const card = document.createElement("div");
    card.className = "file-card";
    const token = localStorage.getItem("fv_token");

    const previewHtml = file.has_thumbnail
        ? `<img src="${thumbnailUrl(file.id)}" alt="${escapeHtml(file.original_name)}" loading="lazy" />`
        : `<span class="file-card-icon">${getCategoryIcon(file.category)}</span>`;

    card.innerHTML = `
        <div class="file-card-preview">${previewHtml}</div>
        <div class="file-card-body">
            <div class="file-card-name" title="${escapeHtml(file.original_name)}">${escapeHtml(file.original_name)}</div>
            <div class="file-card-meta">
                <span class="file-card-category ${file.category}">${file.category}</span>
                <span>${formatBytes(file.file_size)}</span>
            </div>
        </div>
        <div class="file-card-actions">
            <button class="preview-btn" title="Preview">👁 Preview</button>
            <button class="delete-btn" title="Delete">🗑 Delete</button>
        </div>
    `;

    // Load thumbnail with auth header
    if (file.has_thumbnail) {
        const img = card.querySelector(".file-card-preview img");
        fetch(thumbnailUrl(file.id), {
            headers: { Authorization: `Bearer ${token}` },
        })
        .then(r => r.blob())
        .then(blob => { img.src = URL.createObjectURL(blob); })
        .catch(() => {
            img.outerHTML = `<span class="file-card-icon">${getCategoryIcon(file.category)}</span>`;
        });
    }

    // Preview
    card.querySelector(".preview-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        openPreview(file);
    });

    // Delete
    card.querySelector(".delete-btn").addEventListener("click", async (e) => {
        e.stopPropagation();
        if (!confirm(`Delete "${file.original_name}"?`)) return;
        const result = await deleteFile(file.id);
        if (result.ok) {
            card.style.transition = "all 0.3s ease";
            card.style.opacity = "0";
            card.style.transform = "scale(0.9)";
            setTimeout(() => card.remove(), 300);
        }
    });

    return card;
}


function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
