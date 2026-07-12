/* ═══════════════════════════════════════════════════════════════
   Dropzone Component
   ═══════════════════════════════════════════════════════════════ */

import { uploadFiles } from "../api/fileApi.js";
import { formatBytes, getCategoryIcon } from "../utils/helpers.js";

/**
 * Render the drag-and-drop upload zone into a container element.
 * @param {HTMLElement} container
 * @param {function} onUploadComplete - callback after successful upload
 */
export function renderDropzone(container, onUploadComplete) {
    container.innerHTML = `
        <div class="upload-container">
            <div class="dropzone" id="dropzone">
                <span class="dropzone-icon">☁️</span>
                <p class="dropzone-title">Drop files here</p>
                <p class="dropzone-subtitle">or click to browse · max 10 MB per file</p>
                <input type="file" class="dropzone-input" id="file-input" multiple />
            </div>
            <div class="upload-queue" id="upload-queue"></div>
        </div>
    `;

    const zone = container.querySelector("#dropzone");
    const input = container.querySelector("#file-input");
    const queue = container.querySelector("#upload-queue");

    // Click to open file picker
    zone.addEventListener("click", () => input.click());

    // Drag events
    zone.addEventListener("dragover", (e) => {
        e.preventDefault();
        zone.classList.add("dragover");
    });
    zone.addEventListener("dragleave", () => zone.classList.remove("dragover"));
    zone.addEventListener("drop", (e) => {
        e.preventDefault();
        zone.classList.remove("dragover");
        if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files, queue, onUploadComplete);
    });

    // File picker
    input.addEventListener("change", () => {
        if (input.files.length) handleFiles(input.files, queue, onUploadComplete);
        input.value = "";
    });
}


async function handleFiles(files, queueEl, onComplete) {
    // Show items in queue
    const items = [];
    for (const file of files) {
        const icon = getCategoryIcon(guessCategory(file.type));
        const itemEl = document.createElement("div");
        itemEl.className = "upload-item";
        itemEl.innerHTML = `
            <span class="upload-item-icon">${icon}</span>
            <div class="upload-item-info">
                <div class="upload-item-name">${escapeHtml(file.name)}</div>
                <div class="upload-item-size">${formatBytes(file.size)}</div>
                <div class="progress-bar-track"><div class="progress-bar-fill"></div></div>
            </div>
            <span class="upload-item-status pending">Uploading…</span>
        `;
        queueEl.appendChild(itemEl);
        items.push(itemEl);
    }

    try {
        const result = await uploadFiles(files, (pct) => {
            items.forEach((el) => {
                el.querySelector(".progress-bar-fill").style.width = `${pct}%`;
            });
        });

        if (result.ok) {
            items.forEach((el) => {
                el.querySelector(".progress-bar-fill").style.width = "100%";
                const status = el.querySelector(".upload-item-status");
                status.textContent = "Done ✓";
                status.className = "upload-item-status success";
            });
            if (onComplete) setTimeout(onComplete, 600);
        } else {
            items.forEach((el) => {
                const status = el.querySelector(".upload-item-status");
                status.textContent = "Failed";
                status.className = "upload-item-status error";
            });
        }
    } catch (err) {
        items.forEach((el) => {
            const status = el.querySelector(".upload-item-status");
            status.textContent = "Error";
            status.className = "upload-item-status error";
        });
    }
}


function guessCategory(mime) {
    if (mime.startsWith("image/")) return "image";
    if (mime.startsWith("audio/")) return "audio";
    if (mime.startsWith("video/")) return "video";
    if (mime.includes("pdf") || mime.includes("word") || mime.startsWith("text/")) return "document";
    return "other";
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
