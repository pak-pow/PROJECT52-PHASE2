from app.db import get_db


def toggle_like(user_id, post_id):
    """Toggle a like on a post. Returns {'liked': bool, 'count': int}."""
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?",
            (user_id, post_id),
        ).fetchone()
        if existing:
            conn.execute(
                "DELETE FROM likes WHERE user_id = ? AND post_id = ?",
                (user_id, post_id),
            )
            liked = False
        else:
            conn.execute(
                "INSERT INTO likes (user_id, post_id) VALUES (?, ?)",
                (user_id, post_id),
            )
            liked = True
        conn.commit()
        count = conn.execute(
            "SELECT COUNT(*) FROM likes WHERE post_id = ?", (post_id,)
        ).fetchone()[0]
        return {"liked": liked, "count": count}
    finally:
        conn.close()


def get_liked_post_ids(user_id, post_ids):
    """Return a set of post_ids (from the given list) that user_id has liked."""
    if not post_ids:
        return set()
    conn = get_db()
    try:
        placeholders = ",".join("?" * len(post_ids))
        rows = conn.execute(
            f"SELECT post_id FROM likes WHERE user_id = ? AND post_id IN ({placeholders})",
            [user_id, *post_ids],
        ).fetchall()
        return {r["post_id"] for r in rows}
    finally:
        conn.close()
