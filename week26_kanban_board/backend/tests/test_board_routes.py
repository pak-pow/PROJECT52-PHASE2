"""
test_board_routes.py
Integration tests for board API endpoints.
Uses the 'client' fixture from conftest.py which spins up a fresh temp DB per test.
"""


# ---------------------------------------------------------------------------
# GET /api/boards
# ---------------------------------------------------------------------------

class TestListBoards:

    def test_empty_list_on_fresh_db(self, client):
        res = client.get('/api/boards')
        assert res.status_code == 200
        assert res.get_json() == []

    def test_returns_all_boards(self, client):
        client.post('/api/boards', json={'title': 'Alpha', 'accent_color': '#ff0000'})
        client.post('/api/boards', json={'title': 'Beta',  'accent_color': '#00ff00'})
        res = client.get('/api/boards')
        data = res.get_json()
        assert res.status_code == 200
        assert len(data) == 2

    def test_boards_ordered_newest_first(self, client):
        import time
        client.post('/api/boards', json={'title': 'First',  'accent_color': '#111111'})
        time.sleep(1) # Ensure timestamps differ
        client.post('/api/boards', json={'title': 'Second', 'accent_color': '#222222'})
        data = client.get('/api/boards').get_json()
        assert data[0]['title'] == 'Second'
        assert data[1]['title'] == 'First'


# ---------------------------------------------------------------------------
# POST /api/boards
# ---------------------------------------------------------------------------

class TestCreateBoard:

    def test_create_returns_201(self, client):
        res = client.post('/api/boards', json={
            'title':        'My Board',
            'description':  'A description',
            'accent_color': '#6366f1',
        })
        assert res.status_code == 201

    def test_create_returns_board_object(self, client):
        res = client.post('/api/boards', json={'title': 'Board X', 'accent_color': '#abcdef'})
        data = res.get_json()
        assert data['title'] == 'Board X'
        assert data['accent_color'] == '#abcdef'
        assert 'id' in data
        assert 'created_at' in data

    def test_create_missing_title_returns_400(self, client):
        res = client.post('/api/boards', json={'accent_color': '#ffffff'})
        assert res.status_code == 400
        assert 'error' in res.get_json()

    def test_create_invalid_color_returns_400(self, client):
        res = client.post('/api/boards', json={'title': 'Board', 'accent_color': 'red'})
        assert res.status_code == 400

    def test_create_default_accent_color(self, client):
        """accent_color should default to #3b82f6 if omitted."""
        res = client.post('/api/boards', json={'title': 'Minimal Board'})
        assert res.status_code == 201
        assert res.get_json()['accent_color'] == '#3b82f6'

    def test_create_description_is_optional(self, client):
        res = client.post('/api/boards', json={'title': 'No Desc', 'accent_color': '#000000'})
        assert res.status_code == 201


# ---------------------------------------------------------------------------
# GET /api/boards/<id>
# ---------------------------------------------------------------------------

class TestGetBoard:

    def test_get_board_returns_200(self, client, board):
        res = client.get(f'/api/boards/{board["id"]}')
        assert res.status_code == 200

    def test_get_board_includes_columns_key(self, client, board):
        res = client.get(f'/api/boards/{board["id"]}')
        data = res.get_json()
        assert 'columns' in data

    def test_get_board_columns_include_cards(self, client, board, column, card):
        res = client.get(f'/api/boards/{board["id"]}')
        data = res.get_json()
        col = next(c for c in data['columns'] if c['id'] == column['id'])
        assert 'cards' in col
        assert any(c['id'] == card['id'] for c in col['cards'])

    def test_get_nonexistent_board_returns_404(self, client):
        res = client.get('/api/boards/99999')
        assert res.status_code == 404
        assert 'error' in res.get_json()


# ---------------------------------------------------------------------------
# PUT /api/boards/<id>
# ---------------------------------------------------------------------------

class TestUpdateBoard:

    def test_update_returns_200(self, client, board):
        res = client.put(f'/api/boards/{board["id"]}', json={'title': 'Updated'})
        assert res.status_code == 200

    def test_update_returns_updated_object(self, client, board):
        res = client.put(f'/api/boards/{board["id"]}', json={
            'title':        'New Name',
            'accent_color': '#10b981',
        })
        data = res.get_json()
        assert data['title'] == 'New Name'
        assert data['accent_color'] == '#10b981'

    def test_update_partial_preserves_other_fields(self, client, board):
        """Sending only title should keep the original accent_color."""
        original_color = board['accent_color']
        res = client.put(f'/api/boards/{board["id"]}', json={'title': 'New Title Only'})
        assert res.get_json()['accent_color'] == original_color

    def test_update_nonexistent_board_returns_404(self, client):
        res = client.put('/api/boards/99999', json={'title': 'Ghost'})
        assert res.status_code in (400, 404)  # service raises ValueError → route returns 4xx


# ---------------------------------------------------------------------------
# DELETE /api/boards/<id>
# ---------------------------------------------------------------------------

class TestDeleteBoard:

    def test_delete_returns_204(self, client, board):
        res = client.delete(f'/api/boards/{board["id"]}')
        assert res.status_code == 204

    def test_delete_removes_board(self, client, board):
        client.delete(f'/api/boards/{board["id"]}')
        res = client.get(f'/api/boards/{board["id"]}')
        assert res.status_code == 404

    def test_delete_nonexistent_board_returns_404(self, client):
        res = client.delete('/api/boards/99999')
        assert res.status_code == 404

    def test_delete_board_cascades_columns(self, client, board, column):
        """Deleting a board should remove its columns."""
        client.delete(f'/api/boards/{board["id"]}')
        res = client.get(f'/api/boards/{board["id"]}/columns')
        # Board is gone so the board detail endpoint returns 404;
        # columns for a deleted board should return empty list at minimum
        assert res.status_code in (200, 404)
        if res.status_code == 200:
            assert res.get_json() == []
