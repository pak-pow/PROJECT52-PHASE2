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
        if self.connection:
            self.connection.close()
            print("Database Connection Closed")
    
    def execute_write(self, query, params=()):
        try:
            self.connect()
            self.cursor.execute(query, params) # type: ignore
            self.connection.commit() # type: ignore
            print("Write operation successful.")
            return True
        
        except sqlite3.Error as e:
            print(f"Write Error: {e}")
            return False
        
        finally:
            self.disconnect()
        
    
    def execute_read(self, query, params=()):
        try:
            self.connect()
            self.cursor.execute(query, params) # type: ignore
            results = [dict(row) for row in self.cursor.fetchall()] # type: ignore
            return results
        
        except sqlite3.Error as e:
            print(f"❌ Read Error: {e}")
            return []
        
        finally:
            self.disconnect()