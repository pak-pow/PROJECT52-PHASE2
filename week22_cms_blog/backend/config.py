from dotenv import load_dotenv #type: ignore
import os 

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-p52-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'my-super-secret-production-key-123'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASE_DIR, 'data', 'database.db')