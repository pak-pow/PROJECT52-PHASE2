/* ═══════════════════════════════════════════════════════════════
   Dropzone Component
   ═══════════════════════════════════════════════════════════════ */

import { uploadFiles } from "../api/fileApi.js";
import { formatBytes, getFileIcon } from "../utils/helpers.js";

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


const ALLOWED_MIME_TYPES = new Set([
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain", "text/csv", "text/markdown",
    "audio/mpeg", "audio/wav", "audio/ogg",
    "video/mp4", "video/webm",
    "application/zip", "application/x-tar", "application/gzip"
]);
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

async function handleFiles(files, queueEl, onComplete) {
    const validFiles = [];
    const uploadItemElements = [];

    for (const file of files) {
        let err = null;
        if (file.size > MAX_FILE_SIZE) {
            err = "Exceeds 10 MB limit";
        } else if (file.type && !ALLOWED_MIME_TYPES.has(file.type)) {
            err = "Unsupported file type";
        }

        const icon = getFileIcon(file.name, guessCategory(file.type));
        const itemEl = document.createElement("div");
        itemEl.className = "upload-item";

        if (err) {
            itemEl.innerHTML = `
                <span class="upload-item-icon">⚠️</span>
                <div class="upload-item-info">
                    <div class="upload-item-name" style="color:var(--error)">${escapeHtml(file.name)}</div>
                    <div class="upload-item-size">${formatBytes(file.size)} · <span style="color:var(--error)">${err}</span></div>
                </div>
                <span class="upload-item-status error">Blocked</span>
            `;
            queueEl.appendChild(itemEl);
        } else {
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
            validFiles.push(file);
            uploadItemElements.push(itemEl);
        }
    }

    if (!validFiles.length) return;

    try {
        const result = await uploadFiles(validFiles, (pct) => {
            uploadItemElements.forEach((el) => {
                const fill = el.querySelector(".progress-bar-fill");
                if (fill) fill.style.width = `${pct}%`;
            });
        });

        if (result.ok) {
            uploadItemElements.forEach((el) => {
                const fill = el.querySelector(".progress-bar-fill");
                if (fill) fill.style.width = "100%";
                const status = el.querySelector(".upload-item-status");
                if (status) {
                    status.textContent = "Done ✓";
                    status.className = "upload-item-status success";
                }
            });
            if (onComplete) setTimeout(onComplete, 800);
        } else {
            uploadItemElements.forEach((el) => {
                const status = el.querySelector(".upload-item-status");
                if (status) {
                    status.textContent = "Failed";
                    status.className = "upload-item-status error";
                }
            });
        }
    } catch (err) {
        uploadItemElements.forEach((el) => {
            const status = el.querySelector(".upload-item-status");
            if (status) {
                status.textContent = "Error";
                status.className = "upload-item-status error";
            }
        });
    }
}


function guessCategory(mime) {
    if (!mime) return "other";
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
