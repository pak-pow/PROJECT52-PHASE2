import sqlite3
import os
from flask import g #type: ignore

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))