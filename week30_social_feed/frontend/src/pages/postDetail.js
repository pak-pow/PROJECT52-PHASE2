/**
 * postDetail.js — Post detail view and threaded reply compose logic.
 */
import { apiGetPost, apiCreatePost } from "../api/postApi.js";
import { renderPostCard, skeletons } from "../components/postCard.js";
import { showToast } from "../utils/helpers.js";
import { getCurrentUser } from "../utils/state.js";
import { showPage } from "../router.js";

export async function loadPostDetail(postId) {
    showPage("post-detail");
    const detailContainer = document.getElementById("post-detail-container");
    const repliesContainer = document.getElementById("replies-container");
    if (!detailContainer || !repliesContainer) return;

    detailContainer.innerHTML = skeletons(1);
    repliesContainer.innerHTML = skeletons(2);

    const { ok, data } = await apiGetPost(postId);
    if (!ok) { detailContainer.innerHTML = '<p class="empty-state">Post not found.</p>'; return; }

    const post     = data.post;
    const replies  = data.replies || [];
    const currentUser = getCurrentUser();

    detailContainer.innerHTML = "";
    const mainCard = renderPostCard(post, { showDelete: true });
    mainCard.classList.add("post-card--detail");
    detailContainer.appendChild(mainCard);

    // Reply compose box
    const replyBox = document.createElement("div");
    replyBox.className = "reply-compose";
    const replyInitials = (currentUser?.displayName || currentUser?.username || "?")[0].toUpperCase();
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

    // Render replies
    repliesContainer.innerHTML = "";
    if (!replies.length) {
        repliesContainer.innerHTML = '<p class="empty-state">No replies yet. Be the first!</p>';
    } else {
        replies.forEach(r => repliesContainer.appendChild(renderPostCard(r, { showDelete: true })));
    }
}
