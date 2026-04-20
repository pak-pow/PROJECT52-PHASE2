from db_manager import DatabaseManager
import sys

def print_menu():
    """Displays the main CLI menu."""
    print("\n" + "="*35)
    print(" SQLITE MANAGER ")
    print("="*35)
    print("1. 👥 View All Users")
    print("2. ➕ Add New User")
    print("3. ✏️ Update User Role")
    print("4. ❌ Delete User")
    print("5. 🚪 Exit")
    print("="*35)

def main():
    # Initialize our custom manager
    db = DatabaseManager("project52.db")

    # 1. Initialize the Database Table silently on startup
    db.execute_write("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1
    );
    """)

    # 2. The Application Loop
    while True:
        print_menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == '1':
            print("\n--- CURRENT USERS ---")
            users = db.execute_read("SELECT * FROM users")
            if not users:
                print("⚠️ No users found in the database.")
            else:
                for u in users:
                    # Formatting the dictionary output to look like a clean table
                    print(f"ID: {u['id']:<3} | User: {u['username']:<15} | Role: {u['role']:<10} | Active: {u['is_active']}")

        elif choice == '2':
            print("\n--- ADD NEW USER ---")
            username = input("Enter username: ").strip()
            role = input("Enter role (e.g., admin, editor, guest): ").strip()
            
            if username and role:
                success = db.execute_write("INSERT INTO users (username, role) VALUES (?, ?)", (username, role))
                if success:
                    print(f"✅ Successfully added '{username}' to the database.")
            else:
                print("❌ Error: Username and Role cannot be empty.")

        elif choice == '3':
            print("\n--- UPDATE USER ROLE ---")
            username = input("Enter the username to update: ").strip()
            new_role = input("Enter the new role: ").strip()
            
            if username and new_role:
                # Note: This will execute even if the user doesn't exist, but it won't crash.
                success = db.execute_write("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
                if success:
                    print(f"✅ Successfully updated '{username}' to role: {new_role}.")
            else:
                print("❌ Error: Inputs cannot be empty.")

        elif choice == '4':
            print("\n--- DELETE USER ---")
            username = input("Enter the username to DELETE: ").strip()
            
            # Add a safety confirmation before deleting!
            confirm = input(f"⚠️ Are you SURE you want to delete '{username}'? (y/n): ").strip().lower()
            if confirm == 'y':
                success = db.execute_write("DELETE FROM users WHERE username = ?", (username,))
                if success:
                    print(f"🗑️ Successfully deleted '{username}'.")
            else:
                print("🛑 Deletion cancelled.")

        elif choice == '5':
            print("\nShutting down Database Manager. Goodbye! 👋\n")
            sys.exit()

        else:
            print("\n❌ Invalid selection. Please type a number between 1 and 5.")

if __name__ == "__main__":
    main()