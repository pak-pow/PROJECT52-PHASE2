const API_BASE = "https://127.0.0.1:5000/api"

export async function fetchQuizzes() {
    const res = await fetch(`${API_BASE}/quizzes`);
    if (!res.ok) throw new Error("Failed to load Quizzes");
    return res.json();
}

export async function fetchQuiz(id) {
    const res = await fetch(`${API_BASE}/quizzes/${id}`);
    if(!res.ok) throw new Error(`Failed to load quiz ${id}`);
    return res.json();
}

export async function submitQuiz(id, payload) {
    const res = await fetch(`${API_BASE}/quizzes/${id}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to submit quiz");
    return res.json();
}
export async function fetchLeaderboard(id) {
    const res = await fetch(`${API_BASE}/quizzes/${id}/leaderboard`);
    if (!res.ok) throw new Error("Failed to load leaderboard");
    return res.json();
}