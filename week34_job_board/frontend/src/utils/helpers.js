export function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

export function showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3500);
}

export function formatSalary(minSalary, maxSalary) {
    if (!minSalary && !maxSalary) return "Salary Undisclosed";
    const minK = minSalary ? `$${(minSalary / 1000).toFixed(0)}k` : "";
    const maxK = maxSalary ? `$${(maxSalary / 1000).toFixed(0)}k` : "";
    if (minK && maxK) return `${minK} - ${maxK} / yr`;
    return minK ? `From ${minK}` : `Up to ${maxK}`;
}
