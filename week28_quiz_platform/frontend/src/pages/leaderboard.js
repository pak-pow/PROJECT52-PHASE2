import { getRankBadge, getRankClass } from "../utils/helpers.js";

/* ── HTML Template ───────────────────────────────────────────── */
export const LEADERBOARD_HTML = `
  <main class="leaderboard-main">
    <div class="leaderboard-header">
      <h1 class="leaderboard-title">&#127942; Leaderboard</h1>
      <p id="leaderboard-quiz-name" class="leaderboard-quiz-name"></p>
    </div>

    <div class="leaderboard-table-wrapper">
      <table class="leaderboard-table" id="leaderboard-table">
        <thead>
          <tr>
            <th class="col-rank">Rank</th>
            <th class="col-user">Player</th>
            <th class="col-score">Score</th>
            <th class="col-time">Time</th>
          </tr>
        </thead>
        <tbody id="leaderboard-body"></tbody>
      </table>
    </div>

    <div class="leaderboard-actions">
      <button id="btn-play-again-lb" class="btn-primary">Play Another Quiz</button>
      <button id="btn-back-results" class="btn-secondary">&#8592; Back to Results</button>
    </div>
  </main>
`;

/* ── Renderer ────────────────────────────────────────────────── */
export function renderLeaderboard(data, state) {

  document.getElementById("leaderboard-quiz-name").textContent = data.quiz_title;

  const tbody = document.getElementById("leaderboard-body");
  const total = state.lastResult?.total ?? "?";

  if (data.leaderboard.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" style="text-align:center;color:var(--muted);padding:40px 0;">
          No scores yet — be the first! 🏆
        </td>
      </tr>`;
    return;
  }

  tbody.innerHTML = data.leaderboard
    .map((entry, i) => {
      const rank = i + 1;
      return `
        <tr class="${getRankClass(rank)}">
          <td class="col-rank">${getRankBadge(rank)}</td>
          <td class="col-user">${entry.username}</td>
          <td class="col-score">${entry.score} / ${total}</td>
          <td class="col-time">${entry.time_taken_seconds}s</td>
        </tr>`;
    })
    .join("");
}
