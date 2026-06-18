import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory  # type: ignore
from werkzeug.utils import secure_filename  # type: ignore
from app.services import recipe_service
from app.models import recipe_model

recipe_bp = Blueprint('recipe', __name__)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _save_image(file) -> str:
    """Validates, secures, and saves an uploaded image. Returns the saved filename."""
    if not recipe_service.allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        raise ValueError('Invalid file type. Only PNG, JPG, JPEG, and WEBP are allowed.')
    safe_filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(upload_path)
    return unique_filename


def _delete_image_file(image_filename: str):
    """Removes an image file from disk if it exists."""
    if image_filename:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)


# ---------------------------------------------------------------------------
# POST /api/recipes  — Create
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/recipes', methods=['POST'])
def create_recipe():
    raw_data = {
        'title':        request.form.get('title', ''),
        'description':  request.form.get('description', ''),
        'ingredients':  request.form.get('ingredients', ''),
        'instructions': request.form.get('instructions', ''),
    }

    try:
        clean_data = recipe_service.validate_recipe_data(raw_data)
    except recipe_service.ValidationError as e:
        return jsonify({'error': str(e)}), 400

    image_filename = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            try:
                image_filename = _save_image(file)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

    try:
        new_recipe = recipe_model.insert_recipe(
            title=clean_data['title'],
            description=clean_data['description'],
            ingredients=clean_data['ingredients'],
            instructions=clean_data['instructions'],
            image_filename=image_filename
        )
        return jsonify(new_recipe), 201
    except Exception:
        return jsonify({'error': 'Database error occurred.'}), 500


# ---------------------------------------------------------------------------
# GET /api/recipes  — List (paginated)
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/recipes', methods=['GET'])
def list_recipes():
    try:
        page     = max(request.args.get('page', 1, type=int), 1)
        per_page = min(request.args.get('per_page', 12, type=int), 100)
        offset   = (page - 1) * per_page

        recipes = recipe_model.get_recipes_paginated(limit=per_page, offset=offset)
        total   = recipe_model.get_recipe_count()
        pages   = max(1, -(-total // per_page))  # ceiling division

        return jsonify({
            'recipes':  recipes,
            'total':    total,
            'page':     page,
            'per_page': per_page,
            'pages':    pages,
        }), 200
    except Exception:
        return jsonify({'error': 'Failed to fetch recipes from the database.'}), 500


# ---------------------------------------------------------------------------
# GET /api/recipes/<id>  — Single
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_single_recipe(recipe_id):
    recipe = recipe_model.get_recipe_by_id(recipe_id)
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    return jsonify(recipe), 200


# ---------------------------------------------------------------------------
# PUT /api/recipes/<id>  — Update
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    recipe = recipe_model.get_recipe_by_id(recipe_id)
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404

    raw_data = {
        'title':        request.form.get('title', ''),
        'description':  request.form.get('description', ''),
        'ingredients':  request.form.get('ingredients', ''),
        'instructions': request.form.get('instructions', ''),
    }

    try:
        clean_data = recipe_service.validate_recipe_data(raw_data)
    except recipe_service.ValidationError as e:
        return jsonify({'error': str(e)}), 400

    # Handle optional new image upload
    new_image_filename = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            try:
                new_image_filename = _save_image(file)
                # Remove old image if a new one was uploaded
                _delete_image_file(recipe.get('image_filename'))
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

    try:
        updated = recipe_model.update_recipe(
            recipe_id=recipe_id,
            title=clean_data['title'],
            description=clean_data['description'],
            ingredients=clean_data['ingredients'],
            instructions=clean_data['instructions'],
            image_filename=new_image_filename,
        )
        return jsonify(updated), 200
    except Exception:
        return jsonify({'error': 'Database error occurred.'}), 500


# ---------------------------------------------------------------------------
# DELETE /api/recipes/<id>  — Delete
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    recipe = recipe_model.get_recipe_by_id(recipe_id)
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404

    _delete_image_file(recipe.get('image_filename'))

    success = recipe_model.delete_recipe(recipe_id)
    if success:
        return jsonify({'message': 'Recipe deleted successfully'}), 200
    return jsonify({'error': 'Failed to delete from database'}), 500


# ---------------------------------------------------------------------------
# GET /uploads/<filename>  — Serve uploaded images
# ---------------------------------------------------------------------------

@recipe_bp.route('/uploads/<filename>', methods=['GET'])
def get_uploaded_image(filename):
    """Safely streams an image from the server's upload directory to the browser."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)