export function showView(viewId) {
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    const target = document.getElementById(`view-${viewId}`);
    if (target) target.classList.add("active");
}

export function getTimeTaken(startTime) {
    return Math.round((Date.now() - startTime) / 1000);
}

export function getHeadline(score, total) {
    const pct = score / total;
    if (pct === 1)  return "Perfect Score! 🏆";
    if (pct >= 0.8) return "Great job! 🎉";
    if (pct >= 0.6) return "Not bad! 💪";
    if (pct >= 0.4) return "Keep practicing! 📚";
    return "Better luck next time! 🤔";
}

export function getRankBadge(rank) {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return `<span class="rank-number">${rank}</span>`;
}

export function getRankClass(rank) {
    if (rank === 1) return "rank-gold";
    if (rank === 2) return "rank-silver";
    if (rank === 3) return "rank-bronze";
    return "";
}