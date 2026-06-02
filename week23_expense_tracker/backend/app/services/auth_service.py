from werkzeug.security import check_password_hash #type: ignore
from flask_jwt_extended import create_access_token #type: ignore
from app.models.user import User

class AuthService:
    @staticmethod
    def login_user(username, password):
        """Verifies credentials and generates a JWT if valid."""
        user = User.get_by_username(username)
        
        if user and check_password_hash(user['password_hash'], password):
            token = create_access_token(identity=str(user['id']))
            return token
            
        return None 