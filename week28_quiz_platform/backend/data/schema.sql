-- ── Tables ────────────────────────────────────────────────────────────────
-- schema.sql defines structure ONLY.
-- To populate sample data, run: python data/seed.py

CREATE TABLE IF NOT EXISTS quizzes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               TEXT NOT NULL,
    description         TEXT,
    category            TEXT NOT NULL,
    time_limit_seconds  INTEGER NOT NULL DEFAULT 60
);

CREATE TABLE IF NOT EXISTS questions (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id              INTEGER NOT NULL,
    question_text        TEXT NOT NULL,
    options              TEXT NOT NULL,
    correct_option_index INTEGER NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS leaderboard (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id             INTEGER NOT NULL,
    username            TEXT NOT NULL,
    score               INTEGER NOT NULL,
    time_taken_seconds  INTEGER NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);