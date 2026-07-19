from app.db import get_db


def toggle_follow(follower_id, following_id):
    """Follow or unfollow a user. Returns {'following': bool}.
    Raises ValueError if a user tries to follow themselves."""
    if follower_id == following_id:
        raise ValueError("You cannot follow yourself.")
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?",
            (follower_id, following_id),
        ).fetchone()
        if existing:
            conn.execute(
                "DELETE FROM follows WHERE follower_id = ? AND following_id = ?",
                (follower_id, following_id),
            )
            following = False
        else:
            conn.execute(
                "INSERT INTO follows (follower_id, following_id) VALUES (?, ?)",
                (follower_id, following_id),
            )
            following = True
        conn.commit()
        return {"following": following}
    finally:
        conn.close()


def get_follower_count(user_id):
    """Return the number of users following user_id."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM follows WHERE following_id = ?", (user_id,)
        ).fetchone()[0]
    finally:
        conn.close()


def get_following_count(user_id):
    """Return the number of users that user_id follows."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM follows WHERE follower_id = ?", (user_id,)
        ).fetchone()[0]
    finally:
        conn.close()


def is_following(follower_id, following_id):
    """Return True if follower_id follows following_id."""
    conn = get_db()
    try:
        return bool(
            conn.execute(
                "SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?",
                (follower_id, following_id),
            ).fetchone()
        )
    finally:
        conn.close()


def get_followers(user_id, limit=50):
    """Return list of user rows who follow user_id."""
    conn = get_db()
    try:
        return conn.execute(
            """SELECT u.id, u.username, u.display_name, u.avatar_path
               FROM users u
               JOIN follows f ON f.follower_id = u.id
               WHERE f.following_id = ?
               ORDER BY f.created_at DESC
               LIMIT ?""",
            (user_id, limit),
        ).fetchall()
    finally:
        conn.close()


def get_following(user_id, limit=50):
    """Return list of user rows that user_id follows."""
    conn = get_db()
    try:
        return conn.execute(
            """SELECT u.id, u.username, u.display_name, u.avatar_path
               FROM users u
               JOIN follows f ON f.following_id = u.id
               WHERE f.follower_id = ?
               ORDER BY f.created_at DESC
               LIMIT ?""",
            (user_id, limit),
        ).fetchall()
    finally:
        conn.close()
