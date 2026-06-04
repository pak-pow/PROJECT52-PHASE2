from werkzeug.security import check_password_hash, generate_password_hash #type: ignore
from flask_jwt_extended import create_access_token #type: ignore
from app.models.user import User

class AuthService:
    @staticmethod
    def login_user(username, password):
        """Verifies credentials and generates a JWT if valid."""
        user = User.get_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            return create_access_token(identity=str(user['id']))
        return None

    @staticmethod
    def register_user(username, password):
        """Validates rules, hashes the password, and creates a new user."""
        clean_username = username.strip()
        import re
        if len(clean_username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if len(clean_username) > 32:
            raise ValueError("Username must be at most 32 characters long.")
        if not re.match(r'^[a-zA-Z0-9_.\-]+$', clean_username):
            raise ValueError("Username may only contain letters, numbers, underscores, dots, and hyphens.")
            
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        hashed_pw = generate_password_hash(password)
        user_id = User.create(clean_username, hashed_pw)
        return user_id