from flask import Blueprint, jsonify #type: ignore
from app.models.post import Post

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/', methods=['GET'])
def get_posts():
    pass