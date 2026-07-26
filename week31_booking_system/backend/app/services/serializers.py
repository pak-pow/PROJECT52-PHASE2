"""Serializers for converting SQLite Row objects to JSON-safe dicts."""


def serialize_user(row):
    """Convert user row to public dict."""
    if not row:
        return None
    created_at = row["created_at"] or ""
    if created_at and "T" not in created_at:
        created_at = created_at.replace(" ", "T") + "Z"
    return {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "email": row["email"],
        "role": row["role"],
        "created_at": created_at,
    }


def serialize_service(row):
    """Convert service row to public dict."""
    if not row:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "duration_minutes": row["duration_minutes"],
        "price": row["price"],
        "category": row["category"],
    }


def serialize_provider(row):
    """Convert provider row to public dict."""
    if not row:
        return None
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "username": row["username"] if "username" in row.keys() else None,
        "display_name": row["display_name"] if "display_name" in row.keys() else None,
        "email": row["email"] if "email" in row.keys() else None,
        "title": row["title"],
        "bio": row["bio"],
    }


def serialize_booking(row):
    """Convert booking joined row to public dict."""
    if not row:
        return None
    created_at = row["created_at"] or ""
    if created_at and "T" not in created_at:
        created_at = created_at.replace(" ", "T") + "Z"

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "provider_id": row["provider_id"],
        "service_id": row["service_id"],
        "client_name": row["client_name"],
        "client_email": row["client_email"],
        "provider_name": row["provider_name"],
        "provider_title": row["provider_title"],
        "service_title": row["service_title"],
        "duration_minutes": row["duration_minutes"],
        "price": row["price"],
        "service_category": row["service_category"],
        "booking_date": row["booking_date"],
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "status": row["status"],
        "notes": row["notes"],
        "created_at": created_at,
    }
