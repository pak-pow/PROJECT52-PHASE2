"""
test_card_routes.py
Integration tests for card API endpoints.
"""


# ---------------------------------------------------------------------------
# POST /api/columns/<id>/cards
# ---------------------------------------------------------------------------

class TestCreateCard:

    def test_create_returns_201(self, client, column):
        res = client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'New Task'})
        assert res.status_code == 201

    def test_create_returns_full_card_object(self, client, column):
        res = client.post(f'/api/columns/{column["id"]}/cards', json={
            'title':       'Fix bug #42',
            'description': 'Reproduce and patch the login issue',
        })
        data = res.get_json()
        assert data['title'] == 'Fix bug #42'
        assert data['description'] == 'Reproduce and patch the login issue'
        assert data['column_id'] == column['id']
        assert 'id' in data
        assert 'position' in data
        assert 'created_at' in data

    def test_create_missing_title_returns_400(self, client, column):
        res = client.post(f'/api/columns/{column["id"]}/cards', json={'description': 'No title'})
        assert res.status_code == 400
        assert 'error' in res.get_json()

    def test_create_empty_title_returns_400(self, client, column):
        res = client.post(f'/api/columns/{column["id"]}/cards', json={'title': ''})
        assert res.status_code == 400

    def test_create_without_description_returns_201(self, client, column):
        """Description is optional."""
        res = client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'Task with no desc'})
        assert res.status_code == 201

    def test_create_positions_auto_increment(self, client, column):
        """Each new card in the same column gets the next position."""
        card1 = client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'Card 1'}).get_json()
        card2 = client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'Card 2'}).get_json()
        card3 = client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'Card 3'}).get_json()
        assert card1['position'] == 0
        assert card2['position'] == 1
        assert card3['position'] == 2


# ---------------------------------------------------------------------------
# GET /api/columns/<id>/cards
# ---------------------------------------------------------------------------

class TestGetCards:

    def test_empty_list_on_fresh_column(self, client, column):
        res = client.get(f'/api/columns/{column["id"]}/cards')
        assert res.status_code == 200
        assert res.get_json() == []

    def test_returns_all_cards_in_column(self, client, column):
        client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'A'})
        client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'B'})
        res = client.get(f'/api/columns/{column["id"]}/cards')
        assert res.status_code == 200
        assert len(res.get_json()) == 2

    def test_cards_ordered_by_position(self, client, column):
        client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'First'})
        client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'Second'})
        cards = client.get(f'/api/columns/{column["id"]}/cards').get_json()
        assert cards[0]['title'] == 'First'
        assert cards[1]['title'] == 'Second'

    def test_cards_isolated_between_columns(self, client, board, column, second_column):
        """Cards from column A should not appear for column B."""
        client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'Only in col1'})
        res = client.get(f'/api/columns/{second_column["id"]}/cards')
        assert res.get_json() == []


# ---------------------------------------------------------------------------
# GET /api/cards/<id>
# ---------------------------------------------------------------------------

class TestGetSingleCard:

    def test_get_card_returns_200(self, client, card):
        res = client.get(f'/api/cards/{card["id"]}')
        assert res.status_code == 200

    def test_get_card_returns_correct_data(self, client, card):
        res = client.get(f'/api/cards/{card["id"]}')
        data = res.get_json()
        assert data['id'] == card['id']
        assert data['title'] == card['title']

    def test_get_nonexistent_card_returns_404(self, client):
        res = client.get('/api/cards/99999')
        assert res.status_code == 404
        assert 'error' in res.get_json()


# ---------------------------------------------------------------------------
# PUT /api/cards/<id>
# ---------------------------------------------------------------------------

class TestUpdateCard:

    def test_update_returns_200(self, client, card):
        res = client.put(f'/api/cards/{card["id"]}', json={'title': 'Updated title'})
        assert res.status_code == 200

    def test_update_returns_updated_object(self, client, card):
        res = client.put(f'/api/cards/{card["id"]}', json={
            'title':       'New Title',
            'description': 'New description',
        })
        data = res.get_json()
        assert data['title'] == 'New Title'
        assert data['description'] == 'New description'

    def test_update_empty_title_returns_400(self, client, card):
        res = client.put(f'/api/cards/{card["id"]}', json={'title': ''})
        assert res.status_code == 400

    def test_update_partial_preserves_description(self, client, card):
        """Sending only title should not wipe the existing description."""
        original_desc = card['description']
        res = client.put(f'/api/cards/{card["id"]}', json={'title': 'Changed Title'})
        assert res.get_json()['description'] == original_desc

    def test_update_nonexistent_card_returns_400(self, client):
        res = client.put('/api/cards/99999', json={'title': 'Ghost'})
        assert res.status_code == 400

    def test_update_none_description_does_not_crash(self, client, card):
        """Regression: passing description=null must not cause an AttributeError."""
        res = client.put(f'/api/cards/{card["id"]}', json={
            'title':       'Still valid',
            'description': None,
        })
        # Should succeed (200) or cleanly fail (400) — never a 500
        assert res.status_code in (200, 400)
        assert res.status_code != 500


# ---------------------------------------------------------------------------
# DELETE /api/cards/<id>
# ---------------------------------------------------------------------------

class TestDeleteCard:

    def test_delete_returns_204(self, client, card):
        res = client.delete(f'/api/cards/{card["id"]}')
        assert res.status_code == 204

    def test_delete_removes_card(self, client, card):
        client.delete(f'/api/cards/{card["id"]}')
        res = client.get(f'/api/cards/{card["id"]}')
        assert res.status_code == 404

    def test_delete_nonexistent_card_returns_404(self, client):
        res = client.delete('/api/cards/99999')
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /api/cards/<id>/move
# ---------------------------------------------------------------------------

class TestMoveCard:

    def test_move_returns_200(self, client, card, second_column):
        res = client.patch(f'/api/cards/{card["id"]}/move', json={
            'column_id': second_column['id'],
            'position':  0,
        })
        assert res.status_code == 200

    def test_move_updates_column_id(self, client, card, second_column):
        res = client.patch(f'/api/cards/{card["id"]}/move', json={
            'column_id': second_column['id'],
            'position':  0,
        })
        assert res.get_json()['column_id'] == second_column['id']

    def test_move_card_appears_in_new_column(self, client, card, second_column):
        client.patch(f'/api/cards/{card["id"]}/move', json={
            'column_id': second_column['id'],
            'position':  0,
        })
        cards_in_dest = client.get(f'/api/columns/{second_column["id"]}/cards').get_json()
        assert any(c['id'] == card['id'] for c in cards_in_dest)

    def test_move_missing_column_id_returns_400(self, client, card):
        res = client.patch(f'/api/cards/{card["id"]}/move', json={'position': 0})
        assert res.status_code == 400

    def test_move_nonexistent_card_returns_404(self, client, second_column):
        res = client.patch('/api/cards/99999/move', json={
            'column_id': second_column['id'],
            'position':  0,
        })
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /api/columns/<id>/cards/reorder
# ---------------------------------------------------------------------------

class TestReorderCards:

    def test_reorder_returns_200(self, client, column):
        c1 = client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'A'}).get_json()
        c2 = client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'B'}).get_json()
        res = client.patch(
            f'/api/columns/{column["id"]}/cards/reorder',
            json={'updates': [[c1['id'], 1], [c2['id'], 0]]}
        )
        assert res.status_code == 200

    def test_reorder_updates_positions(self, client, column):
        c1 = client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'A'}).get_json()
        c2 = client.post(f'/api/columns/{column["id"]}/cards', json={'title': 'B'}).get_json()
        client.patch(
            f'/api/columns/{column["id"]}/cards/reorder',
            json={'updates': [[c1['id'], 1], [c2['id'], 0]]}
        )
        cards = client.get(f'/api/columns/{column["id"]}/cards').get_json()
        assert cards[0]['title'] == 'B'
        assert cards[1]['title'] == 'A'
