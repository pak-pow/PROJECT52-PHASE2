/**
 * main.js — SocialFeed application entry point.
 * Bootstraps auth state and wires up all page navigation.
 */
import { getSessionUser, saveSession, clearSession, apiLogin, apiRegister, apiLogout } from "./api/authApi.js";
import { apiFeed, apiExplore, apiCreatePost, apiLikePost, apiDeletePost, apiRepostPost, apiGetPost, postImageUrl } from "./api/postApi.js";
import { apiGetProfile, apiGetUserPosts, apiToggleFollow, avatarUrl, apiGetSuggestions, apiUpdateProfile, apiSearchUsers } from "./api/userApi.js";
import { showToast, relativeTime, escapeHtml, linkifyContent, formatCount } from "./utils/helpers.js";

// ── DOM References ─────────────────────────────────────────
const authScreen        = document.getElementById("auth-screen");
const mainApp           = document.getElementById("main-app");
const loginForm         = document.getElementById("login-form");
const registerForm      = document.getElementById("register-form");
const loginError        = document.getElementById("login-error");
const registerError     = document.getElementById("register-error");
const logoutBtn         = document.getElementById("logout-btn");
const sidebarDisplayName = document.getElementById("sidebar-display-name");
const sidebarUsername   = document.getElementById("sidebar-username");
const sidebarAvatar     = document.getElementById("sidebar-avatar");
const composeAvatar     = document.getElementById("compose-avatar");
const composeInput      = document.getElementById("compose-input");
const composeSubmit     = document.getElementById("compose-submit-btn");
const charCounter       = document.getElementById("char-counter");
const feedList          = document.getElementById("feed-list");
const feedLoader        = document.getElementById("feed-loader");
const exploreList       = document.getElementById("explore-list");
const exploreLoader     = document.getElementById("explore-loader");
const backBtn           = document.getElementById("back-btn");

// ── App State ──────────────────────────────────────────────
let currentUser  = null;
let feedLastId   = null;
let feedDone     = false;
let feedLoading  = false;
let exploreLastId  = null;
let exploreDone    = false;
let exploreLoading = false;

// ── Tab switching (Login / Register) ───────────────────────
document.querySelectorAll(".auth-tab").forEach(tab => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".auth-tab").forEach(t => {
            t.classList.toggle("active", t === tab);
            t.setAttribute("aria-selected", t === tab);
        });
        const target = tab.dataset.target;
        ["login-form", "register-form"].forEach(id => {
            document.getElementById(id).classList.toggle("hidden", id !== target);
        });
    });
});

// ── Auth: Login ────────────────────────────────────────────
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginError.classList.add("hidden");
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;
    const btn = document.getElementById("login-submit");
    btn.disabled = true; btn.textContent = "Logging in…";
    const { ok, data } = await apiLogin(username, password);
    btn.disabled = false; btn.textContent = "Login";
    if (!ok) { loginError.textContent = data.error || "Login failed."; loginError.classList.remove("hidden"); return; }
    saveSession(data.token, data.username, data.display_name, data.avatar_path);
    bootApp();
});

// ── Auth: Register ─────────────────────────────────────────
registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    registerError.classList.add("hidden");
    const username    = document.getElementById("reg-username").value.trim();
    const displayName = document.getElementById("reg-display").value.trim();
    const password    = document.getElementById("reg-password").value;
    const btn = document.getElementById("register-submit");
    btn.disabled = true; btn.textContent = "Creating…";
    const { ok, data } = await apiRegister(username, displayName, password);
    btn.disabled = false; btn.textContent = "Create Account";
    if (!ok) { registerError.textContent = data.error || "Registration failed."; registerError.classList.remove("hidden"); return; }
    saveSession(data.token, data.username, data.display_name, "");
    bootApp();
});

// ── Auth: Logout ───────────────────────────────────────────
logoutBtn.addEventListener("click", async () => {
    await apiLogout();
    clearSession();
    showAuth();
});

// ── Page navigation ────────────────────────────────────────
const pages = ["feed", "explore", "profile", "post-detail"];

function showPage(name) {
    pages.forEach(p => {
        document.getElementById(`page-${p}`)?.classList.toggle("hidden", p !== name);
        document.getElementById(`page-${p}`)?.classList.toggle("active", p === name);
    });
    document.querySelectorAll(".nav-item").forEach(el => {
        el.classList.toggle("active", el.dataset.page === name);
    });
}

document.querySelectorAll(".nav-item").forEach(el => {
    el.addEventListener("click", (e) => {
        e.preventDefault();
        const page = el.dataset.page;
        const alreadyOnPage = document.getElementById(`page-${page}`)?.classList.contains("active");
        if (page === "profile") {
            loadProfile(currentUser?.username);
        } else {
            showPage(page);
            if (page === "feed") {
                if (alreadyOnPage) {
                    // Already on home — just scroll to top
                    window.scrollTo({ top: 0, behavior: "smooth" });
                } else {
                    resetFeed(); loadFeed();
                }
            }
            if (page === "explore") { resetExplore(); loadExplore(); }
        }
    });
});

// ── Back button ────────────────────────────────────────────
backBtn.addEventListener("click", () => {
    showPage("feed");
});

// ── Compose: char counter ──────────────────────────────────
composeInput.addEventListener("input", () => {
    charCounter.textContent = 280 - composeInput.value.length;
    charCounter.classList.toggle("char-danger", composeInput.value.length > 260);
});

// ── Compose: post submit ───────────────────────────────────
composeSubmit.addEventListener("click", async () => {
    const content   = composeInput.value.trim();
    const imageFile = document.getElementById("compose-image-input").files[0] || null;
    if (!content && !imageFile) return;
    composeSubmit.disabled = true; composeSubmit.textContent = "Posting…";
    const { ok, data } = await apiCreatePost(content, imageFile);
    composeSubmit.disabled = false; composeSubmit.textContent = "Post";
    if (!ok) { showToast(data.error || "Could not post.", "error"); return; }
    composeInput.value = "";
    charCounter.textContent = "280";
    const imgInput = document.getElementById("compose-image-input");
    imgInput.value = "";
    document.getElementById("compose-image-preview").classList.add("hidden");
    showToast("Posted! 🎉", "success");
    // Prepend new post to top of feed — no full reload
    const newCard = renderPostCard(data, { showDelete: true });
    newCard.classList.add("post-card--new");
    feedList.prepend(newCard);
    // Remove empty-state message if present
    feedList.querySelector(".empty-state")?.remove();
});

// ── Compose: image preview ─────────────────────────────────
const composeImageInput  = document.getElementById("compose-image-input");
const composePreview     = document.getElementById("compose-image-preview");
const composePreviewImg  = document.getElementById("compose-preview-img");
const composeRemoveImage = document.getElementById("compose-remove-image");

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
    // Populate avatar from session
    const modalAvatar = document.getElementById("modal-avatar");
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

// Open triggers
fabBtn.addEventListener("click", openComposeModal);
// sidebar-compose-btn already wires to inline compose on desktop;
// on mobile it's hidden so FAB takes over — no conflict.

// Close triggers
modalCloseBtn.addEventListener("click", closeComposeModal);
composeModal.addEventListener("click", (e) => { if (e.target === composeModal) closeComposeModal(); });

// Char counter
modalInput.addEventListener("input", () => {
    modalCharCounter.textContent = 280 - modalInput.value.length;
    modalCharCounter.classList.toggle("char-danger", modalInput.value.length > 260);
});

// Image preview in modal
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

modalRemoveImage.addEventListener("click", () => {
    modalImageInput.value = "";
    modalPreviewImg.src = "";
    modalImagePreview.classList.add("hidden");
});

// Modal post submit
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
    // Navigate to feed and prepend
    showPage("feed");
    const newCard = renderPostCard(data, { showDelete: true });
    newCard.classList.add("post-card--new");
    feedList.prepend(newCard);
    feedList.querySelector(".empty-state")?.remove();
});

// ── Avatar helper ──────────────────────────────────────────
function makeAvatarEl(username, displayName, sizeClass) {
    const div = document.createElement("div");
    div.className = `avatar ${sizeClass}`;
    div.textContent = (displayName || username || "?")[0].toUpperCase();
    // Try real avatar image
    const img = new Image();
    img.onload = () => {
        div.textContent = "";
        div.style.backgroundImage = `url(${img.src})`;
        div.style.backgroundSize = "cover";
        div.style.backgroundPosition = "center";
    };
    img.src = avatarUrl(username);
    return div;
}

// ── Render post card ───────────────────────────────────────
function renderPostCard(post, opts = {}) {
    const card = document.createElement("article");
    card.className = "post-card";
    card.dataset.postId = post.id;

    const initials = (post.display_name || post.username || "?")[0].toUpperCase();
    const hasImage = post.has_image;

    card.innerHTML = `
        <div class="post-avatar avatar avatar-md">${initials}</div>
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
                ${opts.showDelete && post.username === currentUser?.username
                    ? `<button class="action-btn delete-btn" data-post-id="${post.id}" aria-label="Delete">🗑️</button>`
                    : ""}
            </div>
        </div>
    `;

    // Avatar image load
    const avatarDiv = card.querySelector(".post-avatar");
    const img = new Image();
    img.onload = () => {
        avatarDiv.textContent = "";
        avatarDiv.style.cssText = `background-image:url(${img.src});background-size:cover;background-position:center;`;
    };
    img.src = avatarUrl(post.username);

    // Click card → post detail (but not action buttons or links)
    card.addEventListener("click", (e) => {
        if (e.target.closest(".action-btn") || e.target.closest("a") || e.target.closest("img")) return;
        loadPostDetail(post.id);
    });

    // Click username → profile
    card.querySelector(".post-display-name").addEventListener("click", (e) => {
        e.preventDefault();
        loadProfile(post.username);
    });

    const likeBtn = card.querySelector(".like-btn");
    likeBtn.dataset.count = post.like_count || 0;  // store raw count for accurate optimistic update
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
        loadPostDetail(post.id);
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
            // Roll back
            repostBtn.classList.toggle("reposted", wasReposted);
            repostBtn.innerHTML = `🔁 <span class="repost-count">${formatCount(current)}</span>`;
            repostBtn.dataset.count = current;
            showToast(data.error || "Could not repost.", "error");
        }
    });
    // Delete button (own posts only)
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

// ── Skeleton helper ────────────────────────────────────────
function skeletons(n = 5) {
    return '<div class="skeleton-list">' + Array(n).fill('<div class="skeleton-card"></div>').join("") + '</div>';
}

// ── Feed: load + infinite scroll ───────────────────────────
function resetFeed() { feedList.innerHTML = ""; feedLastId = null; feedDone = false; }

async function loadFeed(append = false) {
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
    posts.forEach(p => { feedList.appendChild(renderPostCard(p, { showDelete: true })); feedLastId = p.id; });
    feedLoader.classList.add("hidden");
}

// ── Explore: load + infinite scroll ───────────────────────
function resetExplore() { exploreList.innerHTML = ""; exploreLastId = null; exploreDone = false; exploreLoading = false; }

async function loadExplore(append = false) {
    if (exploreDone || exploreLoading) return;
    exploreLoading = true;
    if (!append) exploreList.innerHTML = skeletons();
    exploreLoader.classList.toggle("hidden", !append);
    const posts = await apiExplore(exploreLastId);
    exploreLoading = false;
    if (!append) exploreList.innerHTML = "";
    if (!posts.length && !append) {
        exploreList.innerHTML = '<p class="empty-state">Nothing trending yet. Be the first to post!</p>';
        exploreDone = true;
        return;
    }
    if (posts.length < 20) exploreDone = true;
    posts.forEach(p => { exploreList.appendChild(renderPostCard(p)); exploreLastId = p.id; });
    exploreLoader.classList.add("hidden");
}

// ── Infinite scroll via IntersectionObserver ───────────────
function setupInfiniteScroll(loaderEl, loadFn) {
    const obs = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) loadFn(true);
    }, { rootMargin: "200px" });
    obs.observe(loaderEl);
    return obs;
}

// ── Profile page ───────────────────────────────────────────
async function loadProfile(username) {
    if (!username) return;
    showPage("profile");
    const container = document.getElementById("profile-container");
    container.innerHTML = skeletons(3);

    const [{ ok, data: profile }, posts] = await Promise.all([
        apiGetProfile(username),
        apiGetUserPosts(username),
    ]);

    if (!ok) { container.innerHTML = '<p class="empty-state">User not found.</p>'; return; }

    const isMe = currentUser?.username === username;
    const initials = (profile.display_name || profile.username)[0].toUpperCase();

    container.innerHTML = `
        <div class="profile-header">
            <div class="profile-banner"></div>
            <div class="profile-avatar-wrap">
                <div class="avatar avatar-xl profile-avatar" id="pf-avatar">${initials}</div>
                <div class="profile-actions">
                    ${isMe
                        ? `<button class="follow-btn" id="edit-profile-btn">Edit Profile</button>`
                        : `<button class="follow-btn ${profile.is_following ? "following" : ""}" id="follow-btn">
                               ${profile.is_following ? "Following" : "Follow"}
                           </button>`}
                </div>
            </div>
            <div class="profile-info">
                <p class="profile-display-name">${escapeHtml(profile.display_name || profile.username)}</p>
                <p class="profile-username">@${escapeHtml(profile.username)}</p>
                ${profile.bio ? `<p class="profile-bio">${escapeHtml(profile.bio)}</p>` : ""}
                <div class="profile-stats">
                    <span class="profile-stat"><strong>${formatCount(profile.post_count || 0)}</strong> <span>Posts</span></span>
                    <span class="profile-stat"><strong>${formatCount(profile.followers_count || 0)}</strong> <span>Followers</span></span>
                    <span class="profile-stat"><strong>${formatCount(profile.following_count || 0)}</strong> <span>Following</span></span>
                </div>
            </div>
        </div>
        <div id="profile-posts" class="post-list"></div>
    `;

    // Try load avatar image
    const pfAvatar = container.querySelector("#pf-avatar");
    const avImg = new Image();
    avImg.onload = () => {
        pfAvatar.textContent = "";
        pfAvatar.style.cssText = `background-image:url(${avImg.src});background-size:cover;background-position:center;`;
    };
    avImg.src = avatarUrl(username);

    // Follow / unfollow button
    if (!isMe) {
        let following = profile.is_following;
        let followerCount = profile.followers_count || 0;
        const followBtn = container.querySelector("#follow-btn");
        followBtn.addEventListener("click", async () => {
            followBtn.disabled = true;
            const { ok: fOk, data: fData } = await apiToggleFollow(username);
            followBtn.disabled = false;
            if (!fOk) { showToast("Could not update follow.", "error"); return; }
            following = fData.following;
            followerCount = fData.followers_count;
            followBtn.textContent  = following ? "Following" : "Follow";
            followBtn.classList.toggle("following", following);
            const statEl = container.querySelector(".profile-stats .profile-stat:nth-child(2) strong");
            if (statEl) statEl.textContent = formatCount(followerCount);
        });
    }

    // Edit profile button (own profile)
    if (isMe) {
        const editBtn = container.querySelector("#edit-profile-btn");
        if (editBtn) {
            editBtn.addEventListener("click", () => openEditProfileModal(profile, container));
        }
    }

    // Render user posts
    const postsList = container.querySelector("#profile-posts");
    if (!posts.length) {
        postsList.innerHTML = '<p class="empty-state">No posts yet.</p>';
    } else {
        posts.forEach(p => postsList.appendChild(renderPostCard(p, { showDelete: isMe })));
    }
}

// ── Edit Profile Modal ──────────────────────────
function openEditProfileModal(profile, profileContainer) {
    const modal      = document.getElementById("edit-profile-modal");
    const closeBtn   = document.getElementById("edit-profile-close-btn");
    const saveBtn    = document.getElementById("edit-profile-save-btn");
    const nameInput  = document.getElementById("edit-display-name");
    const bioInput   = document.getElementById("edit-bio");
    const bioCounter = document.querySelector(".edit-bio-counter");
    const avatarPrev = document.getElementById("edit-profile-avatar-preview");
    const avatarInput = document.getElementById("edit-avatar-input");
    const errorEl    = document.getElementById("edit-profile-error");

    // Pre-fill current values
    nameInput.value = profile.display_name || "";
    bioInput.value  = profile.bio || "";
    bioCounter.textContent = 160 - bioInput.value.length;
    errorEl.classList.add("hidden");
    errorEl.textContent = "";

    // Show current avatar
    const initials = (profile.display_name || profile.username || "?")[0].toUpperCase();
    avatarPrev.textContent = initials;
    avatarPrev.style.cssText = "";
    const prevImg = new Image();
    prevImg.onload = () => {
        avatarPrev.textContent = "";
        avatarPrev.style.cssText = `background-image:url(${prevImg.src});background-size:cover;background-position:center;`;
    };
    prevImg.src = avatarUrl(profile.username);

    // Reset file input
    avatarInput.value = "";
    let pendingAvatarFile = null;

    // Avatar file change → preview
    const onAvatarChange = () => {
        const file = avatarInput.files[0];
        if (!file) return;
        pendingAvatarFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            avatarPrev.textContent = "";
            avatarPrev.style.cssText = `background-image:url(${e.target.result});background-size:cover;background-position:center;`;
        };
        reader.readAsDataURL(file);
    };
    avatarInput.addEventListener("change", onAvatarChange, { once: true });

    // Bio counter
    const onBioInput = () => {
        bioCounter.textContent = 160 - bioInput.value.length;
    };
    bioInput.addEventListener("input", onBioInput);

    modal.classList.remove("hidden");
    nameInput.focus();

    // Close helpers
    const closeModal = () => {
        modal.classList.add("hidden");
        bioInput.removeEventListener("input", onBioInput);
    };
    closeBtn.onclick  = closeModal;
    modal.onclick = (e) => { if (e.target === modal) closeModal(); };

    // Save
    saveBtn.onclick = async () => {
        const displayName = nameInput.value.trim();
        const bio         = bioInput.value.trim();
        if (!displayName) {
            errorEl.textContent = "Display name cannot be empty.";
            errorEl.classList.remove("hidden");
            return;
        }
        saveBtn.disabled = true; saveBtn.textContent = "Saving…";
        const { ok, data } = await apiUpdateProfile({
            displayName,
            bio,
            avatarFile: pendingAvatarFile,
        });
        saveBtn.disabled = false; saveBtn.textContent = "Save";
        if (!ok) {
            errorEl.textContent = data.error || "Could not save profile.";
            errorEl.classList.remove("hidden");
            return;
        }
        closeModal();
        showToast("Profile updated! ✨", "success");
        // Update sidebar live
        sidebarDisplayName.textContent = data.display_name;
        currentUser.displayName = data.display_name;
        // Update session storage
        saveSession(
            localStorage.getItem("sf_token"),
            data.username,
            data.display_name,
            data.avatar_path,
        );
        // Refresh avatar in sidebar
        const newAvImg = new Image();
        newAvImg.onload = () => {
            sidebarAvatar.textContent = "";
            sidebarAvatar.style.cssText = `background-image:url(${newAvImg.src}?t=${Date.now()});background-size:cover;background-position:center;`;
        };
        newAvImg.src = avatarUrl(data.username) + `?t=${Date.now()}`;
        // Reload profile page in place
        loadProfile(data.username);
    };
}

// ── Post detail + replies ──────────────────────────────────
async function loadPostDetail(postId) {
    showPage("post-detail");
    const detailContainer = document.getElementById("post-detail-container");
    const repliesContainer = document.getElementById("replies-container");
    detailContainer.innerHTML = skeletons(1);
    repliesContainer.innerHTML = skeletons(2);

    const { ok, data } = await apiGetPost(postId);
    if (!ok) { detailContainer.innerHTML = '<p class="empty-state">Post not found.</p>'; return; }

    const post     = data.post;
    const replies  = data.replies || [];

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

    const replyInput  = replyBox.querySelector("#reply-input");
    const replyCounter = replyBox.querySelector("#reply-counter");
    const replySubmit = replyBox.querySelector("#reply-submit-btn");

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
        // Clear empty-state placeholder on first reply
        repliesContainer.querySelector(".empty-state")?.remove();
        // Prepend new reply
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

// ── Show auth vs app ───────────────────────────────────────
function showAuth() {
    authScreen.classList.remove("hidden");
    mainApp.classList.add("hidden");
}

function bootApp() {
    const user = getSessionUser();
    if (!user) { showAuth(); return; }
    currentUser = user;

    authScreen.classList.add("hidden");
    mainApp.classList.remove("hidden");

    // Populate sidebar
    sidebarDisplayName.textContent = user.displayName;
    sidebarUsername.textContent    = `@${user.username}`;
    sidebarAvatar.textContent      = (user.displayName || user.username)[0].toUpperCase();
    composeAvatar.textContent      = (user.displayName || user.username)[0].toUpperCase();

    // Try sidebar avatar image
    const sAvImg = new Image();
    sAvImg.onload = () => {
        sidebarAvatar.textContent = "";
        sidebarAvatar.style.cssText = `background-image:url(${sAvImg.src});background-size:cover;background-position:center;`;
    };
    sAvImg.src = avatarUrl(user.username);

    // Sidebar compose btn → show feed + scroll to compose
    document.getElementById("sidebar-compose-btn").addEventListener("click", () => {
        showPage("feed");
        composeInput.focus();
    });

    // Infinite scroll observers
    setupInfiniteScroll(feedLoader,    (append) => loadFeed(append));
    setupInfiniteScroll(exploreLoader, (append) => loadExplore(append));

    resetFeed();
    showPage("feed");
    loadFeed();
    loadSuggestions();
}

// ── User Search (Explore page) ─────────────────────────────
const searchInput    = document.getElementById("user-search-input");
const searchResults  = document.getElementById("search-results");
const searchClearBtn = document.getElementById("search-clear-btn");
const exploreList    = document.getElementById("explore-list");
const exploreLoader  = document.getElementById("explore-loader");
const exploreSub     = document.querySelector(".explore-sub");

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
            <div class="search-result-info">
                <span class="search-result-name">${escapeHtml(u.display_name || u.username)}</span>
                <span class="search-result-username">@${escapeHtml(u.username)}</span>
            </div>
            <button class="btn-ghost suggestion-follow-btn" data-username="${escapeHtml(u.username)}">Follow</button>
        `;
        // Avatar image
        const avDiv = item.querySelector(".search-result-avatar");
        const img = new Image();
        img.onload = () => {
            avDiv.textContent = "";
            avDiv.style.cssText = `background-image:url(${img.src});background-size:cover;background-position:center;`;
        };
        img.src = avatarUrl(u.username);
        // Click name → profile
        item.querySelector(".search-result-info").addEventListener("click", () => loadProfile(u.username));
        // Follow button
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
        if (exploreSub) exploreSub.classList.remove("hidden");
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

searchInput.addEventListener("input", () => doSearch(searchInput.value));

searchClearBtn.addEventListener("click", () => {
    searchInput.value = "";
    doSearch("");
    searchInput.focus();
});

// Clear search when leaving explore page
window.addEventListener("navigate", (e) => {
    if (e.detail?.page !== "explore" && searchInput.value) {
        searchInput.value = "";
        searchResults.classList.add("hidden");
        exploreList.classList.remove("hidden");
        if (exploreSub) exploreSub.classList.remove("hidden");
        searchClearBtn.classList.add("hidden");
    }
});

async function loadSuggestions() {
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
            <div class="suggestion-avatar avatar avatar-sm">${initials}</div>
            <div class="suggestion-info">
                <span class="suggestion-name">${escapeHtml(u.display_name || u.username)}</span>
                <span class="suggestion-username">@${escapeHtml(u.username)}</span>
            </div>
            <button class="btn-ghost suggestion-follow-btn" data-username="${escapeHtml(u.username)}">Follow</button>
        `;
        // Load avatar
        const avDiv = item.querySelector(".suggestion-avatar");
        const img = new Image();
        img.onload = () => {
            avDiv.textContent = "";
            avDiv.style.cssText = `background-image:url(${img.src});background-size:cover;background-position:center;`;
        };
        img.src = avatarUrl(u.username);
        // Name click → profile
        item.querySelector(".suggestion-info").addEventListener("click", () => loadProfile(u.username));
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
                // Remove from suggestions list on unfollow (shouldn't happen but handle it)
                item.remove();
            }
        });
        list.appendChild(item);
    });
}

// ── @mention delegated click ─────────────────────────
document.addEventListener("click", (e) => {
    const mention = e.target.closest(".mention");
    if (mention) {
        e.preventDefault();
        const username = mention.textContent.replace(/^@/, "").trim();
        if (username) loadProfile(username);
    }
});

// ── Boot ──────────────────────────────────────────────
bootApp();
