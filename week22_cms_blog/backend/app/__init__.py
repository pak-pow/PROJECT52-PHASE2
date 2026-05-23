from flask import Flask #type:ignore
from .extensions.db import close_db, init_db

def create_app():
    pass