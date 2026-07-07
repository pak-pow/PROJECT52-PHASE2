"""
seed.py — Sample data seeder for the Quiz Platform.

Run from the backend/ directory:
    python data/seed.py

Options:
    python data/seed.py          # Seeds only (skips if data already exists)
    python data/seed.py --reset  # Wipes all quiz + question data, then re-seeds
"""

import sqlite3
import json
import os
import sys

# ── Paths ─────────────────────────────────────────────────────────────────────
_DIR     = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.environ.get("DATABASE_PATH", os.path.join(_DIR, "quiz.db"))

# ── Sample Data ───────────────────────────────────────────────────────────────

QUIZZES = [
    {
        "title":              "Web Development Basics",
        "description":        "Test your knowledge of HTML, CSS, and JavaScript fundamentals.",
        "category":           "Web Dev",
        "time_limit_seconds": 60,
    },
    {
        "title":              "Python Programming Trivia",
        "description":        "How well do you know Python? Cover syntax, types, and idioms.",
        "category":           "Python",
        "time_limit_seconds": 90,
    },
]

# Questions are keyed by quiz title for readability.
# Each question: { "text": str, "options": list[str], "answer": int (0-based index) }
QUESTIONS = {
    "Web Development Basics": [
        {
            "text":    "What does HTML stand for?",
            "options": ["HyperText Markup Language", "HighText Machine Language",
                        "HyperText and links Markup Language", "None of the above"],
            "answer":  0,
        },
        {
            "text":    "Which CSS property controls the text size?",
            "options": ["font-size", "text-size", "font-style", "text-style"],
            "answer":  0,
        },
        {
            "text":    "Which JavaScript keyword declares a block-scoped variable?",
            "options": ["var", "let", "define", "set"],
            "answer":  1,
        },
        {
            "text":    "What is the correct HTML element for the largest heading?",
            "options": ["<h6>", "<heading>", "<h1>", "<head>"],
            "answer":  2,
        },
        {
            "text":    "Which event fires when a user clicks an element?",
            "options": ["onhover", "onclick", "onpress", "onselect"],
            "answer":  1,
        },
    ],
    "Python Programming Trivia": [
        {
            "text":    "What data type is the result of: 3 / 2 in Python 3?",
            "options": ["int", "float", "double", "str"],
            "answer":  1,
        },
        {
            "text":    "Which keyword is used to define a function in Python?",
            "options": ["function", "def", "fun", "define"],
            "answer":  1,
        },
        {
            "text":    "What is the output of: bool(0)?",
            "options": ["True", "False", "None", "0"],
            "answer":  1,
        },
        {
            "text":    "Which built-in function returns the length of an object?",
            "options": ["size()", "count()", "len()", "length()"],
            "answer":  2,
        },
        {
            "text":    "What symbol is used for single-line comments in Python?",
            "options": ["//", "--", "#", "/*"],
            "answer":  2,
        },
    ],
}

# ── Seeder ────────────────────────────────────────────────────────────────────

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def reset_data(conn):
    """Delete all quiz and question rows (leaderboard cascades automatically)."""
    conn.execute("DELETE FROM questions")
    conn.execute("DELETE FROM quizzes")
    conn.commit()
    print("  ✓ Existing data cleared.")


def seed(conn):
    """Insert quizzes and questions if they don't already exist."""
    cursor = conn.cursor()

    for quiz_data in QUIZZES:
        # Check if quiz already exists by title
        existing = cursor.execute(
            "SELECT id FROM quizzes WHERE title = ?", (quiz_data["title"],)
        ).fetchone()

        if existing:
            quiz_id = existing["id"]
            print(f"  → Quiz already exists: '{quiz_data['title']}' (id={quiz_id}) — skipping.")
        else:
            cursor.execute(
                """INSERT INTO quizzes (title, description, category, time_limit_seconds)
                   VALUES (?, ?, ?, ?)""",
                (
                    quiz_data["title"],
                    quiz_data["description"],
                    quiz_data["category"],
                    quiz_data["time_limit_seconds"],
                ),
            )
            quiz_id = cursor.lastrowid
            print(f"  ✓ Inserted quiz: '{quiz_data['title']}' (id={quiz_id})")

        # Insert questions for this quiz
        questions = QUESTIONS.get(quiz_data["title"], [])
        inserted = 0
        for q in questions:
            existing_q = cursor.execute(
                "SELECT id FROM questions WHERE quiz_id = ? AND question_text = ?",
                (quiz_id, q["text"]),
            ).fetchone()

            if not existing_q:
                cursor.execute(
                    """INSERT INTO questions (quiz_id, question_text, options, correct_option_index)
                       VALUES (?, ?, ?, ?)""",
                    (quiz_id, q["text"], json.dumps(q["options"]), q["answer"]),
                )
                inserted += 1

        if inserted:
            print(f"    ✓ Inserted {inserted} question(s).")
        else:
            print(f"    → Questions already exist — skipping.")

    conn.commit()


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    reset = "--reset" in sys.argv

    print(f"\n🌱  Quiz Platform Seeder")
    print(f"    DB: {DB_PATH}")
    print(f"    Mode: {'RESET + seed' if reset else 'safe seed (skip existing)'}\n")

    conn = get_connection()

    if reset:
        print("  Resetting data...")
        reset_data(conn)

    seed(conn)
    conn.close()

    print("\n✅  Done!\n")
