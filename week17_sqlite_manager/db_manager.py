import sqlite3
import os

class DatabaseManager:
    db_name = "project52.db" 
    
    def __init__(self, db_name = db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
    
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            print(f"Successfully connected to {self.db_name}")
            
        except sqlite3.Error as e:
            print(f"Connection Error: {e}")
    
    def disconnect(self):
        pass
    
    def execute_write(self):
        pass
    
    def execute_read(self):
        pass