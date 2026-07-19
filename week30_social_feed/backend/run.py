from app import create_app

app = create_app()

if __name__ == "__main__":
    # Development server — hot-reload enabled via debug=True in Config
    app.run(host="0.0.0.0", port=5000)
