"""
test_column_routes.py
Integration tests for column API endpoints.
"""


# ---------------------------------------------------------------------------
# POST /api/boards/<id>/columns
# ---------------------------------------------------------------------------

class TestCreateColumn:

    def test_create_returns_201(self, client, board):
        res = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'Backlog'})
        assert res.status_code == 201

    def test_create_returns_full_column_object(self, client, board):
        res = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'In Progress'})
        data = res.get_json()
        assert data['title'] == 'In Progress'
        assert data['board_id'] == board['id']
        assert 'id' in data
        assert 'position' in data
        assert 'created_at' in data

    def test_create_missing_title_returns_400(self, client, board):
        res = client.post(f'/api/boards/{board["id"]}/columns', json={})
        assert res.status_code == 400
        assert 'error' in res.get_json()

    def test_create_empty_title_returns_400(self, client, board):
        res = client.post(f'/api/boards/{board["id"]}/columns', json={'title': '   '})
        assert res.status_code == 400

    def test_positions_auto_increment(self, client, board):
        """Each new column should get the next position number."""
        c1 = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'Col 1'}).get_json()
        c2 = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'Col 2'}).get_json()
        c3 = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'Col 3'}).get_json()
        assert c1['position'] == 0
        assert c2['position'] == 1
        assert c3['position'] == 2


# ---------------------------------------------------------------------------
# GET /api/boards/<id>/columns
# ---------------------------------------------------------------------------

class TestGetColumns:

    def test_empty_list_on_fresh_board(self, client, board):
        res = client.get(f'/api/boards/{board["id"]}/columns')
        assert res.status_code == 200
        assert res.get_json() == []

    def test_returns_all_columns_for_board(self, client, board):
        client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'A'})
        client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'B'})
        res = client.get(f'/api/boards/{board["id"]}/columns')
        assert res.status_code == 200
        assert len(res.get_json()) == 2

    def test_columns_ordered_by_position(self, client, board):
        client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'First'})
        client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'Second'})
        data = client.get(f'/api/boards/{board["id"]}/columns').get_json()
        assert data[0]['title'] == 'First'
        assert data[1]['title'] == 'Second'

    def test_columns_isolated_between_boards(self, client):
        """Columns from board A should not appear for board B."""
        b1 = client.post('/api/boards', json={'title': 'B1', 'accent_color': '#111111'}).get_json()
        b2 = client.post('/api/boards', json={'title': 'B2', 'accent_color': '#222222'}).get_json()
        client.post(f'/api/boards/{b1["id"]}/columns', json={'title': 'Only in B1'})
        res = client.get(f'/api/boards/{b2["id"]}/columns')
        assert res.get_json() == []


# ---------------------------------------------------------------------------
# PUT /api/columns/<id>
# ---------------------------------------------------------------------------

class TestUpdateColumn:

    def test_update_returns_200(self, client, column):
        res = client.put(f'/api/columns/{column["id"]}', json={'title': 'Renamed'})
        assert res.status_code == 200

    def test_update_returns_updated_object(self, client, column):
        res = client.put(f'/api/columns/{column["id"]}', json={'title': 'Done'})
        data = res.get_json()
        assert data['title'] == 'Done'
        assert data['id'] == column['id']

    def test_update_empty_title_returns_400(self, client, column):
        res = client.put(f'/api/columns/{column["id"]}', json={'title': ''})
        assert res.status_code == 400

    def test_update_nonexistent_column_returns_404(self, client):
        res = client.put('/api/columns/99999', json={'title': 'Ghost'})
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/columns/<id>
# ---------------------------------------------------------------------------

class TestDeleteColumn:

    def test_delete_returns_204(self, client, column):
        res = client.delete(f'/api/columns/{column["id"]}')
        assert res.status_code == 204

    def test_delete_removes_column(self, client, board, column):
        client.delete(f'/api/columns/{column["id"]}')
        columns = client.get(f'/api/boards/{board["id"]}/columns').get_json()
        assert not any(c['id'] == column['id'] for c in columns)

    def test_delete_nonexistent_column_returns_404(self, client):
        res = client.delete('/api/columns/99999')
        assert res.status_code == 404

    def test_delete_column_cascades_cards(self, client, column, card):
        """Deleting a column should remove all its cards."""
        client.delete(f'/api/columns/{column["id"]}')
        res = client.get(f'/api/cards/{card["id"]}')
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /api/boards/<id>/columns/reorder
# ---------------------------------------------------------------------------

class TestReorderColumns:

    def test_reorder_returns_200(self, client, board):
        c1 = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'A'}).get_json()
        c2 = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'B'}).get_json()
        # Swap positions
        res = client.patch(
            f'/api/boards/{board["id"]}/columns/reorder',
            json={'updates': [[c1['id'], 1], [c2['id'], 0]]}
        )
        assert res.status_code == 200

    def test_reorder_updates_positions(self, client, board):
        c1 = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'A'}).get_json()
        c2 = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'B'}).get_json()
        client.patch(
            f'/api/boards/{board["id"]}/columns/reorder',
            json={'updates': [[c1['id'], 1], [c2['id'], 0]]}
        )
        cols = client.get(f'/api/boards/{board["id"]}/columns').get_json()
        assert cols[0]['title'] == 'B'
        assert cols[1]['title'] == 'A'
