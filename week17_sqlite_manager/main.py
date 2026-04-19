from db_manager import DatabaseManager

def run_tests():
    # 1. Initialize our custom manager
    db = DatabaseManager("test_database.db")

    # 2. CREATE (Initialize a table)
    print("\n--- CREATING TABLE ---")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1
    );
    """
    db.execute_write(create_table_query)

    # 3. INSERT (Create records)
    print("\n--- INSERTING DATA ---")
    insert_query = "INSERT INTO users (username, role) VALUES (?, ?)"
    # Using parameterized queries (?, ?) prevents SQL Injection hacks!
    db.execute_write(insert_query, ("admin", "admin"))
    db.execute_write(insert_query, ("test_user", "subscriber"))

    # 4. READ (Select records)
    print("\n--- READING DATA ---")
    select_query = "SELECT * FROM users"
    users = db.execute_read(select_query)
    for user in users:
        print(user)

    # 5. UPDATE (Modify a record)
    print("\n--- UPDATING DATA ---")
    update_query = "UPDATE users SET role = ? WHERE username = ?"
    db.execute_write(update_query, ("super_admin", "admin_paul"))

    # 6. DELETE (Remove a record)
    print("\n--- DELETING DATA ---")
    delete_query = "DELETE FROM users WHERE username = ?"
    db.execute_write(delete_query, ("test_user",))

    # 7. FINAL READ (Verify changes)
    print("\n--- FINAL DATABASE STATE ---")
    final_users = db.execute_read(select_query)
    for user in final_users:
        print(user)

if __name__ == "__main__":
    run_tests()