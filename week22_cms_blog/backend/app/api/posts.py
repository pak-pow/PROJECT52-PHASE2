from flask import Blueprint, jsonify, request #type: ignore
from app.models import Post

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/', methods=['GET'])
def get_posts():
    
    raw_posts = Post.get_all()
    
    posts_list = []
    for post in raw_posts:
        posts_list.append({
            "id": post['id'],
            "title": post['title'],
            "content": post['content'],
            "author_id": post['author_id'],
            "created_at": post['created_at']
        })
        
    return jsonify(posts_list), 200

@posts_bp.route('/', methods=['POST'])
def create_post():
    
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('content') or not data.get('author_id'):
        return jsonify({"error": "Missing required fields: title, content, author_id"}), 400

    new_post_id = Post.create(
        title=data['title'],
        content=data['content'],
        author_id=data['author_id']
    )

    return jsonify({
        "message": "Post created successfully!",
        "post_id": new_post_id
    }), 201

@posts_bp.route('/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    
    post = Post.get_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({"error": "Missing required fields: title, content"}), 400
    
    Post.update(post_id, data['title'], data['content'])
    return jsonify({"message": f"Post {post_id} updated successfully!"}), 200

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
        
    Post.delete(post_id)
    return jsonify({"message": f"Post {post_id} deleted successfully!"}), 200