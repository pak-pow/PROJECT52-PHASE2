from app.db import get_db_connection

class TemplateModel:

    @classmethod
    def create_template(cls, name: str, channel: str, body_template: str, subject: str = None) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO templates (name, channel, subject, body_template)
            VALUES (?, ?, ?, ?)
        """, (name, channel.lower(), subject, body_template))
        template_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cls.get_by_id(template_id)

    @classmethod
    def get_by_id(cls, template_id: int) -> dict:
        conn = get_db_connection()
        tmpl = conn.execute("SELECT * FROM templates WHERE id = ?", (template_id,)).fetchone()
        conn.close()
        return dict(tmpl) if tmpl else None

    @classmethod
    def get_by_name(cls, name: str) -> dict:
        conn = get_db_connection()
        tmpl = conn.execute("SELECT * FROM templates WHERE name = ?", (name,)).fetchone()
        conn.close()
        return dict(tmpl) if tmpl else None

    @classmethod
    def get_all(cls) -> list[dict]:
        conn = get_db_connection()
        templates = conn.execute("SELECT * FROM templates ORDER BY name ASC").fetchall()
        conn.close()
        return [dict(t) for t in templates]
