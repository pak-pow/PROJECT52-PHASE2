/* ═══════════════════════════════════════════════════════════════
   Upload Page
   ═══════════════════════════════════════════════════════════════ */

import { renderDropzone } from "../components/dropzone.js";

/**
 * Render the upload page into a container element.
 * @param {HTMLElement} container
 * @param {function} onUploadComplete - callback to switch to dashboard
 */
export function renderUpload(container, onUploadComplete) {
    renderDropzone(container, onUploadComplete);
}
