"""Production WSGI entrypoint (Waitress)."""
from waitress import serve  # type: ignore
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("Serving on http://0.0.0.0:5000 (Waitress)")
    serve(app, host="0.0.0.0", port=5000)
