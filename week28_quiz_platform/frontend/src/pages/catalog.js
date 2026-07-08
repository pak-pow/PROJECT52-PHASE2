/* ── HTML Template ───────────────────────────────────────────── */
export const CATALOG_HTML = `
  <header class="site-header">
    <div class="header-inner">
      <div class="logo">
        <span class="logo-icon">&#x26A1;</span>
        <span class="logo-text">Quiz<span class="logo-accent">Arena</span></span>
      </div>
      <p class="header-sub">Pick a quiz. Beat the clock. Own the leaderboard.</p>
    </div>
  </header>

  <main class="catalog-main">
    <div class="section-heading">
      <h1>Available Quizzes</h1>
      <p class="section-sub">Select a quiz below to begin</p>
    </div>
    <div id="quiz-catalog-grid" class="catalog-grid">
      <div class="quiz-card skeleton">
        <div class="skeleton-badge"></div>
        <div class="skeleton-title"></div>
        <div class="skeleton-meta"></div>
      </div>
      <div class="quiz-card skeleton">
        <div class="skeleton-badge"></div>
        <div class="skeleton-title"></div>
        <div class="skeleton-meta"></div>
      </div>
    </div>
  </main>
`;

/* ── Renderer ────────────────────────────────────────────────── */

export function renderCatalog(quizzes, onQuizSelect) {
  const grid = document.getElementById("quiz-catalog-grid");

  if (quizzes.length === 0) {
    grid.innerHTML = `
      <p style="color:var(--muted);text-align:center;grid-column:1/-1;padding:40px 0;">
        No quizzes available yet.
      </p>`;
    return;
  }

  grid.innerHTML = quizzes
    .map(
      (q) => `
      <div class="quiz-card" id="quiz-card-${q.id}">
        <div class="card-category-badge">📂 ${q.category}</div>
        <h2 class="card-title">${q.title}</h2>
        <p class="card-desc">${q.description || ""}</p>
        <div class="card-meta">
          <span class="card-meta-item"><span>❓</span>${q.question_count} Questions</span>
          <span class="card-meta-item"><span>⏱️</span>${q.time_limit_seconds}s</span>
          <span class="card-cta">Start →</span>
        </div>
      </div>`
    )
    .join("");

  quizzes.forEach((q) => {
    document
      .getElementById(`quiz-card-${q.id}`)
      .addEventListener("click", () => onQuizSelect(q.id));
  });
}
