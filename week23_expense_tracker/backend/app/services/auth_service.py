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
        """Hashes the password and creates a new user."""
        hashed_pw = generate_password_hash(password)
        user_id = User.create(username, hashed_pw)
        return user_id