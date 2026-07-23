/**
 * explorePage.js — Explore page controller.
 */
import { requireAuthPage } from "../utils/authCheck.js";
import { initSidebar } from "../components/sidebar.js";
import { initComposeModal } from "../components/composeModal.js";
import { loadSuggestions } from "../components/suggestions.js";
import { renderPostCard, skeletons } from "../components/postCard.js";
import { apiExplore } from "../api/postApi.js";
import { apiSearchUsers, apiToggleFollow, avatarUrl } from "../api/userApi.js";
import { showToast, escapeHtml, debounce } from "../utils/helpers.js";

const currentUser = await requireAuthPage();
if (currentUser) {
    initSidebar("explore");
    initComposeModal();

    const searchInput    = document.getElementById("user-search-input");
    const searchResults  = document.getElementById("search-results");
    const searchClearBtn = document.getElementById("search-clear-btn");
    const exploreList    = document.getElementById("explore-list");
    const exploreLoader  = document.getElementById("explore-loader");
    const exploreSub     = document.querySelector(".explore-sub");

    const urlParams = new URLSearchParams(window.location.search);
    let activeTag = urlParams.get("tag")?.trim() || null;

    let exploreLastId  = null;
    let exploreDone    = false;
    let exploreLoading = false;

    async function loadExplore(append = false) {
        if (exploreDone || exploreLoading) return;
        exploreLoading = true;

        if (!append) exploreList.innerHTML = skeletons();
        exploreLoader.classList.toggle("hidden", !append);

        const posts = await apiExplore(exploreLastId, activeTag);
        exploreLoading = false;

        if (!append) exploreList.innerHTML = "";
        if (!posts.length && !append) {
            const msg = activeTag
                ? `<p class="empty-state">No posts tagged <strong>#${escapeHtml(activeTag)}</strong> yet.</p>`
                : '<p class="empty-state">Nothing trending yet. Be the first to post!</p>';
            exploreList.innerHTML = msg;
            exploreDone = true;
            return;
        }

        if (posts.length < 20) exploreDone = true;
        posts.forEach(p => {
            exploreList.appendChild(renderPostCard(p));
            exploreLastId = p.id;
        });
        exploreLoader.classList.add("hidden");
    }

    if (activeTag) {
        const banner = document.createElement("div");
        banner.id = "tag-filter-banner";
        banner.className = "tag-filter-banner";
        const exploreSection = document.querySelector(".content");
        const searchWrap = document.querySelector(".search-bar-wrap");
        if (searchWrap) searchWrap.after(banner);

        banner.innerHTML = `
            <span>Showing posts tagged <strong>#${escapeHtml(activeTag)}</strong></span>
            <button class="btn-ghost tag-clear-btn" id="tag-clear-btn">✕ Clear</button>
        `;

        document.getElementById("tag-clear-btn").addEventListener("click", () => {
            activeTag = null;
            banner.remove();
            if (exploreSub) exploreSub.classList.remove("hidden");
            window.history.replaceState({}, "", "explore.html");
            exploreLastId = null;
            exploreDone = false;
            loadExplore();
        });

        if (exploreSub) exploreSub.classList.add("hidden");
    }

    // User Search
    function renderSearchResults(users) {
        searchResults.innerHTML = "";
        if (!users.length) {
            searchResults.innerHTML = '<p class="empty-state">No users found.</p>';
            return;
        }
        users.forEach(u => {
            const item = document.createElement("div");
            item.className = "search-result-item";
            const initials = (u.display_name || u.username || "?")[0].toUpperCase();
            item.innerHTML = `
                <div class="search-result-avatar avatar avatar-md">${escapeHtml(initials)}</div>
                <div class="search-result-info" onclick="window.location.href='profile.html?u=${encodeURIComponent(u.username)}'">
                    <span class="search-result-name">${escapeHtml(u.display_name || u.username)}</span>
                    <span class="search-result-username">@${escapeHtml(u.username)}</span>
                </div>
                <button class="btn-ghost suggestion-follow-btn" data-username="${escapeHtml(u.username)}">Follow</button>
            `;
            const avDiv = item.querySelector(".search-result-avatar");
            const img = new Image();
            img.onload = () => {
                avDiv.textContent = "";
                avDiv.style.cssText = `background-image:url(${img.src});background-size:cover;background-position:center;`;
            };
            img.src = avatarUrl(u.username);

            const followBtn = item.querySelector(".suggestion-follow-btn");
            followBtn.addEventListener("click", async (e) => {
                e.stopPropagation();
                followBtn.disabled = true;
                const { ok, data } = await apiToggleFollow(u.username);
                followBtn.disabled = false;
                if (!ok) { showToast("Could not follow.", "error"); return; }
                followBtn.textContent = data.following ? "Following" : "Follow";
                followBtn.classList.toggle("following", data.following);
            });
            searchResults.appendChild(item);
        });
    }

    const doSearch = debounce(async (q) => {
        if (!q.trim()) {
            searchResults.classList.add("hidden");
            exploreList.classList.remove("hidden");
            exploreLoader.classList.remove("hidden");
            if (exploreSub && !activeTag) exploreSub.classList.remove("hidden");
            searchClearBtn.classList.add("hidden");
            return;
        }
        searchClearBtn.classList.remove("hidden");
        searchResults.classList.remove("hidden");
        exploreList.classList.add("hidden");
        exploreLoader.classList.add("hidden");
        if (exploreSub) exploreSub.classList.add("hidden");
        searchResults.innerHTML = '<p class="empty-state">Searching…</p>';
        const users = await apiSearchUsers(q);
        renderSearchResults(users);
    }, 300);

    if (searchInput) searchInput.addEventListener("input", () => doSearch(searchInput.value));

    if (searchClearBtn) {
        searchClearBtn.addEventListener("click", () => {
            searchInput.value = "";
            doSearch("");
            searchInput.focus();
        });
    }

    const obs = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) loadExplore(true);
    }, { rootMargin: "200px" });
    obs.observe(exploreLoader);

    loadExplore();
    loadSuggestions();
}
