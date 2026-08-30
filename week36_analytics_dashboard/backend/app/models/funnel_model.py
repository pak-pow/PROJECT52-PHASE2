from app.db import get_db_connection

class FunnelModel:
    @classmethod
    def create_funnel(cls, name: str, description: str = None, steps: list = None) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO funnels (name, description)
            VALUES (?, ?)
        """, (name, description))
        funnel_id = cursor.lastrowid

        if steps:
            for idx, step in enumerate(steps, start=1):
                cursor.execute("""
                    INSERT INTO funnel_steps (funnel_id, step_order, step_name, event_name)
                    VALUES (?, ?, ?, ?)
                """, (funnel_id, idx, step.get("step_name"), step.get("event_name")))

        conn.commit()
        conn.close()
        return cls.get_by_id(funnel_id)

    @classmethod
    def get_by_id(cls, funnel_id: int) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM funnels WHERE id = ?", (funnel_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        funnel_dict = dict(row)
        cursor.execute("""
            SELECT * FROM funnel_steps
            WHERE funnel_id = ?
            ORDER BY step_order ASC
        """, (funnel_id,))
        steps = cursor.fetchall()
        conn.close()
        funnel_dict["steps"] = [dict(s) for s in steps]
        return funnel_dict

    @classmethod
    def get_all(cls) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM funnels ORDER BY id ASC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            f_dict = dict(r)
            cursor.execute("""
                SELECT * FROM funnel_steps
                WHERE funnel_id = ?
                ORDER BY step_order ASC
            """, (f_dict["id"],))
            f_dict["steps"] = [dict(s) for s in cursor.fetchall()]
            result.append(f_dict)
        conn.close()
        return result
