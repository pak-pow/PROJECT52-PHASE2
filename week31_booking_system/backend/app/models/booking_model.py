import sqlite3
from app.db import get_db

_BOOKING_SELECT = """
    SELECT b.*,
           u.username, u.display_name AS client_name, u.email AS client_email,
           p.title AS provider_title, pu.display_name AS provider_name,
           s.title AS service_title, s.duration_minutes, s.price, s.category AS service_category
    FROM bookings b
    JOIN users u ON u.id = b.user_id
    JOIN providers p ON p.id = b.provider_id
    JOIN users pu ON pu.id = p.user_id
    JOIN services s ON s.id = b.service_id
"""


def create_booking(user_id, provider_id, service_id, booking_date, start_time, end_time, notes=""):
    """Create a new booking. Checks for double-booking conflict first."""
    conn = get_db()
    try:
        # Check for overlapping active bookings for the provider
        conflict = conn.execute(
            """SELECT id FROM bookings
               WHERE provider_id = ?
                 AND booking_date = ?
                 AND status = 'confirmed'
                 AND ((start_time < ? AND end_time > ?)
                      OR (start_time >= ? AND start_time < ?))""",
            (provider_id, booking_date, end_time, start_time, start_time, end_time)
        ).fetchone()

        if conflict:
            raise ValueError("The selected time slot is no longer available. Please select another slot.")

        cursor = conn.execute(
            """INSERT INTO bookings (user_id, provider_id, service_id, booking_date, start_time, end_time, status, notes)
               VALUES (?, ?, ?, ?, ?, ?, 'confirmed', ?)""",
            (user_id, provider_id, service_id, booking_date, start_time, end_time, notes)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        if not hasattr(conn, "commit"):
            conn.close()


def get_user_bookings(user_id):
    """Return all bookings for a client ordered by date and time."""
    conn = get_db()
    return conn.execute(
        _BOOKING_SELECT + " WHERE b.user_id = ? ORDER BY b.booking_date DESC, b.start_time DESC",
        (user_id,)
    ).fetchall()


def get_provider_bookings_for_date(provider_id, booking_date):
    """Return all active confirmed bookings for a provider on a given date."""
    conn = get_db()
    return conn.execute(
        _BOOKING_SELECT + " WHERE b.provider_id = ? AND b.booking_date = ? AND b.status = 'confirmed' ORDER BY b.start_time ASC",
        (provider_id, booking_date)
    ).fetchall()


def get_booking_by_id(booking_id):
    """Return single booking row or None."""
    conn = get_db()
    return conn.execute(_BOOKING_SELECT + " WHERE b.id = ?", (booking_id,)).fetchone()


def cancel_booking(booking_id, user_id):
    """Cancel a booking if owned by user. Returns True on success."""
    conn = get_db()
    booking = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not booking:
        return False
    if booking["user_id"] != user_id:
        raise PermissionError("You can only cancel your own bookings.")

    conn.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
    conn.commit()
    return True
