const API_BASE = "https://127.0.0.1:5000/api"

export async function fetchQuizzes() {
    const res = await fetch(`${API_BASE}/quizzes`);
    if (!res.ok) throw new Error("Failed to load Quizzes");
    return res.json();
}

