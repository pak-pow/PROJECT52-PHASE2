/**
 * compose.js — Inline compose bar and mobile compose modal logic.
 */
import { apiCreatePost } from "../api/postApi.js";
import { avatarUrl } from "../api/userApi.js";
import { showToast } from "../utils/helpers.js";
import { getCurrentUser } from "../utils/state.js";
import { renderPostCard } from "./postCard.js";
import { showPage } from "../router.js";

export function initCompose() {
    const composeInput      = document.getElementById("compose-input");
    const composeSubmit     = document.getElementById("compose-submit-btn");
    const charCounter       = document.getElementById("char-counter");
    const feedList          = document.getElementById("feed-list");

    const composeImageInput  = document.getElementById("compose-image-input");
    const composePreview     = document.getElementById("compose-image-preview");
    const composePreviewImg  = document.getElementById("compose-preview-img");
    const composeRemoveImage = document.getElementById("compose-remove-image");

    if (composeInput && composeSubmit) {
        // Char counter
        composeInput.addEventListener("input", () => {
            charCounter.textContent = 280 - composeInput.value.length;
            charCounter.classList.toggle("char-danger", composeInput.value.length > 260);
        });

        // Image preview
        composeImageInput.addEventListener("change", () => {
            const file = composeImageInput.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                composePreviewImg.src = e.target.result;
                composePreview.classList.remove("hidden");
            };
            reader.readAsDataURL(file);
        });

        composeRemoveImage.addEventListener("click", () => {
            composeImageInput.value = "";
            composePreviewImg.src = "";
            composePreview.classList.add("hidden");
        });

        // Post submit
        composeSubmit.addEventListener("click", async () => {
            const content   = composeInput.value.trim();
            const imageFile = composeImageInput.files[0] || null;
            if (!content && !imageFile) return;
            composeSubmit.disabled = true; composeSubmit.textContent = "Posting…";
            const { ok, data } = await apiCreatePost(content, imageFile);
            composeSubmit.disabled = false; composeSubmit.textContent = "Post";
            if (!ok) { showToast(data.error || "Could not post.", "error"); return; }
            composeInput.value = "";
            charCounter.textContent = "280";
            composeImageInput.value = "";
            composePreview.classList.add("hidden");
            showToast("Posted! 🎉", "success");
            // Prepend new post to top of feed
            const newCard = renderPostCard(data, { showDelete: true });
            newCard.classList.add("post-card--new");
            feedList.prepend(newCard);
            feedList.querySelector(".empty-state")?.remove();
        });
    }

    // ── Mobile Compose Modal ───────────────────────────────────
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

    function openComposeModal() {
        const modalAvatar = document.getElementById("modal-avatar");
        const currentUser = getCurrentUser();
        if (currentUser) {
            modalAvatar.textContent = (currentUser.displayName || currentUser.username || "?")[0].toUpperCase();
            const mAvImg = new Image();
            mAvImg.onload = () => {
                modalAvatar.textContent = "";
                modalAvatar.style.cssText = `background-image:url(${mAvImg.src});background-size:cover;background-position:center;`;
            };
            mAvImg.src = avatarUrl(currentUser.username);
        }
        modalInput.value = "";
        modalCharCounter.textContent = "280";
        modalImageInput.value = "";
        modalImagePreview.classList.add("hidden");
        modalPreviewImg.src = "";
        composeModal.classList.remove("hidden");
        modalInput.focus();
    }

    function closeComposeModal() {
        composeModal.classList.add("hidden");
    }

    if (fabBtn) fabBtn.addEventListener("click", openComposeModal);
    if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeComposeModal);
    if (composeModal) {
        composeModal.addEventListener("click", (e) => {
            if (e.target === composeModal) closeComposeModal();
        });
    }

    if (modalInput) {
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
            showPage("feed");
            const newCard = renderPostCard(data, { showDelete: true });
            newCard.classList.add("post-card--new");
            feedList.prepend(newCard);
            feedList.querySelector(".empty-state")?.remove();
        });
    }
}
