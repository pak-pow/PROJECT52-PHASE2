/**
 * suggestions.js — Who to Follow sidebar component.
 */
import { apiGetSuggestions, apiToggleFollow, avatarUrl } from "../api/userApi.js";
import { escapeHtml, showToast } from "../utils/helpers.js";

export async function loadSuggestions() {
    const list = document.getElementById("suggestions-list");
    if (!list) return;
    list.innerHTML = '<p class="suggestions-loading">Loading…</p>';
    const users = await apiGetSuggestions();
    if (!users.length) {
        list.innerHTML = '<p class="suggestions-empty">You\'re following everyone!</p>';
        return;
    }
    list.innerHTML = "";
    users.forEach(u => {
        const item = document.createElement("div");
        item.className = "suggestion-item";
        const initials = (u.display_name || u.username || "?")[0].toUpperCase();
        item.innerHTML = `
            <div class="suggestion-avatar avatar avatar-sm">
                <span class="avatar-initial">${escapeHtml(initials)}</span>
                <img class="avatar-img" src="${avatarUrl(u.username)}" alt="" loading="eager" onerror="this.remove()" />
            </div>
            <div class="suggestion-info">
                <span class="suggestion-name">${escapeHtml(u.display_name || u.username)}</span>
                <span class="suggestion-username">@${escapeHtml(u.username)}</span>
            </div>
            <button class="btn-ghost suggestion-follow-btn" data-username="${escapeHtml(u.username)}">Follow</button>
        `;

        // Name click → profile
        item.querySelector(".suggestion-info").addEventListener("click", () => {
            window.location.href = `profile.html?u=${encodeURIComponent(u.username)}`;
        });

        // Follow button
        const followBtn = item.querySelector(".suggestion-follow-btn");
        followBtn.addEventListener("click", async (e) => {
            e.stopPropagation();
            followBtn.disabled = true;
            const { ok, data } = await apiToggleFollow(u.username);
            followBtn.disabled = false;
            if (!ok) { showToast("Could not follow.", "error"); return; }
            if (data.following) {
                followBtn.textContent = "Following";
                followBtn.classList.add("following");
            } else {
                item.remove();
            }
        });
        list.appendChild(item);
    });
}
