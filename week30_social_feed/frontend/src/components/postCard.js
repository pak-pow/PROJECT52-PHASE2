/**
 * postCard.js — Post card component rendering and interaction logic.
 */
import { apiLikePost, apiDeletePost, apiRepostPost, postImageUrl } from "../api/postApi.js";
import { avatarUrl } from "../api/userApi.js";
import { showToast, relativeTime, escapeHtml, linkifyContent, formatCount } from "../utils/helpers.js";
import { getCurrentUser } from "../utils/state.js";
import { openLightbox } from "./lightbox.js";
import { isBookmarked, toggleBookmark } from "../utils/bookmarks.js";

/**
 * Avatar element generator helper.
 */
export function makeAvatarEl(username, displayName, sizeClass = "avatar-md") {
    const div = document.createElement("div");
    div.className = `avatar ${sizeClass}`;
    const initial = (displayName || username || "?")[0].toUpperCase();
    const src = avatarUrl(username);
    div.innerHTML = `
        <span class="avatar-initial">${escapeHtml(initial)}</span>
        <img class="avatar-img" src="${src}" alt="" loading="eager" onerror="this.remove()" />
    `;
    return div;
}

/**
 * Skeleton loading markup generator.
 */
export function skeletons(n = 5) {
    return '<div class="skeleton-list">' + Array(n).fill('<div class="skeleton-card"></div>').join("") + '</div>';
}

/**
 * Profile skeleton loading markup generator matching exact profile header dimensions.
 */
export function profileSkeleton() {
    return `
        <div class="skeleton-profile-header">
            <div class="skeleton-banner"></div>
            <div class="skeleton-avatar-wrap">
                <div class="skeleton-avatar"></div>
                <div class="skeleton-btn"></div>
            </div>
            <div class="skeleton-info">
                <div class="skeleton-line skeleton-name"></div>
                <div class="skeleton-line skeleton-handle"></div>
                <div class="skeleton-line skeleton-bio"></div>
                <div class="skeleton-stats">
                    <div class="skeleton-line skeleton-stat"></div>
                    <div class="skeleton-line skeleton-stat"></div>
                    <div class="skeleton-line skeleton-stat"></div>
                </div>
            </div>
        </div>
        ${skeletons(2)}
    `;
}

/**
 * Render a post card article element with events.
 */
export function renderPostCard(post, opts = {}) {
    const currentUser = getCurrentUser();
    const card = document.createElement("article");
    card.className = "post-card";
    card.dataset.postId = post.id;

    const initials = (post.display_name || post.username || "?")[0].toUpperCase();
    const hasImage = post.has_image;

    card.innerHTML = `
        <div class="post-avatar avatar avatar-md">
            <span class="avatar-initial">${escapeHtml(initials)}</span>
            <img class="avatar-img" src="${avatarUrl(post.username)}" alt="" loading="eager" onerror="this.remove()" />
        </div>
        <div class="post-body">
            <div class="post-header">
                <a class="post-display-name" href="#" data-username="${escapeHtml(post.username)}">${escapeHtml(post.display_name || post.username)}</a>
                <span class="post-username">@${escapeHtml(post.username)}</span>
                <span class="post-time">${relativeTime(post.created_at)}</span>
            </div>
            <div class="post-content">${linkifyContent(post.content || "")}</div>
            ${hasImage ? `<img class="post-image" src="${postImageUrl(post.id)}" alt="Post image" loading="lazy" />` : ""}
            <div class="post-actions">
                <button class="action-btn like-btn ${post.liked_by_me ? "liked" : ""}" data-post-id="${post.id}" aria-label="Like">
                    ${post.liked_by_me ? "❤️" : "🤍"} <span class="like-count">${formatCount(post.like_count || 0)}</span>
                </button>
                <button class="action-btn reply-btn" data-post-id="${post.id}" aria-label="Replies">
                    💬 <span>${formatCount(post.reply_count || 0)}</span>
                </button>
                <button class="action-btn repost-btn ${post.reposted_by_me ? "reposted" : ""}" data-post-id="${post.id}" aria-label="Repost">
                    🔁 <span class="repost-count">${formatCount(post.repost_count || 0)}</span>
                </button>
                <button class="action-btn bookmark-btn ${isBookmarked(post.id) ? "bookmarked" : ""}" data-post-id="${post.id}" aria-label="Bookmark" title="Bookmark post">🔖</button>
                <button class="action-btn share-btn" data-post-id="${post.id}" aria-label="Share" title="Copy post link">🔗</button>
                ${opts.showDelete && post.username === currentUser?.username
                    ? `<button class="action-btn delete-btn" data-post-id="${post.id}" aria-label="Delete">🗑️</button>`
                    : ""}
            </div>
        </div>
    `;

    // Post image click -> open lightbox
    const postImgEl = card.querySelector(".post-image");
    if (postImgEl) {
        postImgEl.addEventListener("click", (e) => {
            e.stopPropagation();
            openLightbox(postImgEl.src, "Post image");
        });
    }

    // Click card → post detail (but not action buttons or links)
    card.addEventListener("click", (e) => {
        if (e.target.closest(".action-btn") || e.target.closest("a") || e.target.closest("img")) return;
        window.location.href = `post.html?id=${post.id}`;
    });

    // Click username → profile
    card.querySelector(".post-display-name").addEventListener("click", (e) => {
        e.preventDefault();
        window.location.href = `profile.html?u=${encodeURIComponent(post.username)}`;
    });

    const likeBtn = card.querySelector(".like-btn");
    likeBtn.dataset.count = post.like_count || 0;
    likeBtn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const wasLiked = likeBtn.classList.contains("liked");
        const current  = parseInt(likeBtn.dataset.count, 10) || 0;
        const next     = wasLiked ? Math.max(0, current - 1) : current + 1;
        likeBtn.classList.toggle("liked", !wasLiked);
        likeBtn.innerHTML = `${!wasLiked ? "❤️" : "🤍"} <span class="like-count">${formatCount(next)}</span>`;
        likeBtn.dataset.count = next;
        const { ok, data } = await apiLikePost(post.id);
        if (ok) {
            likeBtn.classList.toggle("liked", data.liked);
            likeBtn.innerHTML = `${data.liked ? "❤️" : "🤍"} <span class="like-count">${formatCount(data.count)}</span>`;
            likeBtn.dataset.count = data.count;
        } else {
            likeBtn.classList.toggle("liked", wasLiked);
            likeBtn.innerHTML = `${wasLiked ? "❤️" : "🤍"} <span class="like-count">${formatCount(current)}</span>`;
            likeBtn.dataset.count = current;
        }
    });

    // Reply → open post detail
    card.querySelector(".reply-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        window.location.href = `post.html?id=${post.id}`;
    });

    // Repost (optimistic UI)
    const repostBtn = card.querySelector(".repost-btn");
    repostBtn.dataset.count = post.repost_count || 0;
    repostBtn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const wasReposted = repostBtn.classList.contains("reposted");
        const current = parseInt(repostBtn.dataset.count, 10) || 0;
        const next = wasReposted ? Math.max(0, current - 1) : current + 1;
        repostBtn.classList.toggle("reposted", !wasReposted);
        repostBtn.innerHTML = `🔁 <span class="repost-count">${formatCount(next)}</span>`;
        repostBtn.dataset.count = next;
        const { ok, data } = await apiRepostPost(post.id);
        if (ok) {
            repostBtn.classList.toggle("reposted", data.reposted);
            repostBtn.innerHTML = `🔁 <span class="repost-count">${formatCount(data.count)}</span>`;
            repostBtn.dataset.count = data.count;
            if (!wasReposted && data.reposted) showToast("Reposted!", "success");
            if (wasReposted && !data.reposted) showToast("Repost removed.", "success");
        } else {
            repostBtn.classList.toggle("reposted", wasReposted);
            repostBtn.innerHTML = `🔁 <span class="repost-count">${formatCount(current)}</span>`;
            repostBtn.dataset.count = current;
            showToast(data.error || "Could not repost.", "error");
        }
    });

    // Bookmark button
    const bookmarkBtn = card.querySelector(".bookmark-btn");
    if (bookmarkBtn) {
        bookmarkBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            const nowSaved = toggleBookmark(post.id);
            bookmarkBtn.classList.toggle("bookmarked", nowSaved);
            showToast(nowSaved ? "Post bookmarked! 🔖" : "Bookmark removed.", "info");
        });
    }

    // Share link button
    const shareBtn = card.querySelector(".share-btn");
    if (shareBtn) {
        shareBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            const basePath = window.location.pathname.substring(0, window.location.pathname.lastIndexOf("/") + 1);
            const shareUrl = `${window.location.origin}${basePath}post.html?id=${post.id}`;
            navigator.clipboard.writeText(shareUrl).then(() => {
                showToast("Post link copied to clipboard! 📋", "success");
            }).catch(() => {
                showToast("Could not copy link.", "error");
            });
        });
    }

    // Delete button
    const deleteBtn = card.querySelector(".delete-btn");
    if (deleteBtn) {
        deleteBtn.addEventListener("click", async (e) => {
            e.stopPropagation();
            if (!confirm("Delete this post?")) return;
            const { ok } = await apiDeletePost(post.id);
            if (ok) {
                card.remove();
                showToast("Post deleted.", "success");
            } else {
                showToast("Could not delete post.", "error");
            }
        });
    }

    return card;
}
