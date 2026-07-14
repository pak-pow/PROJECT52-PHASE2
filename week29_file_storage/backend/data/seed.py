import os
import sys
import shutil

# Ensure path is correct to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.db import init_db
from app.models.user_model import create_user
from app.models.file_model import insert_file
from app.config.settings import Config
from app.services.thumbnail_service import generate_thumbnail

try:
    from PIL import Image  # type: ignore
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


def seed():
    print("Initializing database...")
    init_db()

    print("Re-creating directories...")
    # Wipe old directories to ensure clean states
    if os.path.exists(Config.UPLOAD_DIR):
        shutil.rmtree(Config.UPLOAD_DIR)
    if os.path.exists(Config.THUMBNAIL_DIR):
        shutil.rmtree(Config.THUMBNAIL_DIR)

    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(Config.THUMBNAIL_DIR, exist_ok=True)

    print("Seeding default user: demo_user / password123")
    user_id = create_user("demo_user", "password123")

    # Configure mock files
    files_to_seed = [
        {
            "original_name": "welcome_poster.png",
            "stored_name": "welcome_poster.png",
            "mime_type": "image/png",
            "category": "image",
            "content": None,
        },
        {
            "original_name": "project_notes.txt",
            "stored_name": "project_notes.txt",
            "mime_type": "text/plain",
            "category": "document",
            "content": b"Welcome to FileVault!\nThis is a simple text file seeded to show list/grid layouts."
        },
        {
            "original_name": "lofi_beat.mp3",
            "stored_name": "lofi_beat.mp3",
            "mime_type": "audio/mpeg",
            "category": "audio",
            "content": b"MOCK MP3 CONTENT"
        }
    ]

    for f in files_to_seed:
        dest_path = os.path.join(Config.UPLOAD_DIR, f["stored_name"])

        if f["mime_type"] == "image/png":
            if PILLOW_AVAILABLE:
                # Generate a premium gradient/indigo image
                img = Image.new("RGB", (600, 400), color=(99, 102, 241))
                img.save(dest_path, format="PNG")
            else:
                # Fallback text file
                with open(dest_path, "wb") as fh:
                    fh.write(b"MOCK IMAGE")
        else:
            with open(dest_path, "wb") as fh:
                fh.write(f["content"])

        file_size = os.path.getsize(dest_path)

        # Generate thumbnail for the image
        has_thumb = False
        if f["category"] == "image" and PILLOW_AVAILABLE:
            has_thumb = generate_thumbnail(dest_path, f["stored_name"])

        insert_file(
            user_id=user_id,
            original_name=f["original_name"],
            stored_name=f["stored_name"],
            mime_type=f["mime_type"],
            file_size=file_size,
            category=f["category"],
            has_thumbnail=has_thumb
        )
        print(f"Seeded file: {f['original_name']} (Thumbnail: {has_thumb})")

    print("Seeding complete successfully!")


if __name__ == "__main__":
    seed()
