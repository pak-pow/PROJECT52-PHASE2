import os 
from dotenv import load_dotenv #type: ignore

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-week23'
    JWS_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret-jwt-key-week23'
    DATABASE = os.path.join(BASE_DIR, 'data', 'database.db')