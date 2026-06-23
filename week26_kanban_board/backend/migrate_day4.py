import sqlite3
import os

def migrate():
    # Find database path relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'data', 'kanban.db')
    
    if not os.path.exists(db_path):
        print(f"No database found at {db_path}. No migration needed.")
        return

    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if position column already exists
        cursor.execute("PRAGMA table_info(boards)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'position' in columns:
            print("Migration already applied. 'position' column exists in 'boards' table.")
            return
            
        print("Adding 'position' column to 'boards' table...")
        cursor.execute("ALTER TABLE boards ADD COLUMN position INTEGER DEFAULT 0")
        
        # Populate initial positions sequentially based on ID
        cursor.execute("SELECT id FROM boards ORDER BY id ASC")
        boards = cursor.fetchall()
        
        for idx, (board_id,) in enumerate(boards):
            cursor.execute("UPDATE boards SET position = ? WHERE id = ?", (idx, board_id))
            
        conn.commit()
        print(f"Migration completed successfully! Migrated {len(boards)} boards.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
