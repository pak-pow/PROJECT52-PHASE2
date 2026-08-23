import json
from app.db import get_db_connection

class NotificationModel:

    @classmethod
    def create_notification(cls, user_id: int, recipient: str, channel: str, content: str, subject: str = None, template_name: str = None, variables: dict = None, idempotency_key: str = None) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        variables_json = json.dumps(variables) if variables else None
        
        cursor.execute("""
            INSERT INTO notifications (idempotency_key, user_id, recipient, channel, template_name, subject, content, variables_json, status, attempts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Queued', 0)
        """, (idempotency_key, user_id, recipient, channel.lower(), template_name, subject, content, variables_json))
        
        notif_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cls.get_by_id(notif_id)

    @classmethod
    def get_by_id(cls, notif_id: int) -> dict:
        conn = get_db_connection()
        n = conn.execute("SELECT * FROM notifications WHERE id = ?", (notif_id,)).fetchone()
        conn.close()
        return dict(n) if n else None

    @classmethod
    def get_by_idempotency_key(cls, idempotency_key: str) -> dict:
        if not idempotency_key:
            return None
        conn = get_db_connection()
        n = conn.execute("SELECT * FROM notifications WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
        conn.close()
        return dict(n) if n else None

    @classmethod
    def update_status(cls, notif_id: int, status: str, error_message: str = None, attempts: int = None) -> dict:
        conn = get_db_connection()
        fields = ["status = ?"]
        values = [status]

        if error_message is not None:
            fields.append("error_message = ?")
            values.append(error_message)

        if attempts is not None:
            fields.append("attempts = ?")
            values.append(attempts)

        if status == "Sent":
            fields.append("sent_at = CURRENT_TIMESTAMP")

        values.append(notif_id)
        query = f"UPDATE notifications SET {', '.join(fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        conn.close()
        return cls.get_by_id(notif_id)

    @classmethod
    def get_user_notifications(cls, user_id: int, limit: int = 50) -> list[dict]:
        conn = get_db_connection()
        notifs = conn.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit)).fetchall()
        conn.close()
        return [dict(n) for n in notifs]

    @classmethod
    def count_recent_user_notifications(cls, user_id: int, minutes: int = 1) -> int:
        conn = get_db_connection()
        res = conn.execute("""
            SELECT COUNT(*) as count FROM notifications 
            WHERE user_id = ? AND created_at >= datetime('now', '-' || ? || ' minute')
        """, (user_id, minutes)).fetchone()
        conn.close()
        return res["count"] if res else 0
