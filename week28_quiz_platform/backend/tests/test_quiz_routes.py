import json


# ── GET /api/quizzes ──────────────────────────────────────────────────────────

class TestListQuizzes:
    def test_returns_200(self, client):
        res = client.get("/api/quizzes")
        assert res.status_code == 200

    def test_returns_two_seeded_quizzes(self, client):
        res = client.get("/api/quizzes")
        data = res.get_json()
        assert isinstance(data, list)
        assert len(data) == 4


    def test_quiz_has_expected_fields(self, client):
        res = client.get("/api/quizzes")
        quiz = res.get_json()[0]
        assert "id" in quiz
        assert "title" in quiz
        assert "category" in quiz
        assert "time_limit_seconds" in quiz
        assert "question_count" in quiz

    def test_question_counts_are_five(self, client):
        res = client.get("/api/quizzes")
        for quiz in res.get_json():
            assert quiz["question_count"] == 5


# ── GET /api/quizzes/<id> ─────────────────────────────────────────────────────

class TestGetQuiz:
    def test_returns_200_for_valid_id(self, client):
        res = client.get("/api/quizzes/1")
        assert res.status_code == 200

    def test_returns_404_for_invalid_id(self, client):
        res = client.get("/api/quizzes/999")
        assert res.status_code == 404

    def test_returns_five_questions(self, client):
        res = client.get("/api/quizzes/1")
        data = res.get_json()
        assert len(data["questions"]) == 5

    def test_correct_option_index_is_not_in_response(self, client):
        res = client.get("/api/quizzes/1")
        for question in res.get_json()["questions"]:
            assert "correct_option_index" not in question

    def test_options_is_a_list(self, client):
        res = client.get("/api/quizzes/1")
        for question in res.get_json()["questions"]:
            assert isinstance(question["options"], list)


# ── POST /api/quizzes/<id>/submit ─────────────────────────────────────────────

class TestSubmitQuiz:
    VALID_PAYLOAD = {
        "username": "tester",
        "answers": [0, 0, 1, 2, 1],
        "time_taken": 30
    }

    def test_returns_201_on_valid_submission(self, client):
        res = client.post("/api/quizzes/1/submit", json=self.VALID_PAYLOAD)
        assert res.status_code == 201

    def test_returns_score_and_total(self, client):
        res = client.post("/api/quizzes/1/submit", json=self.VALID_PAYLOAD)
        data = res.get_json()
        assert "score" in data
        assert "total" in data
        assert data["total"] == 5

    def test_results_list_length_matches_questions(self, client):
        res = client.post("/api/quizzes/1/submit", json=self.VALID_PAYLOAD)
        data = res.get_json()
        assert len(data["results"]) == 5

    def test_returns_400_when_username_missing(self, client):
        payload = {"answers": [0, 0, 1, 2, 1], "time_taken": 30}
        res = client.post("/api/quizzes/1/submit", json=payload)
        assert res.status_code == 400

    def test_returns_400_when_answers_wrong_length(self, client):
        payload = {"username": "tester", "answers": [0, 1], "time_taken": 30}
        res = client.post("/api/quizzes/1/submit", json=payload)
        assert res.status_code == 400

    def test_returns_400_when_time_taken_missing(self, client):
        payload = {"username": "tester", "answers": [0, 0, 1, 2, 1]}
        res = client.post("/api/quizzes/1/submit", json=payload)
        assert res.status_code == 400

    def test_returns_404_for_invalid_quiz(self, client):
        res = client.post("/api/quizzes/999/submit", json=self.VALID_PAYLOAD)
        assert res.status_code == 404

    def test_returns_400_when_answers_contain_non_integers(self, client):
        payload = {"username": "tester", "answers": [0, "1", 2, 3, 4], "time_taken": 30}
        res = client.post("/api/quizzes/1/submit", json=payload)
        assert res.status_code == 400
        assert "integer" in res.get_json()["error"]

    def test_returns_400_when_time_taken_negative(self, client):
        payload = {"username": "tester", "answers": [0, 1, 2, 3, 4], "time_taken": -10}
        res = client.post("/api/quizzes/1/submit", json=payload)
        assert res.status_code == 400

    def test_grades_out_of_bounds_answers_as_incorrect(self, client):
        payload = {"username": "tester", "answers": [0, 99, -5, 2, 1], "time_taken": 30}
        res = client.post("/api/quizzes/1/submit", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert len(data["results"]) == 5
        # Index 1 and 2 were out of bounds, so they must be graded incorrect and show None for submitted_answer
        assert data["results"][1]["is_correct"] is False
        assert data["results"][1]["submitted_answer"] is None
        assert data["results"][2]["is_correct"] is False
        assert data["results"][2]["submitted_answer"] is None


# ── GET /api/quizzes/<id>/leaderboard ────────────────────────────────────────

class TestLeaderboard:
    PAYLOAD = {"username": "leader", "answers": [0, 0, 1, 2, 1], "time_taken": 25}

    def test_returns_200(self, client):
        res = client.get("/api/quizzes/1/leaderboard")
        assert res.status_code == 200

    def test_returns_empty_leaderboard_initially(self, client):
        res = client.get("/api/quizzes/1/leaderboard")
        data = res.get_json()
        assert data["leaderboard"] == []

    def test_entry_appears_after_submission(self, client):
        client.post("/api/quizzes/1/submit", json=self.PAYLOAD)
        res = client.get("/api/quizzes/1/leaderboard")
        data = res.get_json()
        assert len(data["leaderboard"]) == 1
        assert data["leaderboard"][0]["username"] == "leader"

    def test_returns_404_for_invalid_quiz(self, client):
        res = client.get("/api/quizzes/999/leaderboard")
        assert res.status_code == 404

    def test_leaderboard_sorted_by_score_then_time(self, client):
        client.post("/api/quizzes/1/submit",
                    json={"username": "slow", "answers": [0, 0, 1, 2, 1], "time_taken": 55})
        client.post("/api/quizzes/1/submit",
                    json={"username": "fast", "answers": [0, 0, 1, 2, 1], "time_taken": 10})
        res = client.get("/api/quizzes/1/leaderboard")
        board = res.get_json()["leaderboard"]
        assert board[0]["username"] == "fast"


# ── GET /api/health ─────────────────────────────────────────────────────────

class TestHealthCheck:
    def test_health_check_returns_200(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "ok"
        assert data["project"] == "week28_quiz_platform"

