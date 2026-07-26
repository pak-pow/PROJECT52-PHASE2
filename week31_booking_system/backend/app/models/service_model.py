from app.db import get_db


def get_all_services(category=None):
    """Return all available services, optionally filtered by category."""
    conn = get_db()
    if category:
        return conn.execute(
            "SELECT * FROM services WHERE category = ? ORDER BY title ASC", (category,)
        ).fetchall()
    return conn.execute("SELECT * FROM services ORDER BY title ASC").fetchall()


def get_service_by_id(service_id):
    """Return service by id or None."""
    conn = get_db()
    return conn.execute("SELECT * FROM services WHERE id = ?", (service_id,)).fetchone()
