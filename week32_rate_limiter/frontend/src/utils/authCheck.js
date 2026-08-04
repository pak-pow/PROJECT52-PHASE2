export function getActiveApiKey() {
    return localStorage.getItem("limiter_api_key") || "demo-free-key";
}

export function setActiveApiKey(key) {
    if (key) {
        localStorage.setItem("limiter_api_key", key);
    }
}

export function clearSession() {
    localStorage.removeItem("limiter_api_key");
}
