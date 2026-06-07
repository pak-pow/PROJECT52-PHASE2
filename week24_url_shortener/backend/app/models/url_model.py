from app.utils import db as db_utils 

def insert_url(original_url: str, short_code: str) -> dict:
    """Insert a new URL record and return the created row."""
    db = db_utils.get_db() 
    cursor = db.execute(
        "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
        (original_url, short_code)
    )
    db.commit()
    return find_by_id(cursor.lastrowid) # type: ignore


def find_by_code(short_code: str) -> dict | None:
    """Look up a URL record by its short code. Returns None if not found."""
    db = db_utils.get_db()
    row = db.execute(
        "SELECT * FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()
    return dict(row) if row else None


def find_by_original_url(original_url: str) -> dict | None:
    """Check if a URL has already been shortened. Avoids duplicates."""
    db = db_utils.get_db()
    row = db.execute(
        "SELECT * FROM urls WHERE original_url = ?",
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
    """Return all URL records ordered by most recently created."""
    db = db_utils.get_db()
    rows = db.execute(
        "SELECT * FROM urls ORDER BY created_at DESC"
    ).fetchall()
    return [dict(row) for row in rows]
