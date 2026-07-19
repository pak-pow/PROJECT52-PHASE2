"""Serializers for posts and users — convert SQLite Row objects to JSON-safe dicts."""


def serialize_post(row, liked_ids=None):
    """Convert a post DB row to a public-facing dict.

    Args:
        row: sqlite3.Row with post + joined user columns.
        liked_ids: set of post_ids liked by the current user (for liked_by_me flag).
    """
    created_at = row["created_at"] or ""
    if created_at and "T" not in created_at:
        created_at = created_at.replace(" ", "T") + "Z"

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "avatar_path": row["avatar_path"],
        "content": row["content"],
        "image_path": row["image_path"],
        "reply_to_id": row["reply_to_id"],
        "repost_of_id": row["repost_of_id"],
        "like_count": row["like_count"],
        "reply_count": row["reply_count"],
        "repost_count": row["repost_count"],
        "liked_by_me": (row["id"] in liked_ids) if liked_ids is not None else False,
        "created_at": created_at,
    }


def serialize_user(row, follower_count=0, following_count=0, is_following=False, post_count=0):
    """Convert a user DB row to a public profile dict."""
    created_at = row["created_at"] or ""
    if created_at and "T" not in created_at:
        created_at = created_at.replace(" ", "T") + "Z"

    return {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "bio": row["bio"],
        "avatar_path": row["avatar_path"],
        "follower_count": follower_count,
        "following_count": following_count,
        "is_following": is_following,
        "post_count": post_count,
        "created_at": created_at,
    }


def serialize_mini_user(row):
    """Compact user dict for follower/following lists."""
    return {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "avatar_path": row["avatar_path"],
    }
