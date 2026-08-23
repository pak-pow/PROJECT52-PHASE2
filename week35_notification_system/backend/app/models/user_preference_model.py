from app.db import get_db_connection

class UserPreferenceModel:

    @classmethod
    def get_user_preferences(cls, user_id: int) -> dict:
        conn = get_db_connection()
        pref = conn.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        if not pref:
            # Default: All channels enabled
            return {
                "user_id": user_id,
                "email_enabled": True,
                "sms_enabled": True,
                "webhook_enabled": True
            }
        return {
            "user_id": pref["user_id"],
            "email_enabled": bool(pref["email_enabled"]),
            "sms_enabled": bool(pref["sms_enabled"]),
            "webhook_enabled": bool(pref["webhook_enabled"])
        }

    @classmethod
    def set_user_preferences(cls, user_id: int, email_enabled: bool = True, sms_enabled: bool = True, webhook_enabled: bool = True) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_preferences (user_id, email_enabled, sms_enabled, webhook_enabled, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                email_enabled = excluded.email_enabled,
                sms_enabled = excluded.sms_enabled,
                webhook_enabled = excluded.webhook_enabled,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, int(email_enabled), int(sms_enabled), int(webhook_enabled)))
        conn.commit()
        conn.close()
        return cls.get_user_preferences(user_id)

    @classmethod
    def is_channel_enabled(cls, user_id: int, channel: str) -> bool:
        prefs = cls.get_user_preferences(user_id)
        ch = channel.lower()
        if ch == "email":
            return prefs["email_enabled"]
        elif ch == "sms":
            return prefs["sms_enabled"]
        elif ch == "webhook":
            return prefs["webhook_enabled"]
        return True
