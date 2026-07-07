import { getRankBadge, getRankClass } from "../utils/helpers.js";

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
