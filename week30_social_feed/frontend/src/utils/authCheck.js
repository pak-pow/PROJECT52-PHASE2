/**
 * authCheck.js — Multi-Page Application authentication guards.
 */
import { getSessionUser, clearSession, saveSession, apiMe } from "../api/authApi.js";
import { setCurrentUser } from "./state.js";

/**
 * Enforce authentication on protected pages (feed, explore, profile, post).
 * Validates session token against backend. If invalid/expired, redirects to login.html.
 */
export async function requireAuthPage() {
    const user = getSessionUser();
    if (!user || !user.token) {
        clearSession();
        window.location.href = "login.html";
        return null;
    }
    const { ok, data } = await apiMe();
    if (!ok) {
        clearSession();
        window.location.href = "login.html";
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
 * If user is already logged in, redirects to feed.html.
 */
export function requireGuestPage() {
    const user = getSessionUser();
    if (user && user.token) {
        window.location.href = "feed.html";
        return null;
    }
    return true;
}
