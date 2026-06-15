import os 
import uuid
from flask import Blueprint, request, jsonify, current_app #type: ignore
from werkzeug.utils import secure_filename #type: ignore
from app.services import recipe_service
from app.models import recipe_model

recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/api/recipes', methods=['POST'])
def create_recipe():
    pass