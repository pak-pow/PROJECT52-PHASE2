/**
 * postPage.js — Post detail page controller.
 */
import { requireAuthPage } from "../utils/authCheck.js";
import { initSidebar } from "../components/sidebar.js";
import { initComposeModal } from "../components/composeModal.js";
import { loadSuggestions } from "../components/suggestions.js";
import { renderPostCard, skeletons } from "../components/postCard.js";
import { apiGetPost, apiCreatePost } from "../api/postApi.js";
import { showToast } from "../utils/helpers.js";

const currentUser = requireAuthPage();
if (currentUser) {
    initSidebar("");
    initComposeModal();

    const urlParams = new URLSearchParams(window.location.search);
    const postId = parseInt(urlParams.get("id"), 10);

    const backBtn          = document.getElementById("back-btn");
    const detailContainer = document.getElementById("post-detail-container");
    const repliesContainer = document.getElementById("replies-container");

    if (backBtn) {
        backBtn.addEventListener("click", () => {
            if (document.referrer && document.referrer.includes(window.location.host)) {
                window.history.back();
            } else {
                window.location.href = "feed.html";
            }
        });
    }

    async function loadPostDetail() {
        if (!postId) {
            detailContainer.innerHTML = '<p class="empty-state">Invalid post ID.</p>';
            return;
        }
        detailContainer.innerHTML = skeletons(1);
        repliesContainer.innerHTML = skeletons(2);

        const { ok, data } = await apiGetPost(postId);
        if (!ok) { detailContainer.innerHTML = '<p class="empty-state">Post not found.</p>'; return; }

        const post    = data.post;
        const replies = data.replies || [];

        detailContainer.innerHTML = "";
        const mainCard = renderPostCard(post, { showDelete: true });
        mainCard.classList.add("post-card--detail");
        detailContainer.appendChild(mainCard);

        const replyBox = document.createElement("div");
        replyBox.className = "reply-compose";
        const replyInitials = (currentUser.displayName || currentUser.username || "?")[0].toUpperCase();
        replyBox.innerHTML = `
            <div class="avatar avatar-md">${replyInitials}</div>
            <div class="compose-inline-right">
                <textarea class="compose-textarea" id="reply-input" placeholder="Post your reply…" maxlength="280" rows="2"></textarea>
                <div class="compose-actions">
                    <span class="char-counter" id="reply-counter">280</span>
                    <button class="btn-primary" id="reply-submit-btn">Reply</button>
                </div>
            </div>
        `;
        detailContainer.appendChild(replyBox);

        const replyInput   = replyBox.querySelector("#reply-input");
        const replyCounter = replyBox.querySelector("#reply-counter");
        const replySubmit  = replyBox.querySelector("#reply-submit-btn");

        replyInput.addEventListener("input", () => {
            replyCounter.textContent = 280 - replyInput.value.length;
            replyCounter.classList.toggle("char-danger", replyInput.value.length > 260);
        });

        replySubmit.addEventListener("click", async () => {
            const content = replyInput.value.trim();
            if (!content) return;
            replySubmit.disabled = true; replySubmit.textContent = "Replying…";
            const { ok: rOk, data: rData } = await apiCreatePost(content, null, postId);
            replySubmit.disabled = false; replySubmit.textContent = "Reply";
            if (!rOk) { showToast(rData.error || "Could not reply.", "error"); return; }
            replyInput.value = ""; replyCounter.textContent = "280";
            showToast("Replied!", "success");
            repliesContainer.querySelector(".empty-state")?.remove();
            const newCard = renderPostCard(rData, { showDelete: true });
            repliesContainer.prepend(newCard);
        });

        repliesContainer.innerHTML = "";
        if (!replies.length) {
            repliesContainer.innerHTML = '<p class="empty-state">No replies yet. Be the first!</p>';
        } else {
            replies.forEach(r => repliesContainer.appendChild(renderPostCard(r, { showDelete: true })));
        }
    }

    loadPostDetail();
    loadSuggestions();
}
