/**
 * authCheck.js — Multi-Page Application authentication guards.
 */
import { getSessionUser, clearSession, saveSession, apiMe } from "../api/authApi.js";
import { setCurrentUser } from "./state.js";

/**
 * Safe navigation helper: avoids reloading if already on target page.
 */
function safeRedirect(targetPage) {
    const current = window.location.pathname;
    if (!current.endsWith("/" + targetPage) && !current.endsWith(targetPage)) {
        const basePath = current.substring(0, current.lastIndexOf("/") + 1);
        window.location.href = `${basePath}${targetPage}`;
    }
}

/**
 * Enforce authentication on protected pages (feed, explore, profile, post).
 * Validates session token against backend. If invalid/expired, redirects to login.html.
 */
export async function requireAuthPage() {
    const user = getSessionUser();
    if (!user || !user.token) {
        clearSession();
        safeRedirect("login.html");
        return null;
    }
    const { ok, data } = await apiMe();
    if (!ok) {
        clearSession();
        safeRedirect("login.html");
        return null;
    }
    saveSession(user.token, data.username, data.display_name, data.avatar_path);
    const updatedUser = {
        token: user.token,
        username: data.username,
        displayName: data.display_name,
        avatarPath: data.avatar_path,
        bio: data.bio,
    };
    setCurrentUser(updatedUser);
    return updatedUser;
}

/**
 * Enforce guest state on auth pages (login, register).
 * If user is already logged in with a valid token, redirects to feed.html.
 * If token is invalid or expired, clears session and stays on auth page.
 */
export async function requireGuestPage() {
    const user = getSessionUser();
    if (user && user.token) {
        const { ok } = await apiMe();
        if (ok) {
            safeRedirect("feed.html");
            return null;
        } else {
            clearSession();
        }
    }
    return true;
}
