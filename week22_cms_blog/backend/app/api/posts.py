from flask import Blueprint, jsonify #type: ignore
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
    pass