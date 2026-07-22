import os
from flask import Blueprint, request, jsonify, g, send_file
from app.services.auth_service import require_auth
from app.services.serializers import serialize_user, serialize_mini_user
from app.services.image_service import save_avatar
from app.services.serializers import serialize_post
from app.models.user_model import get_user_by_username, update_user_profile
from app.models.post_model import get_user_posts, get_post_count, get_reposted_post_ids
from app.models.like_model import get_liked_post_ids
from app.models.follow_model import (
    toggle_follow, get_follower_count, get_following_count,
    is_following, get_followers, get_following,
)
from app.config.settings import Config

user_bp = Blueprint("users", __name__, url_prefix="/api/users")


@user_bp.route("/<username>", methods=["GET"])
@require_auth
def get_profile(username):
    """GET /api/users/<username> — fetch public profile with follow stats."""
    user = get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(serialize_user(
        user,
        follower_count=get_follower_count(user["id"]),
        following_count=get_following_count(user["id"]),
        is_following=is_following(g.user["id"], user["id"]),
        post_count=get_post_count(user["id"]),
    )), 200


@user_bp.route("/<username>/posts", methods=["GET"])
@require_auth
def get_posts(username):
    """GET /api/users/<username>/posts — paginated posts by a user."""
    user = get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found."}), 404
    before_id = request.args.get("before", type=int)
    rows = get_user_posts(user["id"], Config.FEED_PAGE_SIZE, before_id)
    post_ids = [r["id"] for r in rows]
    liked    = get_liked_post_ids(g.user["id"], post_ids)
    reposted = get_reposted_post_ids(g.user["id"], post_ids)
    return jsonify([serialize_post(r, liked, reposted) for r in rows]), 200


@user_bp.route("/me", methods=["PUT"])
@require_auth
def update_profile():
    """PUT /api/users/me — update display name, bio, and/or avatar."""
    display_name = request.form.get("display_name", "").strip() or None
    bio = request.form.get("bio", "").strip()

    if display_name and len(display_name) > Config.MAX_DISPLAY_NAME_LEN:
        return jsonify({"error": f"Display name cannot exceed {Config.MAX_DISPLAY_NAME_LEN} characters."}), 400
    if bio and len(bio) > Config.MAX_BIO_LEN:
        return jsonify({"error": f"Bio cannot exceed {Config.MAX_BIO_LEN} characters."}), 400

    avatar_path = None
    avatar_file = request.files.get("avatar")
    if avatar_file:
        if avatar_file.content_type not in Config.ALLOWED_IMAGE_TYPES:
            return jsonify({"error": "Unsupported avatar image type."}), 415
        avatar_path = save_avatar(avatar_file)

    update_user_profile(
        g.user["id"],
        display_name=display_name,
        bio=bio if bio else None,
        avatar_path=avatar_path,
    )
    return jsonify({"message": "Profile updated successfully."}), 200


@user_bp.route("/<username>/follow", methods=["POST"])
@require_auth
def follow(username):
    """POST /api/users/<username>/follow — toggle follow/unfollow."""
    user = get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found."}), 404
    try:
        result = toggle_follow(g.user["id"], user["id"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    count = get_follower_count(user["id"])
    return jsonify({
        "following":       result["following"],
        "followers_count": count,
    }), 200


@user_bp.route("/<username>/followers", methods=["GET"])
@require_auth
def followers(username):
    """GET /api/users/<username>/followers — list of users following this user."""
    user = get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found."}), 404
    rows = get_followers(user["id"])
    return jsonify([serialize_mini_user(r) for r in rows]), 200


@user_bp.route("/<username>/following", methods=["GET"])
@require_auth
def following(username):
    """GET /api/users/<username>/following — list of users this user follows."""
    user = get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found."}), 404
    rows = get_following(user["id"])
    return jsonify([serialize_mini_user(r) for r in rows]), 200


@user_bp.route("/<username>/avatar", methods=["GET"])
def serve_avatar(username):
    """GET /api/users/<username>/avatar — stream the user's avatar image (public)."""
    user = get_user_by_username(username)
    if not user or not user["avatar_path"]:
        return jsonify({"error": "Avatar not found."}), 404
    path = os.path.join(Config.AVATAR_DIR, user["avatar_path"])
    if not os.path.exists(path):
        return jsonify({"error": "Avatar file not found on server."}), 500
    return send_file(path, mimetype="image/jpeg")
