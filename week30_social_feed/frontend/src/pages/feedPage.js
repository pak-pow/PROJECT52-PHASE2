/**
 * feedPage.js — Home feed page controller.
 */
import { requireAuthPage } from "../utils/authCheck.js";
import { initSidebar } from "../components/sidebar.js";
import { initComposeModal } from "../components/composeModal.js";
import { loadSuggestions } from "../components/suggestions.js";
import { renderPostCard, skeletons } from "../components/postCard.js";
import { apiFeed, apiCreatePost } from "../api/postApi.js";
import { showToast } from "../utils/helpers.js";
import { avatarUrl } from "../api/userApi.js";

const currentUser = await requireAuthPage();
if (currentUser) {
    initSidebar("feed");

    const composeAvatar     = document.getElementById("compose-avatar");
    const composeInput      = document.getElementById("compose-input");
    const composeSubmit     = document.getElementById("compose-submit-btn");
    const charCounter       = document.getElementById("char-counter");
    const feedList          = document.getElementById("feed-list");
    const feedLoader        = document.getElementById("feed-loader");
    const composeImageInput  = document.getElementById("compose-image-input");
    const composePreview     = document.getElementById("compose-image-preview");
    const composePreviewImg  = document.getElementById("compose-preview-img");
    const composeRemoveImage = document.getElementById("compose-remove-image");

    if (composeAvatar) {
        composeAvatar.textContent = (currentUser.displayName || currentUser.username || "?")[0].toUpperCase();
        const img = new Image();
        img.onload = () => {
            composeAvatar.textContent = "";
            composeAvatar.style.cssText = `background-image:url(${img.src});background-size:cover;background-position:center;`;
        };
        img.src = avatarUrl(currentUser.username);
    }

    if (composeInput && composeSubmit) {
        composeInput.addEventListener("input", () => {
            charCounter.textContent = 280 - composeInput.value.length;
            charCounter.classList.toggle("char-danger", composeInput.value.length > 260);
        });

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

            const newCard = renderPostCard(data, { showDelete: true });
            newCard.classList.add("post-card--new");
            feedList.prepend(newCard);
            feedList.querySelector(".empty-state")?.remove();
        });
    }

    // Feed Loading & Infinite Scroll
    let feedLastId = null;
    let feedDone   = false;

    async function loadFeed(append = false) {
        if (feedDone) return;
        if (!append) feedList.innerHTML = skeletons();
        feedLoader.classList.toggle("hidden", !append);

        const posts = await apiFeed(feedLastId);
        if (!append) feedList.innerHTML = "";

        if (!posts || !posts.length) {
            if (!append) {
                feedList.innerHTML = '<p class="empty-state">No posts yet. Follow some people or write your first post!</p>';
            }
            feedDone = true;
            feedLoader.classList.add("hidden");
            if (obs) obs.unobserve(feedLoader);
            return;
        }

        if (posts.length < 20) {
            feedDone = true;
            feedLoader.classList.add("hidden");
            if (obs) obs.unobserve(feedLoader);
        }
        posts.forEach(p => {
            feedList.appendChild(renderPostCard(p, { showDelete: true }));
            feedLastId = p.id;
        });
    }

    const obs = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) loadFeed(true);
    }, { rootMargin: "200px" });
    obs.observe(feedLoader);

    initComposeModal((newPost) => {
        const newCard = renderPostCard(newPost, { showDelete: true });
        newCard.classList.add("post-card--new");
        feedList.prepend(newCard);
        feedList.querySelector(".empty-state")?.remove();
    });

    loadFeed();
    loadSuggestions();
}
