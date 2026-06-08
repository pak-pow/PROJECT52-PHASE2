from flask import Blueprint, request, jsonify, redirect #type: ignore
from app.services import url_service

url_bp = Blueprint('url', __name__)


# ---------------------------------------------------------------------------
# POST /api/shorten
# Accepts a long URL and returns a short code.
# ---------------------------------------------------------------------------
@url_bp.route('/api/shorten', methods=['POST'])
def shorten():
    data = request.get_json(silent=True)
    if not data or 'url' not in data:
        return jsonify({'error': 'Request body must include a "url" field.'}), 400

    custom_alias = data.get('custom_alias') # Grab it if it exists, otherwise it's None

    try:
        record = url_service.shorten_url(data['url'], custom_alias)
        return jsonify({
            'short_code': record['short_code'],
            'short_url':  f"{request.host_url}{record['short_code']}",
            'original_url': record['original_url'],
            'clicks':     record['clicks'],
            'created_at': record['created_at'],
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 # Bad request (invalid url/alias format)
    except KeyError as e:
        return jsonify({'error': str(e)}), 409 # Conflict (Alias taken)


# ---------------------------------------------------------------------------
# GET /<short_code>
# Redirects the browser to the original URL (301 Permanent Redirect).
# ---------------------------------------------------------------------------
@url_bp.route('/<string:short_code>', methods=['GET'])
def redirect_to_url(short_code):
    # Guard: don't swallow routes that are clearly not short codes
    if len(short_code) > 20 or not all(c.isalnum() or c == '-' for c in short_code):
        return jsonify({'error': 'Invalid short code.'}), 400

    try:
        record = url_service.resolve_url(short_code)
        return redirect(record['original_url'], code=301)
    except KeyError:
        return jsonify({'error': f"Short code '{short_code}' not found."}), 404


# ---------------------------------------------------------------------------
# GET /api/stats
# Returns all shortened URLs and their click counts.
# ---------------------------------------------------------------------------
@url_bp.route('/api/stats', methods=['GET'])
def stats():
    records = url_service.get_stats()
    return jsonify(records), 200
