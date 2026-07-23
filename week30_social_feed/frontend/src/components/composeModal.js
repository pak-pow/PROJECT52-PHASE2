/**
 * composeModal.js — Shared mobile compose modal for multi-page application.
 */
import { apiCreatePost } from "../api/postApi.js";
import { avatarUrl } from "../api/userApi.js";
import { showToast } from "../utils/helpers.js";
import { getCurrentUser } from "../utils/state.js";
import { renderPostCard } from "./postCard.js";

export function initComposeModal(onPostCreated) {
    const composeModal       = document.getElementById("compose-modal");
    const modalCloseBtn      = document.getElementById("modal-close-btn");
    const modalPostBtn       = document.getElementById("modal-post-btn");
    const modalInput         = document.getElementById("modal-compose-input");
    const modalCharCounter   = document.getElementById("modal-char-counter");
    const modalImageInput    = document.getElementById("modal-image-input");
    const modalImagePreview  = document.getElementById("modal-image-preview");
    const modalPreviewImg    = document.getElementById("modal-preview-img");
    const modalRemoveImage   = document.getElementById("modal-remove-image");
    const fabBtn             = document.getElementById("fab-compose-btn");

    if (!composeModal) return;

    function openComposeModal() {
        const modalAvatar = document.getElementById("modal-avatar");
        const currentUser = getCurrentUser();
        if (currentUser && modalAvatar) {
            modalAvatar.textContent = (currentUser.displayName || currentUser.username || "?")[0].toUpperCase();
            const mAvImg = new Image();
            mAvImg.onload = () => {
                modalAvatar.textContent = "";
                modalAvatar.style.cssText = `background-image:url(${mAvImg.src});background-size:cover;background-position:center;`;
            };
            mAvImg.src = avatarUrl(currentUser.username);
        }
        if (modalInput) modalInput.value = "";
        if (modalCharCounter) modalCharCounter.textContent = "280";
        if (modalImageInput) modalImageInput.value = "";
        if (modalImagePreview) modalImagePreview.classList.add("hidden");
        if (modalPreviewImg) modalPreviewImg.src = "";
        composeModal.classList.remove("hidden");
        if (modalInput) modalInput.focus();
    }

    function closeComposeModal() {
        composeModal.classList.add("hidden");
    }

    if (fabBtn) fabBtn.addEventListener("click", openComposeModal);
    if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeComposeModal);
    composeModal.addEventListener("click", (e) => {
        if (e.target === composeModal) closeComposeModal();
    });

    if (modalInput && modalCharCounter) {
        modalInput.addEventListener("input", () => {
            modalCharCounter.textContent = 280 - modalInput.value.length;
            modalCharCounter.classList.toggle("char-danger", modalInput.value.length > 260);
        });
    }

    if (modalImageInput) {
        modalImageInput.addEventListener("change", () => {
            const file = modalImageInput.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                modalPreviewImg.src = e.target.result;
                modalImagePreview.classList.remove("hidden");
            };
            reader.readAsDataURL(file);
        });
    }

    if (modalRemoveImage) {
        modalRemoveImage.addEventListener("click", () => {
            modalImageInput.value = "";
            modalPreviewImg.src = "";
            modalImagePreview.classList.add("hidden");
        });
    }

    if (modalPostBtn) {
        modalPostBtn.addEventListener("click", async () => {
            const content   = modalInput.value.trim();
            const imageFile = modalImageInput.files[0] || null;
            if (!content && !imageFile) return;
            modalPostBtn.disabled = true; modalPostBtn.textContent = "Posting…";
            const { ok, data } = await apiCreatePost(content, imageFile);
            modalPostBtn.disabled = false; modalPostBtn.textContent = "Post";
            if (!ok) { showToast(data.error || "Could not post.", "error"); return; }
            closeComposeModal();
            showToast("Posted! 🎉", "success");
            
            if (onPostCreated) {
                onPostCreated(data);
            } else {
                window.location.href = "feed.html";
            }
        });
    }
}
