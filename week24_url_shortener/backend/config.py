import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is not set. Check your .env file.")

    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
