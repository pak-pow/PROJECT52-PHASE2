"""
Tests for the expense CRUD routes:
  GET    /api/expenses/
  POST   /api/expenses/
  PUT    /api/expenses/<id>
  DELETE /api/expenses/<id>
  GET    /api/expenses/summary
"""
import pytest  # type: ignore
from tests.conftest import make_expense


# ─── AUTHENTICATION GUARD ────────────────────────────────────────────────────

class TestAuthGuard:
    """Every expense endpoint must reject unauthenticated requests."""

    def test_get_expenses_requires_auth(self, client):
        assert client.get('/api/expenses/').status_code == 401

    def test_post_expense_requires_auth(self, client):
        assert client.post('/api/expenses/', json={}).status_code == 401

    def test_put_expense_requires_auth(self, client):
        assert client.put('/api/expenses/1', json={}).status_code == 401

    def test_delete_expense_requires_auth(self, client):
        assert client.delete('/api/expenses/1').status_code == 401

    def test_summary_requires_auth(self, client):
        assert client.get('/api/expenses/summary').status_code == 401


# ─── CREATE (POST) ───────────────────────────────────────────────────────────

class TestCreateExpense:
    """Tests for POST /api/expenses/"""

    def test_create_valid_expense_returns_201(self, client, auth_headers):
        """A complete, valid payload should return 201 with the new ID."""
        res = make_expense(client, auth_headers, amount=99.99, category="Food")
        assert res.status_code == 201
        assert "id" in res.get_json()

    def test_create_expense_with_zero_amount_returns_400(self, client, auth_headers):
        """Amount of 0 is not a valid expense and should be rejected."""
        res = make_expense(client, auth_headers, amount=0)
        assert res.status_code == 400

    def test_create_expense_with_negative_amount_returns_400(self, client, auth_headers):
        """Negative amounts should be rejected."""
        res = make_expense(client, auth_headers, amount=-10)
        assert res.status_code == 400

    def test_create_expense_with_string_amount_returns_400(self, client, auth_headers):
        """Non-numeric amount should be rejected with 400."""
        res = client.post('/api/expenses/', json={
            "amount": "lots",
            "category": "Food",
            "date": "2026-05-01"
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_create_expense_with_excessive_amount_returns_400(self, client, auth_headers):
        """An unrealistically large amount (>999999) should be rejected."""
        res = make_expense(client, auth_headers, amount=9999999)
        assert res.status_code == 400

    def test_create_expense_missing_category_returns_400(self, client, auth_headers):
        """Missing category should return 400."""
        res = client.post('/api/expenses/', json={
            "amount": 50,
            "date": "2026-05-01"
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_create_expense_missing_date_returns_400(self, client, auth_headers):
        """Missing date should return 400."""
        res = client.post('/api/expenses/', json={
            "amount": 50,
            "category": "Food"
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_create_expense_invalid_date_format_returns_400(self, client, auth_headers):
        """A date that is not YYYY-MM-DD format should be rejected."""
        res = make_expense(client, auth_headers, date="01-05-2026")
        assert res.status_code == 400

    def test_create_expense_non_date_string_returns_400(self, client, auth_headers):
        """A completely invalid date string should be rejected."""
        res = make_expense(client, auth_headers, date="not-a-date")
        assert res.status_code == 400

    def test_create_expense_category_too_long_returns_400(self, client, auth_headers):
        """A category exceeding 50 characters should be rejected."""
        res = make_expense(client, auth_headers, category="A" * 51)
        assert res.status_code == 400

    def test_create_expense_amount_is_rounded_to_2_decimal_places(self, client, auth_headers):
        """Amounts with more than 2 decimal places should be stored rounded."""
        make_expense(client, auth_headers, amount=10.999)
        res = client.get('/api/expenses/', headers=auth_headers)
        stored_amount = res.get_json()[0]["amount"]
        assert stored_amount == 11.0  # 10.999 rounded to 2dp

    def test_create_expense_strips_category_whitespace(self, client, auth_headers):
        """Leading/trailing whitespace on category should be stripped before storage."""
        make_expense(client, auth_headers, category="  Food  ")
        res = client.get('/api/expenses/', headers=auth_headers)
        assert res.get_json()[0]["category"] == "Food"

    def test_response_does_not_expose_user_id(self, client, auth_headers):
        """The expense list response should not include the user_id field."""
        make_expense(client, auth_headers)
        res = client.get('/api/expenses/', headers=auth_headers)
        expense = res.get_json()[0]
        assert "user_id" not in expense


# ─── READ (GET) ──────────────────────────────────────────────────────────────

class TestGetExpenses:
    """Tests for GET /api/expenses/"""

    def test_get_expenses_returns_empty_list_for_new_user(self, client, auth_headers):
        """A user with no expenses should receive an empty array."""
        res = client.get('/api/expenses/', headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json() == []

    def test_get_expenses_returns_only_own_expenses(self, client, auth_headers, other_user_headers):
        """User A must not see User B's expenses."""
        make_expense(client, auth_headers, category="My Expense")
        make_expense(client, other_user_headers, category="Their Expense")

        res = client.get('/api/expenses/', headers=auth_headers)
        expenses = res.get_json()
        assert len(expenses) == 1
        assert expenses[0]["category"] == "My Expense"

    def test_get_expenses_ordered_by_date_descending(self, client, auth_headers):
        """Expenses should be returned with the most recent date first."""
        make_expense(client, auth_headers, date="2026-05-01", category="Old")
        make_expense(client, auth_headers, date="2026-05-31", category="New")
        res = client.get('/api/expenses/', headers=auth_headers)
        expenses = res.get_json()
        assert expenses[0]["category"] == "New"
        assert expenses[1]["category"] == "Old"

    def test_pagination_limit_param(self, client, auth_headers):
        """?limit=2 should return at most 2 expenses even if more exist."""
        for i in range(5):
            make_expense(client, auth_headers, amount=10 + i)
        res = client.get('/api/expenses/?limit=2', headers=auth_headers)
        assert len(res.get_json()) == 2

    def test_pagination_page_param(self, client, auth_headers):
        """?page=2&limit=2 should return the second page of results."""
        for i in range(4):
            make_expense(client, auth_headers, amount=float(10 + i),
                         date=f"2026-05-{10 + i:02d}")
        page1 = client.get('/api/expenses/?page=1&limit=2', headers=auth_headers).get_json()
        page2 = client.get('/api/expenses/?page=2&limit=2', headers=auth_headers).get_json()

        # Pages should not overlap
        page1_ids = {e["id"] for e in page1}
        page2_ids = {e["id"] for e in page2}
        assert page1_ids.isdisjoint(page2_ids)
        assert len(page2) == 2


# ─── UPDATE (PUT) ────────────────────────────────────────────────────────────

class TestUpdateExpense:
    """Tests for PUT /api/expenses/<id>"""

    def test_update_expense_success(self, client, auth_headers):
        """A valid update should return 200 and persist the new values."""
        post_res = make_expense(client, auth_headers, amount=50, category="Food")
        expense_id = post_res.get_json()["id"]

        put_res = client.put(f'/api/expenses/{expense_id}', json={
            "amount": 75.00,
            "category": "Transport",
            "description": "Updated",
            "date": "2026-05-20"
        }, headers=auth_headers)
        assert put_res.status_code == 200

        # Verify the value actually changed in the database
        get_res = client.get('/api/expenses/', headers=auth_headers)
        updated = get_res.get_json()[0]
        assert updated["amount"] == 75.00
        assert updated["category"] == "Transport"

    def test_update_nonexistent_expense_returns_404(self, client, auth_headers):
        """Trying to update an ID that doesn't exist should return 404."""
        res = client.put('/api/expenses/9999', json={
            "amount": 50,
            "category": "Food",
            "date": "2026-05-01"
        }, headers=auth_headers)
        assert res.status_code == 404

    def test_update_another_users_expense_returns_404(self, client, auth_headers, other_user_headers):
        """User A must not be able to update User B's expenses."""
        post_res = make_expense(client, other_user_headers, amount=100)
        expense_id = post_res.get_json()["id"]

        res = client.put(f'/api/expenses/{expense_id}', json={
            "amount": 999,
            "category": "Hacked",
            "date": "2026-05-01"
        }, headers=auth_headers)
        assert res.status_code == 404

    def test_update_with_invalid_data_returns_400(self, client, auth_headers):
        """An update with invalid data should be rejected before hitting the DB."""
        post_res = make_expense(client, auth_headers)
        expense_id = post_res.get_json()["id"]

        res = client.put(f'/api/expenses/{expense_id}', json={
            "amount": -99,
            "category": "Food",
            "date": "2026-05-01"
        }, headers=auth_headers)
        assert res.status_code == 400


# ─── DELETE ──────────────────────────────────────────────────────────────────

class TestDeleteExpense:
    """Tests for DELETE /api/expenses/<id>"""

    def test_delete_expense_success(self, client, auth_headers):
        """Deleting an existing expense should return 200 and remove it."""
        post_res = make_expense(client, auth_headers)
        expense_id = post_res.get_json()["id"]

        del_res = client.delete(f'/api/expenses/{expense_id}', headers=auth_headers)
        assert del_res.status_code == 200

        get_res = client.get('/api/expenses/', headers=auth_headers)
        assert len(get_res.get_json()) == 0

    def test_delete_nonexistent_expense_returns_404(self, client, auth_headers):
        """Attempting to delete a non-existent ID should return 404."""
        res = client.delete('/api/expenses/9999', headers=auth_headers)
        assert res.status_code == 404

    def test_delete_another_users_expense_returns_404(self, client, auth_headers, other_user_headers):
        """User A must not be able to delete User B's expenses."""
        post_res = make_expense(client, other_user_headers)
        expense_id = post_res.get_json()["id"]

        res = client.delete(f'/api/expenses/{expense_id}', headers=auth_headers)
        assert res.status_code == 404

        # Verify expense still exists for its owner
        get_res = client.get('/api/expenses/', headers=other_user_headers)
        assert len(get_res.get_json()) == 1


# ─── SUMMARY ─────────────────────────────────────────────────────────────────

class TestSummary:
    """Tests for GET /api/expenses/summary"""

    def test_summary_aggregates_by_category(self, client, auth_headers):
        """Multiple expenses in the same category should sum correctly."""
        make_expense(client, auth_headers, amount=10.00, category="Food", date="2026-05-01")
        make_expense(client, auth_headers, amount=20.00, category="Food", date="2026-05-02")
        make_expense(client, auth_headers, amount=50.00, category="Rent", date="2026-05-01")

        res = client.get('/api/expenses/summary', headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()

        # Rent should be first (highest total)
        assert data[0]["category"] == "Rent"
        assert data[0]["total_amount"] == 50.00
        assert data[1]["category"] == "Food"
        assert data[1]["total_amount"] == 30.00

    def test_summary_date_range_filter(self, client, auth_headers):
        """?start_date=&end_date= should only aggregate expenses within the range."""
        make_expense(client, auth_headers, amount=100, category="Food", date="2026-05-15")
        make_expense(client, auth_headers, amount=200, category="Food", date="2026-06-15")

        res = client.get('/api/expenses/summary?start_date=2026-05-01&end_date=2026-05-31', headers=auth_headers)
        data = res.get_json()
        assert len(data) == 1
        assert data[0]["total_amount"] == 100.00

    def test_summary_start_date_filter(self, client, auth_headers):
        """?start_date=2026-01-01 should exclude expenses before that date."""
        make_expense(client, auth_headers, amount=100, category="Food", date="2026-05-01")
        make_expense(client, auth_headers, amount=500, category="Food", date="2025-05-01")

        res = client.get('/api/expenses/summary?start_date=2026-01-01', headers=auth_headers)
        data = res.get_json()
        assert data[0]["total_amount"] == 100.00

    def test_summary_returns_empty_for_no_expenses(self, client, auth_headers):
        """A user with no expenses should get an empty summary."""
        res = client.get('/api/expenses/summary', headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json() == []

    def test_summary_only_shows_own_data(self, client, auth_headers, other_user_headers):
        """Summary must only include the authenticated user's own data."""
        make_expense(client, auth_headers, amount=100, category="My Food")
        make_expense(client, other_user_headers, amount=9999, category="Their Rent")

        res = client.get('/api/expenses/summary', headers=auth_headers)
        data = res.get_json()
        categories = [row["category"] for row in data]
        assert "Their Rent" not in categories
        assert "My Food" in categories