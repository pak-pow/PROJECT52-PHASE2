import { getHeadline } from "../utils/helpers.js";

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
