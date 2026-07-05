import json
from app.db import get_db


def get_all_quizzes():
    """Return all quizzes with their question counts."""
    conn = get_db()
    quizzes = conn.execute("""
        SELECT q.id, q.title, q.description, q.category, q.time_limit_seconds,
               COUNT(qs.id) AS question_count
        FROM quizzes q
        LEFT JOIN questions qs ON qs.quiz_id = q.id
        GROUP BY q.id
        ORDER BY q.id
    """).fetchall()
    conn.close()
    return quizzes


def get_quiz_by_id(quiz_id):
    """Return a single quiz row or None."""
    conn = get_db()
    quiz = conn.execute(
        "SELECT * FROM quizzes WHERE id = ?", (quiz_id,)
    ).fetchone()
    conn.close()
    return quiz


def get_questions_by_quiz(quiz_id):
    """Return all questions for a given quiz (includes correct_option_index for grading)."""
    conn = get_db()
    questions = conn.execute(
        "SELECT * FROM questions WHERE quiz_id = ? ORDER BY id",
        (quiz_id,)
    ).fetchall()
    conn.close()
    return questions


def insert_leaderboard_entry(quiz_id, username, score, time_taken):
    """Insert a new leaderboard record and return its id."""
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO leaderboard (quiz_id, username, score, time_taken_seconds)
           VALUES (?, ?, ?, ?)""",
        (quiz_id, username, score, time_taken)
    )
    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()
    return entry_id


def get_leaderboard_by_quiz(quiz_id, limit=10):
    """Return top scores for a quiz — highest score first, then fastest time."""
    conn = get_db()
    rows = conn.execute(
        """SELECT id, username, score, time_taken_seconds, created_at
           FROM leaderboard
           WHERE quiz_id = ?
           ORDER BY score DESC, time_taken_seconds ASC
           LIMIT ?""",
        (quiz_id, limit)
    ).fetchall()
    conn.close()
    return rows
