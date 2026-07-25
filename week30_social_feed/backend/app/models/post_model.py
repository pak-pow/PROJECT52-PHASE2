from app.db import get_db


def create_post(user_id, content, image_path=None, reply_to_id=None, repost_of_id=None):
    """Insert a new post. Returns the new post id."""
    conn = get_db()
    try:
        cursor = conn.execute(
            """INSERT INTO posts (user_id, content, image_path, reply_to_id, repost_of_id)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, content, image_path, reply_to_id, repost_of_id),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


# ── Shared column set for rich post queries ──────────────────
_POST_SELECT = """
    SELECT p.*,
           u.username, u.display_name, u.avatar_path,
           orig_u.username AS orig_username, orig_u.display_name AS orig_display_name,
           orig.content AS orig_content, orig.image_path AS orig_image_path,
           (SELECT COUNT(*) FROM likes  WHERE post_id  = p.id)           AS like_count,
           (SELECT COUNT(*) FROM posts  WHERE reply_to_id  = p.id)       AS reply_count,
           (SELECT COUNT(*) FROM posts  WHERE repost_of_id = p.id)       AS repost_count
    FROM posts p
    JOIN users u ON u.id = p.user_id
    LEFT JOIN posts orig ON orig.id = p.repost_of_id
    LEFT JOIN users orig_u ON orig_u.id = orig.user_id
"""


def get_post_by_id(post_id):
    """Return a single post row (with author info + counts), or None."""
    conn = get_db()
    try:
        return conn.execute(
            _POST_SELECT + " WHERE p.id = ?", (post_id,)
        ).fetchone()
    finally:
        conn.close()


def get_home_feed(user_id, limit=20, before_id=None):
    """Return paginated posts from followed users + own posts (excluding replies)."""
    conn = get_db()
    try:
        where = """
            WHERE p.reply_to_id IS NULL
              AND (p.user_id = ? OR p.user_id IN (
                    SELECT following_id FROM follows WHERE follower_id = ?
                  ))
        """
        params = [user_id, user_id]
        if before_id:
            where += " AND p.id < ?"
            params.append(before_id)
        query = _POST_SELECT + where + " ORDER BY p.id DESC LIMIT ?"
        params.append(limit)
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()


def get_explore_feed(limit=20, before_id=None, tag=None):
    """Return globally trending posts sorted by like count.
    
    Args:
        tag: Optional hashtag string (without #). Filters to posts containing #<tag>.
    """
    conn = get_db()
    try:
        where = " WHERE p.reply_to_id IS NULL AND p.repost_of_id IS NULL"
        params = []
        if tag:
            where += " AND p.content LIKE ?"
            params.append(f"%#{tag}%")
        if before_id:
            where += " AND p.id < ?"
            params.append(before_id)
        query = _POST_SELECT + where + " ORDER BY like_count DESC, p.id DESC LIMIT ?"
        params.append(limit)
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()


def get_user_posts(user_id, limit=20, before_id=None):
    """Return paginated top-level posts by a specific user."""
    conn = get_db()
    try:
        where = " WHERE p.user_id = ? AND p.reply_to_id IS NULL"
        params = [user_id]
        if before_id:
            where += " AND p.id < ?"
            params.append(before_id)
        query = _POST_SELECT + where + " ORDER BY p.id DESC LIMIT ?"
        params.append(limit)
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()


def get_replies_to(post_id, limit=50):
    """Return up to 50 direct replies to a given post, oldest first."""
    conn = get_db()
    try:
        return conn.execute(
            _POST_SELECT + " WHERE p.reply_to_id = ? ORDER BY p.id ASC LIMIT ?",
            (post_id, limit),
        ).fetchall()
    finally:
        conn.close()


def delete_post(post_id, user_id):
    """Delete a post owned by user_id. Returns True if a row was deleted."""
    conn = get_db()
    try:
        result = conn.execute(
            "DELETE FROM posts WHERE id = ? AND user_id = ?", (post_id, user_id)
        )
        conn.commit()
        return result.rowcount > 0
    finally:
        conn.close()


def get_post_count(user_id):
    """Return number of top-level posts by user_id."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM posts WHERE user_id = ? AND reply_to_id IS NULL",
            (user_id,),
        ).fetchone()[0]
    finally:
        conn.close()


def has_reposted(user_id, post_id):
    """Return True if user_id has already reposted post_id."""
    conn = get_db()
    try:
        return bool(conn.execute(
            "SELECT 1 FROM posts WHERE user_id = ? AND repost_of_id = ?",
            (user_id, post_id),
        ).fetchone())
    finally:
        conn.close()


def get_reposted_post_ids(user_id, post_ids):
    """Return set of original post_ids that user_id has reposted."""
    if not post_ids:
        return set()
    conn = get_db()
    try:
        placeholders = ",".join("?" * len(post_ids))
        rows = conn.execute(
            f"SELECT repost_of_id FROM posts WHERE user_id = ? AND repost_of_id IN ({placeholders})",
            [user_id, *post_ids],
        ).fetchall()
        return {r["repost_of_id"] for r in rows}
    finally:
        conn.close()


def toggle_repost(user_id, post_id):
    """Create or delete a repost of post_id by user_id.
    Returns {'reposted': bool, 'count': int}.
    """
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM posts WHERE user_id = ? AND repost_of_id = ?",
            (user_id, post_id),
        ).fetchone()
        if existing:
            conn.execute("DELETE FROM posts WHERE id = ?", (existing["id"],))
            reposted = False
        else:
            conn.execute(
                "INSERT INTO posts (user_id, content, repost_of_id) VALUES (?, '', ?)",
                (user_id, post_id),
            )
            reposted = True
        conn.commit()
        count = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE repost_of_id = ?", (post_id,)
        ).fetchone()[0]
        return {"reposted": reposted, "count": count}
    finally:
        conn.close()
