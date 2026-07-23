/**
 * feed.js — Home feed page controller & infinite scroll.
 */
import { apiFeed } from "../api/postApi.js";
import { renderPostCard, skeletons } from "../components/postCard.js";

let feedLastId  = null;
let feedDone    = false;

export function resetFeed() {
    const feedList = document.getElementById("feed-list");
    if (feedList) feedList.innerHTML = "";
    feedLastId = null;
    feedDone = false;
}

export async function loadFeed(append = false) {
    const feedList   = document.getElementById("feed-list");
    const feedLoader = document.getElementById("feed-loader");
    if (!feedList || !feedLoader) return;

    if (feedDone) return;
    if (!append) feedList.innerHTML = skeletons();
    feedLoader.classList.toggle("hidden", !append);

    const posts = await apiFeed(feedLastId);
    if (!append) feedList.innerHTML = "";

    if (!posts.length && !append) {
        feedList.innerHTML = '<p class="empty-state">No posts yet. Follow some people or write your first post!</p>';
        feedDone = true;
        return;
    }

    if (posts.length < 20) feedDone = true;
    posts.forEach(p => {
        feedList.appendChild(renderPostCard(p, { showDelete: true }));
        feedLastId = p.id;
    });
    feedLoader.classList.add("hidden");
}

export function setupFeedInfiniteScroll() {
    const feedLoader = document.getElementById("feed-loader");
    if (!feedLoader) return;
    const obs = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) loadFeed(true);
    }, { rootMargin: "200px" });
    obs.observe(feedLoader);
}
