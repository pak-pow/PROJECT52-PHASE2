from flask import Blueprint, request, jsonify, redirect  # type: ignore
from app.services import url_service
from app.services.url_service import AliasTakenError, ExpiredURLError
from app import limiter
from config import Config

url_bp = Blueprint('url', __name__)


# ---------------------------------------------------------------------------
# POST /api/shorten
# Accepts a long URL and returns a short code.
# ---------------------------------------------------------------------------
@url_bp.route('/api/shorten', methods=['POST'])
@limiter.limit("5 per minute")
def shorten():
    data = request.get_json(silent=True)
    if not data or 'url' not in data:
        return jsonify({'error': 'Request body must include a "url" field.'}), 400

    custom_alias = data.get('custom_alias')
    expires_in_hours = data.get('expires_in_hours')

    try:
        record = url_service.shorten_url(data['url'], custom_alias, expires_in_hours)

        # FIX: Build the short_url from a hardcoded base URL (Config.BASE_URL)
        # instead of request.host_url to prevent Host Header Injection attacks.
        base_url = Config.BASE_URL.rstrip('/')
        return jsonify({
            'short_code':   record['short_code'],
            'short_url':    f"{base_url}/{record['short_code']}",
            'original_url': record['original_url'],
            'clicks':       record['clicks'],
            'created_at':   record['created_at'],
            'expires_at':   record.get('expires_at'),
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400      # Bad request (invalid url/alias/type)
    except AliasTakenError as e:
        return jsonify({'error': str(e)}), 409      # Conflict (alias already taken)


# ---------------------------------------------------------------------------
# GET /<short_code>
# Redirects the browser to the original URL (302 Temporary Redirect).
# Using 302 so browsers don't cache it, allowing expiry/deletion to work.
# ---------------------------------------------------------------------------
@url_bp.route('/<string:short_code>', methods=['GET'])
@limiter.limit("60 per minute")
def redirect_to_url(short_code):
    if len(short_code) > 20 or not all(c.isalnum() or c == '-' for c in short_code):
        return jsonify({'error': 'Invalid short code.'}), 400

    try:
        record = url_service.resolve_url(short_code)
        return redirect(record['original_url'], code=302)
    except KeyError:
        return jsonify({'error': f"Short code '{short_code}' not found."}), 404
    except ExpiredURLError as e:
        return jsonify({'error': str(e)}), 410


# ---------------------------------------------------------------------------
# GET /api/stats
# Returns analytics (click counts) for all shortened URLs.
# FIX: original_url is intentionally excluded at the model layer to prevent
# unauthenticated enumeration of all URLs in the database.
# ---------------------------------------------------------------------------
@url_bp.route('/api/stats', methods=['GET'])
@limiter.limit("10 per minute")
def stats():
    records = url_service.get_stats()
    return jsonify(records), 200