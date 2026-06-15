import os 
import uuid
from flask import Blueprint, request, jsonify, current_app #type: ignore
from werkzeug.utils import secure_filename #type: ignore
from app.services import recipe_service
from app.models import recipe_model

recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/api/recipes', methods=['POST'])
def create_recipe():
    raw_data = {
        'title': request.form.get('title', ''),
        'description': request.form.get('description', ''),
        'ingredients': request.form.get('ingredients', ''),
        'instructions': request.form.get('instructions', ''),
    }
    
    try:
        clean_data = recipe_service.validate_recipe_data(raw_data)
    
    except recipe_service.ValidationError as e:
        return jsonify({'error':  str(e)}), 400
    
    image_filename = None
    if 'image' in request.files:
        file = request.files['image']
        
        if file.filename != '':
            if not recipe_service.allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, and WEBP are allowed.'}), 400
            
            safe_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(upload_path)
            image_filename = unique_filename

    try:
        new_recipe = recipe_model.insert_recipe(
            title=clean_data['title'],
            description = clean_data['description'],
            ingredients = clean_data['ingredients'],
            instructions = clean_data['instructions'],
            image_filename = image_filename # type: ignore
        )
        return jsonify(new_recipe), 201
    except Exception as e:
        return jsonify({'error': 'Database error occurred.'}), 500