from flask import Blueprint, jsonify, request #type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity #type: ignore
from app.models.post import Post

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/', methods=['GET'])
def get_posts():
    status_filter = request.args.get('status')
    
    raw_posts = Post.get_all(status_filter=status_filter)
    posts_list = []
    for post in raw_posts:
        posts_list.append({
            "id": post['id'],
            "title": post['title'],
            "content": post['content'],
            "author_id": post['author_id'],
            "status": post['status'],
            "created_at": post['created_at']
        })
    return jsonify(posts_list), 200

@posts_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({"error": "Missing required fields"}), 400

    current_user_id = get_jwt_identity()
    post_status = data.get('status', 'draft') 

    new_post_id = Post.create(
        title=data['title'],
        content=data['content'],
        author_id=current_user_id,
        status=post_status
    )

    return jsonify({"message": "Post created successfully!", "post_id": new_post_id}), 201

@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    data = request.get_json()
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({"error": "Post not found"}), 404
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({"error": "Missing required fields"}), 400
    
    post_status = data.get('status', post['status'])
    
    Post.update(post_id, data['title'], data['content'], post_status)
    return jsonify({"message": f"Post {post_id} updated successfully!"}), 200

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post = Post.get_by_id(post_id)
    
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    Post.delete(post_id)
    return jsonify({"message": "Deleted successfully!"}), 200