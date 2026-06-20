import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",   # Vite dev server
    "http://localhost:5173",
    "http://127.0.0.1:5500",   # VS Code Live Server
    "http://localhost:5500",
    "null",                     # file:// direct browser open
]