import os

try:
    from PIL import Image  # type: ignore
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

from app.config.settings import Config


def can_generate_thumbnail(mime_type):
    """Return True if the file type supports thumbnail generation."""
    return PILLOW_AVAILABLE and mime_type in (
        "image/jpeg", "image/png", "image/gif", "image/webp"
    )


def generate_thumbnail(source_path, stored_name):
    """
    Generate a thumbnail for an image file.
    Saves to THUMBNAIL_DIR/<stored_name>.
    Returns True on success, False on failure.
    """
    if not PILLOW_AVAILABLE:
        return False

    try:
        os.makedirs(Config.THUMBNAIL_DIR, exist_ok=True)
        thumb_path = os.path.join(Config.THUMBNAIL_DIR, stored_name)

        with Image.open(source_path) as img:
            img.thumbnail(Config.THUMBNAIL_SIZE)
            # Convert RGBA to RGB for JPEG thumbnails
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(thumb_path, "JPEG", quality=85)

        return True
    except Exception:
        return False


def get_thumbnail_path(stored_name):
    """Return the absolute path to a thumbnail, or None if missing."""
    path = os.path.join(Config.THUMBNAIL_DIR, stored_name)
    return path if os.path.isfile(path) else None


def delete_thumbnail(stored_name):
    """Delete a thumbnail file if it exists."""
    path = os.path.join(Config.THUMBNAIL_DIR, stored_name)
    if os.path.isfile(path):
        os.remove(path)
