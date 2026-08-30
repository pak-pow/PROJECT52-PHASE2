import json
from app.db import get_db_connection

class EventModel:
    @classmethod
    def create_event(cls, event_name: str, session_id: str, url_path: str,
                     user_id: str = None, referrer: str = None,
                     device_type: str = "desktop", browser: str = "Chrome",
                     os_name: str = "Windows", country: str = "United States",
                     metadata: dict = None, created_at: str = None) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        metadata_str = json.dumps(metadata) if metadata else None

        if created_at:
            cursor.execute("""
                INSERT INTO events (
                    event_name, session_id, user_id, url_path, referrer,
                    device_type, browser, os, country, metadata_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_name, session_id, user_id, url_path, referrer,
                  device_type, browser, os_name, country, metadata_str, created_at))
        else:
            cursor.execute("""
                INSERT INTO events (
                    event_name, session_id, user_id, url_path, referrer,
                    device_type, browser, os, country, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_name, session_id, user_id, url_path, referrer,
                  device_type, browser, os_name, country, metadata_str))
            
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return cls.get_by_id(event_id)

    @classmethod
    def get_by_id(cls, event_id: int) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @classmethod
    def get_live_stream(cls, limit: int = 50) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM events
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def get_total_count(cls) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM events")
        row = cursor.fetchone()
        conn.close()
        return row["count"] if row else 0
