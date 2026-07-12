from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """Abstract storage interface — swap in S3, GCS, etc. later."""

    @abstractmethod
    def save(self, file_obj, stored_name):
        """Persist a file and return the full path."""

    @abstractmethod
    def delete(self, stored_name):
        """Remove a file by stored name."""

    @abstractmethod
    def get_path(self, stored_name):
        """Return the absolute path to a stored file."""
