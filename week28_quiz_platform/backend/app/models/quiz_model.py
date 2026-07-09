import json
from app.db import get_db


def get_all_quizzes():
    """Return all quizzes with their question counts."""
    conn = get_db()
    try:
        quizzes = conn.execute("""
            SELECT q.id, q.title, q.description, q.category, q.time_limit_seconds,
                   COUNT(qs.id) AS question_count
            FROM quizzes q
            LEFT JOIN questions qs ON qs.quiz_id = q.id
            GROUP BY q.id
            ORDER BY q.id
        """).fetchall()
        return quizzes
    finally:
        conn.close()


def get_quiz_by_id(quiz_id):
    """Return a single quiz row or None."""
    conn = get_db()
    try:
        quiz = conn.execute(
            "SELECT * FROM quizzes WHERE id = ?", (quiz_id,)
        ).fetchone()
        return quiz
    finally:
        conn.close()


def get_questions_by_quiz(quiz_id):
    """Return all questions for a given quiz (includes correct_option_index for grading)."""
    conn = get_db()
    try:
        questions = conn.execute(
            "SELECT * FROM questions WHERE quiz_id = ? ORDER BY id",
            (quiz_id,)
        ).fetchall()
        return questions
    finally:
        conn.close()


def insert_leaderboard_entry(quiz_id, username, score, time_taken):
    """Insert a new leaderboard record and return its id."""
    conn = get_db()
    try:
        cursor = conn.execute(
            """INSERT INTO leaderboard (quiz_id, username, score, time_taken_seconds)
               VALUES (?, ?, ?, ?)""",
            (quiz_id, username, score, time_taken)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_leaderboard_by_quiz(quiz_id, limit=10):
    """Return top scores for a quiz — highest score first, then fastest time."""
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT id, username, score, time_taken_seconds, created_at
               FROM leaderboard
               WHERE quiz_id = ?
               ORDER BY score DESC, time_taken_seconds ASC
               LIMIT ?""",
            (quiz_id, limit)
        ).fetchall()
        return rows
    finally:
        conn.close()
