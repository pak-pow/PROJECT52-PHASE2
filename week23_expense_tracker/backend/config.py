import os
from dotenv import load_dotenv  # type: ignore
from datetime import timedelta

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _require_env(name: str) -> str:
    """Raise at startup if a required environment variable is missing."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not set. "
            f"Copy .env.example to .env and fill in the values."
        )
    return value


class Config:
    SECRET_KEY = _require_env('SECRET_KEY')
    JWT_SECRET_KEY = _require_env('JWT_SECRET_KEY')  # fixed: was JWS_ (typo)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)    # explicit — do not rely on library defaults
    DATABASE = os.path.join(BASE_DIR, 'data', 'database.db')