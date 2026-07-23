import os
from flask import Blueprint, request, jsonify, g, send_file
from app.services.auth_service import require_auth
from app.services.serializers import serialize_post
from app.services.image_service import save_post_image
from app.models.post_model import (
    create_post, get_post_by_id, get_home_feed,
    get_explore_feed, delete_post, get_replies_to,
    toggle_repost, has_reposted, get_reposted_post_ids,
)
from app.models.like_model import toggle_like, get_liked_post_ids
from app.config.settings import Config

post_bp = Blueprint("posts", __name__, url_prefix="/api/posts")


@post_bp.route("", methods=["GET"])
@require_auth
def home_feed():
    """GET /api/posts — paginated home feed (own + following posts)."""
    before_id = request.args.get("before", type=int)
    rows = get_home_feed(g.user["id"], Config.FEED_PAGE_SIZE, before_id)
    post_ids = [r["id"] for r in rows]
    liked    = get_liked_post_ids(g.user["id"], post_ids)
    reposted = get_reposted_post_ids(g.user["id"], post_ids)
    return jsonify([serialize_post(r, liked, reposted) for r in rows]), 200


@post_bp.route("/explore", methods=["GET"])
@require_auth
def explore():
    """GET /api/posts/explore — trending global feed sorted by likes.
    Optional ?tag=<hashtag> to filter by hashtag.
    """
    before_id = request.args.get("before", type=int)
    tag = request.args.get("tag", "").strip() or None
    rows = get_explore_feed(Config.EXPLORE_PAGE_SIZE, before_id, tag)
    post_ids = [r["id"] for r in rows]
    liked    = get_liked_post_ids(g.user["id"], post_ids)
    reposted = get_reposted_post_ids(g.user["id"], post_ids)
    return jsonify([serialize_post(r, liked, reposted) for r in rows]), 200


@post_bp.route("", methods=["POST"])
@require_auth
def create():
    """POST /api/posts — create a new post (multipart: content + optional image)."""
    content = request.form.get("content", "").strip()
    reply_to_id = request.form.get("reply_to_id", type=int)
    repost_of_id = request.form.get("repost_of_id", type=int)
    img_file = request.files.get("image")

    if not content and not img_file:
        return jsonify({"error": "A post must have text content or an image."}), 400
    if len(content) > Config.MAX_POST_LEN:
        return jsonify({"error": f"Post cannot exceed {Config.MAX_POST_LEN} characters."}), 400
    if img_file and img_file.content_type not in Config.ALLOWED_IMAGE_TYPES:
        return jsonify({"error": "Unsupported image type. Allowed: JPEG, PNG, GIF, WebP."}), 415

    image_path = None
    if img_file:
        image_path = save_post_image(img_file)

    post_id = create_post(g.user["id"], content, image_path, reply_to_id, repost_of_id)
    row = get_post_by_id(post_id)
    return jsonify(serialize_post(row, liked_ids=set())), 201


@post_bp.route("/<int:post_id>", methods=["GET"])
@require_auth
def get_single(post_id):
    """GET /api/posts/<id> — single post with its replies."""
    row = get_post_by_id(post_id)
    if not row:
        return jsonify({"error": "Post not found."}), 404
    replies = get_replies_to(post_id)
    all_ids  = [post_id] + [r["id"] for r in replies]
    liked    = get_liked_post_ids(g.user["id"], all_ids)
    reposted = get_reposted_post_ids(g.user["id"], all_ids)
    return jsonify({
        "post":    serialize_post(row, liked, reposted),
        "replies": [serialize_post(r, liked, reposted) for r in replies],
    }), 200


@post_bp.route("/<int:post_id>", methods=["DELETE"])
@require_auth
def remove(post_id):
    """DELETE /api/posts/<id> — delete own post."""
    deleted = delete_post(post_id, g.user["id"])
    if not deleted:
        return jsonify({"error": "Post not found or you are not the author."}), 404
    return jsonify({"message": "Post deleted."}), 200


@post_bp.route("/<int:post_id>/like", methods=["POST"])
@require_auth
def like(post_id):
    """POST /api/posts/<id>/like — toggle like on/off."""
    if not get_post_by_id(post_id):
        return jsonify({"error": "Post not found."}), 404
    result = toggle_like(g.user["id"], post_id)
    return jsonify(result), 200


@post_bp.route("/<int:post_id>/image", methods=["GET"])
def serve_image(post_id):
    """GET /api/posts/<id>/image — stream the post image file (public)."""
    row = get_post_by_id(post_id)
    if not row or not row["image_path"]:
        return jsonify({"error": "Image not found."}), 404
    path = os.path.join(Config.POST_IMAGE_DIR, row["image_path"])
    if not os.path.exists(path):
        return jsonify({"error": "Image file not found on server."}), 500
    return send_file(path, mimetype="image/jpeg")


@post_bp.route("/<int:post_id>/repost", methods=["POST"])
@require_auth
def repost(post_id):
    """POST /api/posts/<id>/repost — toggle repost on/off."""
    original = get_post_by_id(post_id)
    if not original:
        return jsonify({"error": "Post not found."}), 404
    if original["user_id"] == g.user["id"]:
        return jsonify({"error": "You cannot repost your own post."}), 400
    result = toggle_repost(g.user["id"], post_id)
    return jsonify(result), 200
