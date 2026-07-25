/**
 * bookmarks.js — Client-side persistent bookmark management.
 */

export function getBookmarks() {
    try {
        return JSON.parse(localStorage.getItem("sf_bookmarks") || "[]");
    } catch {
        return [];
    }
}

export function isBookmarked(postId) {
    const list = getBookmarks();
    return list.includes(Number(postId));
}

export function toggleBookmark(postId) {
    let list = getBookmarks();
    const id = Number(postId);
    const index = list.indexOf(id);
    let bookmarked = false;
    if (index >= 0) {
        list.splice(index, 1);
        bookmarked = false;
    } else {
        list.push(id);
        bookmarked = true;
    }
    localStorage.setItem("sf_bookmarks", JSON.stringify(list));
    return bookmarked;
}
