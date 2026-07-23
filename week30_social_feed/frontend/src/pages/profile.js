/**
 * profile.js — User profile page controller & edit profile modal.
 */
import { apiGetProfile, apiGetUserPosts, apiToggleFollow, apiUpdateProfile, avatarUrl } from "../api/userApi.js";
import { saveSession } from "../api/authApi.js";
import { renderPostCard, skeletons } from "../components/postCard.js";
import { showToast, escapeHtml, formatCount } from "../utils/helpers.js";
import { getCurrentUser } from "../utils/state.js";
import { showPage } from "../router.js";

export async function loadProfile(username) {
    if (!username) return;
    showPage("profile");
    const container = document.getElementById("profile-container");
    container.innerHTML = skeletons(3);

    const currentUser = getCurrentUser();

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

export function openEditProfileModal(profile, profileContainer) {
    const modal      = document.getElementById("edit-profile-modal");
    const closeBtn   = document.getElementById("edit-profile-close-btn");
    const saveBtn    = document.getElementById("edit-profile-save-btn");
    const nameInput  = document.getElementById("edit-display-name");
    const bioInput   = document.getElementById("edit-bio");
    const bioCounter = document.querySelector(".edit-bio-counter");
    const avatarPrev = document.getElementById("edit-profile-avatar-preview");
    const avatarInput = document.getElementById("edit-avatar-input");
    const errorEl    = document.getElementById("edit-profile-error");

    const sidebarDisplayName = document.getElementById("sidebar-display-name");
    const sidebarAvatar     = document.getElementById("sidebar-avatar");

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

    const onBioInput = () => {
        bioCounter.textContent = 160 - bioInput.value.length;
    };
    bioInput.addEventListener("input", onBioInput);

    modal.classList.remove("hidden");
    nameInput.focus();

    const closeModal = () => {
        modal.classList.add("hidden");
        bioInput.removeEventListener("input", onBioInput);
    };
    closeBtn.onclick  = closeModal;
    modal.onclick = (e) => { if (e.target === modal) closeModal(); };

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
        
        if (sidebarDisplayName) sidebarDisplayName.textContent = data.display_name;
        const currentUser = getCurrentUser();
        if (currentUser) currentUser.displayName = data.display_name;
        
        saveSession(
            localStorage.getItem("sf_token"),
            data.username,
            data.display_name,
            data.avatar_path,
        );
        
        if (sidebarAvatar) {
            const newAvImg = new Image();
            newAvImg.onload = () => {
                sidebarAvatar.textContent = "";
                sidebarAvatar.style.cssText = `background-image:url(${newAvImg.src}?t=${Date.now()});background-size:cover;background-position:center;`;
            };
            newAvImg.src = avatarUrl(data.username) + `?t=${Date.now()}`;
        }
        loadProfile(data.username);
    };
}
