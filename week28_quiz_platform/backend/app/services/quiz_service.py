import json


# ── Serializers ───────────────────────────────────────────────────────────────

def serialize_quiz(row):
    """Convert a quiz DB row to a safe public dict."""
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "category": row["category"],
        "time_limit_seconds": row["time_limit_seconds"],
        "question_count": row["question_count"] if "question_count" in row.keys() else None,
    }


def serialize_question_public(row):
    """Convert a question row to a public dict — correct_option_index is EXCLUDED."""
    return {
        "id": row["id"],
        "question_text": row["question_text"],
        "options": json.loads(row["options"]),
    }


def serialize_leaderboard_entry(row):
    """Convert a leaderboard row to a public dict."""
    return {
        "id": row["id"],
        "username": row["username"],
        "score": row["score"],
        "time_taken_seconds": row["time_taken_seconds"],
        "created_at": row["created_at"],
    }


# ── Validation ────────────────────────────────────────────────────────────────

def validate_submission(data, expected_count):
    """
    Validate a submission request body.
    Returns (True, None) on success or (False, error_message) on failure.
    """
    if not data:
        return False, "Request body is required."

    username = data.get("username", "").strip()
    answers = data.get("answers")
    time_taken = data.get("time_taken")

    if not username:
        return False, "Field 'username' is required and cannot be empty."

    if answers is None or not isinstance(answers, list):
        return False, "Field 'answers' must be a list of option indices."

    if len(answers) != expected_count:
        return False, f"Expected {expected_count} answers, got {len(answers)}."

    if time_taken is None or not isinstance(time_taken, (int, float)) or time_taken < 0:
        return False, "Field 'time_taken' must be a non-negative number (seconds)."

    return True, None


# ── Grading ───────────────────────────────────────────────────────────────────

def grade_submission(questions, answers):
    """
    Compare submitted answers against correct_option_index for each question.
    Returns a dict with score, total, and a per-question results list.
    """
    results = []
    score = 0

    for i, question in enumerate(questions):
        submitted = answers[i]
        correct = question["correct_option_index"]
        is_correct = submitted == correct
        if is_correct:
            score += 1

        options = json.loads(question["options"])
        results.append({
            "question_id": question["id"],
            "question_text": question["question_text"],
            "submitted_index": submitted,
            "correct_index": correct,
            "submitted_answer": options[submitted] if 0 <= submitted < len(options) else None,
            "correct_answer": options[correct],
            "is_correct": is_correct,
        })

    return {
        "score": score,
        "total": len(questions),
        "results": results,
    }
