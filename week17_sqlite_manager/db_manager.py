import sqlite3
import os

class DatabaseManager:
    db_name = "project52.db" 
    
    def __init__(self, db_name = db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
    
    def connect(self):
        pass
    
    def disconnect(self):
        pass
    
    def execute_write(self):
        pass
    
    def execute_read(self):
        pass