from flask import Blueprint, jsonify, request
from app.models.quiz_model import (
    get_all_quizzes,
    get_quiz_by_id,
    get_questions_by_quiz,
    insert_leaderboard_entry,
    get_leaderboard_by_quiz,
)
from app.services.quiz_service import (
    serialize_quiz,
    serialize_question_public,
    serialize_leaderboard_entry,
    validate_submission,
    grade_submission,
)

quiz_bp = Blueprint("quiz", __name__, url_prefix="/api/quizzes")


# ── GET /api/quizzes ──────────────────────────────────────────────────────────

@quiz_bp.route("", methods=["GET"])
def list_quizzes():
    """Return all quizzes with their question counts."""
    quizzes = get_all_quizzes()
    return jsonify([serialize_quiz(q) for q in quizzes]), 200


# ── GET /api/quizzes/<id> ─────────────────────────────────────────────────────

@quiz_bp.route("/<int:quiz_id>", methods=["GET"])
def get_quiz(quiz_id):
    """Return a single quiz with its questions. Correct answers are NOT included."""
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return jsonify({"error": f"Quiz {quiz_id} not found."}), 404

    questions = get_questions_by_quiz(quiz_id)
    data = {
        "id": quiz["id"],
        "title": quiz["title"],
        "description": quiz["description"],
        "category": quiz["category"],
        "time_limit_seconds": quiz["time_limit_seconds"],
        "questions": [serialize_question_public(q) for q in questions],
    }
    return jsonify(data), 200


# ── POST /api/quizzes/<id>/submit ─────────────────────────────────────────────

@quiz_bp.route("/<int:quiz_id>/submit", methods=["POST"])
def submit_quiz(quiz_id):
    """Grade submitted answers and save the result to the leaderboard."""
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return jsonify({"error": f"Quiz {quiz_id} not found."}), 404

    questions = get_questions_by_quiz(quiz_id)
    data = request.get_json(silent=True)

    valid, error_msg = validate_submission(data, expected_count=len(questions))
    if not valid:
        return jsonify({"error": error_msg}), 400

    username = data["username"].strip()
    answers = data["answers"]
    time_taken = int(data["time_taken"])

    graded = grade_submission(questions, answers)

    entry_id = insert_leaderboard_entry(
        quiz_id=quiz_id,
        username=username,
        score=graded["score"],
        time_taken=time_taken,
    )

    return jsonify({
        "entry_id": entry_id,
        "username": username,
        "quiz_id": quiz_id,
        "score": graded["score"],
        "total": graded["total"],
        "time_taken_seconds": time_taken,
        "results": graded["results"],
    }), 201


# ── GET /api/quizzes/<id>/leaderboard ────────────────────────────────────────

@quiz_bp.route("/<int:quiz_id>/leaderboard", methods=["GET"])
def get_leaderboard(quiz_id):
    """Return the top 10 scores for a quiz."""
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return jsonify({"error": f"Quiz {quiz_id} not found."}), 404

    rows = get_leaderboard_by_quiz(quiz_id, limit=10)
    return jsonify({
        "quiz_id": quiz_id,
        "quiz_title": quiz["title"],
        "leaderboard": [serialize_leaderboard_entry(r) for r in rows],
    }), 200
