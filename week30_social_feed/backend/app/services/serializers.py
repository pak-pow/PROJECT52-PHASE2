"""Serializers for posts and users — convert SQLite Row objects to JSON-safe dicts."""


def serialize_post(row, liked_ids=None, reposted_ids=None):
    """Convert a post DB row to a public-facing dict.

    Args:
        row: sqlite3.Row with post + joined user columns.
        liked_ids: set of post_ids liked by the current user.
        reposted_ids: set of post_ids reposted by the current user.
    """
    created_at = row["created_at"] or ""
    if created_at and "T" not in created_at:
        created_at = created_at.replace(" ", "T") + "Z"

    is_repost = bool(row["repost_of_id"])
    row_keys = row.keys() if hasattr(row, "keys") else []
    content = row["orig_content"] if (is_repost and "orig_content" in row_keys and row["orig_content"] is not None) else row["content"]
    image_path = row["orig_image_path"] if (is_repost and "orig_image_path" in row_keys and row["orig_image_path"] is not None) else row["image_path"]
    repost_author_username = row["orig_username"] if (is_repost and "orig_username" in row_keys) else None
    repost_author_display_name = row["orig_display_name"] if (is_repost and "orig_display_name" in row_keys) else None

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "avatar_path": row["avatar_path"],
        "content": content,
        "image_path": image_path,
        "has_image": bool(image_path),
        "reply_to_id": row["reply_to_id"],
        "repost_of_id": row["repost_of_id"],
        "repost_author_username": repost_author_username,
        "repost_author_display_name": repost_author_display_name,
        "like_count": row["like_count"],
        "reply_count": row["reply_count"],
        "repost_count": row["repost_count"],
        "liked_by_me":    (row["id"] in liked_ids)    if liked_ids    is not None else False,
        "reposted_by_me": (row["id"] in reposted_ids) if reposted_ids is not None else False,
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
        "followers_count": follower_count,
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
