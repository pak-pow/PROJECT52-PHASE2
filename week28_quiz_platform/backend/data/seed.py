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
_DIR        = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.environ.get("DATABASE_PATH", os.path.join(_DIR, "quiz.db"))
SCHEMA_PATH = os.path.join(_DIR, "schema.sql")

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
    {
        "title":              "JavaScript Deep Dive",
        "description":        "Master closures, prototype inheritance, DOM, and type coercion.",
        "category":           "JavaScript",
        "time_limit_seconds": 120,
    },
    {
        "title":              "Database Systems & SQL",
        "description":        "Test your knowledge of relations, SQL, indexes, and normalization.",
        "category":           "Databases",
        "time_limit_seconds": 75,
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
    "JavaScript Deep Dive": [
        {
            "text":    "Which of the following is NOT a primitive data type in JavaScript?",
            "options": ["string", "boolean", "object", "symbol"],
            "answer":  2,
        },
        {
            "text":    "What is the result of: typeof null in JavaScript?",
            "options": ["null", "object", "undefined", "string"],
            "answer":  1,
        },
        {
            "text":    "Which method is used to add one or more elements to the end of an array?",
            "options": ["push()", "pop()", "shift()", "unshift()"],
            "answer":  0,
        },
        {
            "text":    "What does DOM stand for?",
            "options": ["Document Object Model", "Domain Object Model", "Direct Object Manipulation", "Document Oriented Middleware"],
            "answer":  0,
        },
        {
            "text":    "Which symbol is used for strict equality comparison?",
            "options": ["=", "==", "===", "!="],
            "answer":  2,
        },
    ],
    "Database Systems & SQL": [
        {
            "text":    "What does SQL stand for?",
            "options": ["Structured Query Language", "Strong Query Language", "Structured Question Language", "Sequential Query Language"],
            "answer":  0,
        },
        {
            "text":    "Which SQL clause is used to filter query results based on aggregate functions?",
            "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"],
            "answer":  1,
        },
        {
            "text":    "What type of join returns all rows from the left table, and matched rows from the right table?",
            "options": ["INNER JOIN", "RIGHT JOIN", "LEFT JOIN", "FULL JOIN"],
            "answer":  2,
        },
        {
            "text":    "Which SQL constraint uniquely identifies each record in a database table?",
            "options": ["FOREIGN KEY", "UNIQUE", "PRIMARY KEY", "CHECK"],
            "answer":  2,
        },
        {
            "text":    "Which SQL command is used to delete a table's structure along with its data?",
            "options": ["DELETE", "TRUNCATE", "DROP", "REMOVE"],
            "answer":  2,
        },
    ],
}

# ── Seeder ────────────────────────────────────────────────────────────────────

def get_connection():
    db_path = os.environ.get("DATABASE_PATH", DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn



def init_schema(conn):
    """Create tables from schema.sql if they don't exist."""
    with open(SCHEMA_PATH, "r") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()


def reset_data(conn):
    """Delete all quiz and question rows (leaderboard cascades automatically)."""
    conn.execute("DELETE FROM questions")
    conn.execute("DELETE FROM quizzes")
    conn.commit()
    print("  [OK] Existing data cleared.")


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
            print(f"  [SKIP] Quiz already exists: '{quiz_data['title']}' (id={quiz_id})")
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
            print(f"  [OK] Inserted quiz: '{quiz_data['title']}' (id={quiz_id})")

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
            print(f"    [OK] Inserted {inserted} question(s).")
        else:
            print(f"    [SKIP] Questions already exist.")

    conn.commit()


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    reset = "--reset" in sys.argv

    print(f"\n[SEEDER] Quiz Platform Seeder")
    print(f"  DB  : {DB_PATH}")
    print(f"  Mode: {'RESET + seed' if reset else 'safe seed (skip existing)'}\n")

    conn = get_connection()
    init_schema(conn)

    if reset:
        print("  Resetting data...")
        reset_data(conn)

    seed(conn)
    conn.close()

    print("\n[DONE] Seeding complete!\n")
