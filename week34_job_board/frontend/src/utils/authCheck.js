export function getStoredUser() {
    try {
        const userStr = localStorage.getItem("jobboard_user");
        return userStr ? JSON.parse(userStr) : null;
    } catch (e) {
        return null;
    }
}

export function setStoredUser(user) {
    if (user) {
        localStorage.setItem("jobboard_user", JSON.stringify(user));
    } else {
        localStorage.removeItem("jobboard_user");
    }
}

export function logoutUser() {
    localStorage.removeItem("jobboard_user");
    window.location.reload();
}
