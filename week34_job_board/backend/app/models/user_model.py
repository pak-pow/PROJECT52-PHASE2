import hashlib
from app.db import get_db_connection

class UserModel:

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @classmethod
    def create_user(cls, username: str, email: str, password: str, role: str = "applicant", company_name: str = None) -> dict:
        password_hash = cls.hash_password(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, company_name)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password_hash, role, company_name))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cls.get_by_id(user_id)

    @classmethod
    def get_by_id(cls, user_id: int) -> dict:
        conn = get_db_connection()
        user = conn.execute("SELECT id, username, email, role, company_name, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None

    @classmethod
    def get_by_email(cls, email: str) -> dict:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return dict(user) if user else None

    @classmethod
    def verify_password(cls, email: str, password: str) -> dict:
        user = cls.get_by_email(email)
        if not user:
            return None
        if user["password_hash"] == cls.hash_password(password):
            user_data = dict(user)
            user_data.pop("password_hash", None)
            return user_data
        return None
