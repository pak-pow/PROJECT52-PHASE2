import pytest

@pytest.fixture
def users_setup(client):
    # Register User A
    res_a = client.post('/api/auth/register', json={
        'username': 'usera',
        'password': 'password123'
    })
    token_a = res_a.get_json()['token']

    # Register User B
    res_b = client.post('/api/auth/register', json={
        'username': 'userb',
        'password': 'password123'
    })
    token_b = res_b.get_json()['token']

    # Create a board as User A
    res_board = client.post('/api/boards', json={
        'title': 'User A Board',
        'description': 'Owned by A',
        'accent_color': '#6366f1'
    }, headers={'Authorization': f'Bearer {token_a}'})
    board_a = res_board.get_json()

    # Create a column as User A
    res_col = client.post(f'/api/boards/{board_a["id"]}/columns', json={
        'title': 'User A Column'
    }, headers={'Authorization': f'Bearer {token_a}'})
    column_a = res_col.get_json()

    # Create a card as User A
    res_card = client.post(f'/api/columns/{column_a["id"]}/cards', json={
        'title': 'User A Card',
        'description': 'Private to A'
    }, headers={'Authorization': f'Bearer {token_a}'})
    card_a = res_card.get_json()

    return {
        'token_a': token_a,
        'token_b': token_b,
        'board_a': board_a,
        'column_a': column_a,
        'card_a': card_a
    }

def test_list_boards_isolation(client, users_setup):
    # User B lists boards - should be empty (not contain User A's board)
    res = client.get('/api/boards', headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code == 200
    boards = res.get_json()
    assert len(boards) == 0

    # User A lists boards - should see their own board
    res_a = client.get('/api/boards', headers={'Authorization': f'Bearer {users_setup["token_a"]}'})
    assert res_a.status_code == 200
    boards_a = res_a.get_json()
    assert len(boards_a) == 1
    assert boards_a[0]['id'] == users_setup['board_a']['id']

def test_board_get_isolation(client, users_setup):
    # User B attempts to access User A's board - should get 404
    board_id = users_setup['board_a']['id']
    res = client.get(f'/api/boards/{board_id}', headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code == 404

def test_board_update_isolation(client, users_setup):
    # User B attempts to update User A's board - should get 404/400 (not found/unauthorized)
    board_id = users_setup['board_a']['id']
    res = client.put(f'/api/boards/{board_id}', json={'title': 'Hacked Title'}, headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code in [400, 404]

def test_board_delete_isolation(client, users_setup):
    # User B attempts to delete User A's board - should get 404
    board_id = users_setup['board_a']['id']
    res = client.delete(f'/api/boards/{board_id}', headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code == 404

def test_column_create_isolation(client, users_setup):
    # User B attempts to create column on User A's board - should get 404
    board_id = users_setup['board_a']['id']
    res = client.post(f'/api/boards/{board_id}/columns', json={'title': 'Spam Column'}, headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code == 404

def test_column_update_isolation(client, users_setup):
    # User B attempts to rename User A's column - should get 404
    col_id = users_setup['column_a']['id']
    res = client.put(f'/api/columns/{col_id}', json={'title': 'Renamed'}, headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code == 404

def test_column_delete_isolation(client, users_setup):
    # User B attempts to delete User A's column - should get 404
    col_id = users_setup['column_a']['id']
    res = client.delete(f'/api/columns/{col_id}', headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code == 404

def test_card_create_isolation(client, users_setup):
    # User B attempts to create card in User A's column - should get 404
    col_id = users_setup['column_a']['id']
    res = client.post(f'/api/columns/{col_id}/cards', json={'title': 'Spam Card'}, headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code == 404

def test_card_update_isolation(client, users_setup):
    # User B attempts to edit User A's card - should get 404
    card_id = users_setup['card_a']['id']
    res = client.put(f'/api/cards/{card_id}', json={'title': 'Hacked Card'}, headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code == 404

def test_card_delete_isolation(client, users_setup):
    # User B attempts to delete User A's card - should get 404
    card_id = users_setup['card_a']['id']
    res = client.delete(f'/api/cards/{card_id}', headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code == 404

def test_card_move_isolation(client, users_setup):
    # User B attempts to move User A's card - should get 404
    card_id = users_setup['card_a']['id']
    res = client.patch(f'/api/cards/{card_id}/move', json={'column_id': 9999}, headers={'Authorization': f'Bearer {users_setup["token_b"]}'})
    assert res.status_code == 404
