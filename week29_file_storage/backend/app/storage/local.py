import os
from app.storage.base import BaseStorage
from app.config.settings import Config


class LocalStorage(BaseStorage):
    """Store files on the local filesystem under UPLOAD_DIR."""

    def __init__(self, upload_dir=None):
        self.upload_dir = upload_dir or Config.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def save(self, file_obj, stored_name):
        """Save a Werkzeug FileStorage object to disk. Returns the full path."""
        dest = os.path.join(self.upload_dir, stored_name)
        file_obj.save(dest)
        return dest

    def delete(self, stored_name):
        """Delete the file from disk if it exists."""
        path = os.path.join(self.upload_dir, stored_name)
        if os.path.isfile(path):
            os.remove(path)

    def get_path(self, stored_name):
        """Return the absolute path to the file, or None if missing."""
        path = os.path.join(self.upload_dir, stored_name)
        return path if os.path.isfile(path) else None
