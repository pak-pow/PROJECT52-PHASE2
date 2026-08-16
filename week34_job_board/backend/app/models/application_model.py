from app.db import get_db_connection

class ApplicationModel:

    @classmethod
    def create_application(cls, job_id: int, applicant_name: str, applicant_email: str, applicant_id: int = None, resume_path: str = None, cover_letter: str = "") -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications (job_id, applicant_id, applicant_name, applicant_email, resume_path, cover_letter)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (job_id, applicant_id, applicant_name, applicant_email, resume_path, cover_letter))
        app_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cls.get_by_id(app_id)

    @classmethod
    def get_by_id(cls, app_id: int) -> dict:
        conn = get_db_connection()
        app = conn.execute("""
            SELECT a.*, j.title AS job_title, j.company AS job_company 
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.id = ?
        """, (app_id,)).fetchone()
        conn.close()
        return dict(app) if app else None

    @classmethod
    def get_by_job(cls, job_id: int) -> list[dict]:
        conn = get_db_connection()
        apps = conn.execute("SELECT * FROM applications WHERE job_id = ? ORDER BY applied_at DESC", (job_id,)).fetchall()
        conn.close()
        return [dict(a) for a in apps]

    @classmethod
    def get_by_applicant(cls, applicant_id: int) -> list[dict]:
        conn = get_db_connection()
        apps = conn.execute("""
            SELECT a.*, j.title AS job_title, j.company AS job_company, j.location AS job_location
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.applicant_id = ?
            ORDER BY a.applied_at DESC
        """, (applicant_id,)).fetchall()
        conn.close()
        return [dict(a) for a in apps]

    @classmethod
    def update_status(cls, app_id: int, status: str) -> dict:
        conn = get_db_connection()
        conn.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
        conn.commit()
        conn.close()
        return cls.get_by_id(app_id)

    @classmethod
    def toggle_saved_job(cls, user_id: int, job_id: int) -> dict:
        conn = get_db_connection()
        existing = conn.execute("SELECT * FROM saved_jobs WHERE user_id = ? AND job_id = ?", (user_id, job_id)).fetchone()
        if existing:
            conn.execute("DELETE FROM saved_jobs WHERE user_id = ? AND job_id = ?", (user_id, job_id))
            saved = False
        else:
            conn.execute("INSERT INTO saved_jobs (user_id, job_id) VALUES (?, ?)", (user_id, job_id))
            saved = True
        conn.commit()
        conn.close()
        return {"user_id": user_id, "job_id": job_id, "saved": saved}

    @classmethod
    def get_saved_jobs(cls, user_id: int) -> list[dict]:
        conn = get_db_connection()
        jobs = conn.execute("""
            SELECT j.* FROM saved_jobs sj
            JOIN jobs j ON sj.job_id = j.id
            WHERE sj.user_id = ?
            ORDER BY sj.saved_at DESC
        """, (user_id,)).fetchall()
        conn.close()
        return [dict(j) for j in jobs]
