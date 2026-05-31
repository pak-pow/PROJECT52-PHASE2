import os 
from dotenv import load_dotenv #type: ignore

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config: 
    pass