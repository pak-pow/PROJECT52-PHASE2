"""Image processing service — resizes and stores uploaded avatar and post images."""
import os
import uuid
from app.config.settings import Config

try:
    from PIL import Image  # type: ignore
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


def save_avatar(file_obj):
    """Resize avatar to square thumbnail and save as JPEG. Returns stored filename."""
    filename = f"{uuid.uuid4().hex}.jpg"
    dest = os.path.join(Config.AVATAR_DIR, filename)
    os.makedirs(Config.AVATAR_DIR, exist_ok=True)

    if PILLOW_AVAILABLE:
        img = Image.open(file_obj).convert("RGB")
        # Centre-crop to square before resize
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize(Config.AVATAR_SIZE, Image.LANCZOS)
        img.save(dest, "JPEG", quality=Config.IMAGE_QUALITY, optimize=True)
    else:
        # Fallback — save raw if Pillow is not installed
        file_obj.save(dest)

    return filename


def save_post_image(file_obj):
    """Resize post image (preserving aspect ratio) and save as JPEG. Returns stored filename."""
    filename = f"{uuid.uuid4().hex}.jpg"
    dest = os.path.join(Config.POST_IMAGE_DIR, filename)
    os.makedirs(Config.POST_IMAGE_DIR, exist_ok=True)

    if PILLOW_AVAILABLE:
        img = Image.open(file_obj).convert("RGB")
        img.thumbnail(Config.POST_IMAGE_MAX_SIZE, Image.LANCZOS)
        img.save(dest, "JPEG", quality=Config.IMAGE_QUALITY, optimize=True)
    else:
        file_obj.save(dest)

    return filename


def delete_image(directory, filename):
    """Safely delete an image file from disk. Silently ignores missing files."""
    if not filename:
        return
    path = os.path.join(directory, filename)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
