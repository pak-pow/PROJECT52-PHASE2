/**
 * authCheck.js — Multi-Page Application authentication guards.
 */
import { getSessionUser } from "../api/authApi.js";
import { setCurrentUser } from "./state.js";

/**
 * Enforce authentication on protected pages (feed, explore, profile, post).
 * If user is not logged in, redirects to login.html.
 */
export function requireAuthPage() {
    const user = getSessionUser();
    if (!user || !user.token) {
        window.location.href = "login.html";
        return null;
    }
    setCurrentUser(user);
    return user;
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
