from app.db import get_db


def get_all_providers():
    """Return all providers joined with user display names."""
    conn = get_db()
    return conn.execute(
        """SELECT p.*, u.username, u.display_name, u.email
           FROM providers p
           JOIN users u ON u.id = p.user_id
           ORDER BY u.display_name ASC"""
    ).fetchall()


def get_providers_for_service(service_id):
    """Return list of providers qualified to perform a specific service."""
    conn = get_db()
    return conn.execute(
        """SELECT p.*, u.username, u.display_name, u.email
           FROM providers p
           JOIN users u ON u.id = p.user_id
           JOIN provider_services ps ON ps.provider_id = p.id
           WHERE ps.service_id = ?
           ORDER BY u.display_name ASC""",
        (service_id,)
    ).fetchall()


def get_provider_by_id(provider_id):
    """Return single provider joined with user info or None."""
    conn = get_db()
    return conn.execute(
        """SELECT p.*, u.username, u.display_name, u.email
           FROM providers p
           JOIN users u ON u.id = p.user_id
           WHERE p.id = ?""",
        (provider_id,)
    ).fetchone()


def get_provider_availability(provider_id, day_of_week):
    """Return provider working hours for a given day of week (0=Mon, 6=Sun)."""
    conn = get_db()
    return conn.execute(
        """SELECT * FROM provider_availability
           WHERE provider_id = ? AND day_of_week = ?""",
        (provider_id, day_of_week)
    ).fetchall()
