import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory, current_app  # type: ignore
from werkzeug.utils import secure_filename  # type: ignore

from app.models.recipe_model import (
    insert_recipe,
    get_recipe_by_id,
    get_recipes_paginated,
    get_recipe_count,
    get_all_categories,
    update_recipe,
    delete_recipe,
)
from app.services.recipe_service import validate_recipe_data, allowed_file
from app.config.settings import DEFAULT_PER_PAGE, MAX_PER_PAGE, CATEGORIES

recipe_bp = Blueprint('recipes', __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save_image(file_storage) -> str:
    """Validates and saves an uploaded image. Returns the saved filename."""
    if not allowed_file(file_storage.filename, current_app.config['ALLOWED_EXTENSIONS']):
        raise ValueError("Invalid file type. Allowed: png, jpg, jpeg, webp")
    ext      = file_storage.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return filename


def _delete_image(filename: str):
    """Removes an image file from disk if it exists."""
    if filename:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(path):
            os.remove(path)


# ---------------------------------------------------------------------------
# GET /api/recipes   — paginated list with optional ?category= and ?search=
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/recipes', methods=['GET'])
def list_recipes():
    try:
        page     = max(1, int(request.args.get('page', 1)))
        per_page = min(int(request.args.get('per_page', DEFAULT_PER_PAGE)), MAX_PER_PAGE)
        category = request.args.get('category', '').strip() or None
        search   = request.args.get('search', '').strip() or None

        offset   = (page - 1) * per_page
        total    = get_recipe_count(category=category, search=search)
        recipes  = get_recipes_paginated(per_page, offset, category=category, search=search)

        return jsonify({
            'recipes': recipes,
            'total':   total,
            'page':    page,
            'per_page': per_page,
            'pages':   max(1, -(-total // per_page)),  # ceiling division
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# GET /api/categories  — list of distinct categories that have recipes
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/categories', methods=['GET'])
def list_categories():
    try:
        categories = get_all_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# POST /api/recipes  — create
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/recipes', methods=['POST'])
def create_recipe():
    data = {
        'title':        request.form.get('title', '').strip(),
        'description':  request.form.get('description', '').strip(),
        'ingredients':  request.form.get('ingredients', '').strip(),
        'instructions': request.form.get('instructions', '').strip(),
    }
    category = request.form.get('category', 'Uncategorised').strip()

    try:
        validate_recipe_data(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    image_filename = None
    if 'image' in request.files and request.files['image'].filename:
        try:
            image_filename = _save_image(request.files['image'])
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    recipe = insert_recipe(**data, image_filename=image_filename, category=category)
    return jsonify(recipe), 201


# ---------------------------------------------------------------------------
# GET /api/recipes/<id>  — single recipe
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id: int):
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    return jsonify(recipe)


# ---------------------------------------------------------------------------
# PUT /api/recipes/<id>  — update
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
def edit_recipe(recipe_id: int):
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404

    data = {
        'title':        request.form.get('title', '').strip(),
        'description':  request.form.get('description', '').strip(),
        'ingredients':  request.form.get('ingredients', '').strip(),
        'instructions': request.form.get('instructions', '').strip(),
    }
    category = request.form.get('category', None)

    try:
        validate_recipe_data(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    image_filename = None
    if 'image' in request.files and request.files['image'].filename:
        try:
            image_filename = _save_image(request.files['image'])
            _delete_image(recipe.get('image_filename'))
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    updated = update_recipe(recipe_id, **data, image_filename=image_filename, category=category)
    return jsonify(updated)


# ---------------------------------------------------------------------------
# DELETE /api/recipes/<id>  — delete
# ---------------------------------------------------------------------------

@recipe_bp.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def remove_recipe(recipe_id: int):
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404

    _delete_image(recipe.get('image_filename'))
    delete_recipe(recipe_id)
    return jsonify({'message': 'Recipe deleted successfully'}), 200


# ---------------------------------------------------------------------------
# GET /uploads/<filename>  — serve uploaded images
# ---------------------------------------------------------------------------

@recipe_bp.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename: str):
    safe_name = secure_filename(filename)
    upload_dir = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(os.path.join(upload_dir, safe_name)):
        return jsonify({'error': 'Image not found'}), 404
    return send_from_directory(upload_dir, safe_name)