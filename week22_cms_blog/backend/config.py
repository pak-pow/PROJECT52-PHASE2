from dotenv import load_dotenv() #type: ignore
import os 

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-p52-key'
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')