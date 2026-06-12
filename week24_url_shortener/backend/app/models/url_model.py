from app.utils import db as db_utils


def insert_url(original_url: str, expires_at: str = None) -> int:  # type: ignore
    """
    Insert a new URL record WITHOUT a short_code yet.
    Returns the new row's integer ID so the caller can generate a Base62 code from it.
    short_code stays NULL until update_short_code() is called.
    """
    db = db_utils.get_db()
    cursor = db.execute(
        "INSERT INTO urls (original_url, expires_at) VALUES (?, ?)",
        (original_url, expires_at)
    )
    db.commit()
    return cursor.lastrowid  # type: ignore


def insert_url_with_alias(original_url: str, short_code: str, expires_at: str = None) -> dict:  # type: ignore
    """Insert a URL record with a pre-determined custom alias short code."""
    db = db_utils.get_db()
    cursor = db.execute(
        "INSERT INTO urls (original_url, short_code, expires_at) VALUES (?, ?, ?)",
        (original_url, short_code, expires_at)
    )
    db.commit()
    return find_by_id(cursor.lastrowid)  # type: ignore


def update_short_code(url_id: int, short_code: str) -> None:
    """Update the short code for an existing URL record."""
    db = db_utils.get_db()
    db.execute(
        "UPDATE urls SET short_code = ? WHERE id = ?",
        (short_code, url_id)
    )
    db.commit()


def find_by_code(short_code: str) -> dict | None:
    """Look up a URL record by its short code. Returns None if not found."""
    db = db_utils.get_db()
    row = db.execute(
        "SELECT * FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()
    return dict(row) if row else None


def delete_by_id(url_id: int) -> None:
    """Permanently delete a URL record by primary key (used when a link self-destructs)."""
    db = db_utils.get_db()
    db.execute("DELETE FROM urls WHERE id = ?", (url_id,))
    db.commit()


def find_by_original_url(original_url: str) -> dict | None:
    """
    Check if an active (non-expired) URL has already been shortened.
    Avoids duplicates, but ignores expired records so users can re-shorten.
    """
    db = db_utils.get_db()
    row = db.execute(
        """
        SELECT * FROM urls
        WHERE original_url = ?
          AND short_code IS NOT NULL
          AND (expires_at IS NULL OR expires_at > strftime('%Y-%m-%dT%H:%M:%S', 'now'))
        """,
        (original_url,)
    ).fetchone()
    return dict(row) if row else None


def find_by_id(url_id: int) -> dict | None:
    """Fetch a URL record by primary key."""
    db = db_utils.get_db()
    row = db.execute(
        "SELECT * FROM urls WHERE id = ?",
        (url_id,)
    ).fetchone()
    return dict(row) if row else None


def increment_clicks(short_code: str) -> None:
    """Atomically increment the click counter for a given short code."""
    db = db_utils.get_db()
    db.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
        (short_code,)
    )
    db.commit()


def get_all_urls() -> list[dict]:
    """
    Return all active (non-expired) URL records, ordered by most recently created.
    Expired links are excluded — they self-destruct on access and should not appear
    in the analytics table.
    """
    db = db_utils.get_db()
    rows = db.execute(
        """
        SELECT id, short_code, original_url, clicks, created_at, expires_at
        FROM urls
        WHERE expires_at IS NULL
           OR expires_at > strftime('%Y-%m-%dT%H:%M:%S', 'now')
        ORDER BY created_at DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]
