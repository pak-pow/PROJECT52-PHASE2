import { getHeadline } from "../utils/helpers.js";

/* ── HTML Template ───────────────────────────────────────────── */
export const RESULTS_HTML = `
  <main class="results-main">
    <div class="results-hero">
      <div class="score-ring">
        <span id="results-score" class="score-number">0</span>
        <span class="score-divider">/</span>
        <span id="results-total" class="score-total">0</span>
      </div>
      <h2 id="results-headline" class="results-headline">&#8212;</h2>
      <p id="results-meta" class="results-meta"></p>
    </div>

    <div class="breakdown-section">
      <h3 class="breakdown-heading">Question Breakdown</h3>
      <div id="results-breakdown" class="breakdown-list"></div>
    </div>

    <div class="results-actions">
      <button id="btn-view-leaderboard" class="btn-primary">&#127942; View Leaderboard</button>
      <button id="btn-play-again-results" class="btn-secondary">Play Again</button>
    </div>
  </main>
`;

/* ── Renderer ────────────────────────────────────────────────── */
export function renderResults(data, state) {

  // Save result in state so leaderboard can reference total
  state.lastResult = data;

  // Score hero
  document.getElementById("results-score").textContent     = data.score;
  document.getElementById("results-total").textContent     = data.total;
  document.getElementById("results-headline").textContent  = getHeadline(data.score, data.total);
  document.getElementById("results-meta").innerHTML =
    `Completed in <strong>${data.time_taken_seconds} seconds</strong>`;

  // Per-question breakdown
  const breakdown = document.getElementById("results-breakdown");
  breakdown.innerHTML = data.results
    .map((r) => {
      const cls      = r.is_correct ? "correct" : "incorrect";
      const icon     = r.is_correct ? "✓" : "✗";
      const answerLine = r.is_correct
        ? `Your answer: <strong>${r.correct_answer}</strong>`
        : `Your answer: <strong>${r.submitted_answer ?? "No answer (timed out)"}</strong>
           · Correct: <strong>${r.correct_answer}</strong>`;

      return `
        <div class="breakdown-row ${cls}">
          <span class="breakdown-icon">${icon}</span>
          <div class="breakdown-body">
            <p class="breakdown-question">${r.question_text}</p>
            <p class="breakdown-answer">${answerLine}</p>
          </div>
        </div>`;
    })
    .join("");
}
