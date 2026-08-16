from app.db import get_db_connection

class JobModel:

    @classmethod
    def create_job(cls, employer_id: int, title: str, company: str, location: str, job_type: str, salary_min: int, salary_max: int, category: str, description: str, requirements: str = "") -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jobs (employer_id, title, company, location, job_type, salary_min, salary_max, category, description, requirements)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (employer_id, title, company, location, job_type, salary_min, salary_max, category, description, requirements))
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cls.get_by_id(job_id)

    @classmethod
    def get_by_id(cls, job_id: int) -> dict:
        conn = get_db_connection()
        job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        conn.close()
        return dict(job) if job else None

    @classmethod
    def get_all(cls, keyword: str = None, location: str = None, job_type: str = None, category: str = None, min_salary: int = 0) -> list[dict]:
        conn = get_db_connection()
        query = "SELECT * FROM jobs WHERE is_active = 1"
        params = []

        if keyword:
            query += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
            kw_param = f"%{keyword}%"
            params.extend([kw_param, kw_param, kw_param])

        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")

        if job_type:
            query += " AND LOWER(job_type) = LOWER(?)"
            params.append(job_type)

        if category:
            query += " AND LOWER(category) = LOWER(?)"
            params.append(category)

        if min_salary and int(min_salary) > 0:
            query += " AND salary_max >= ?"
            params.append(int(min_salary))

        query += " ORDER BY created_at DESC"
        jobs = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(j) for j in jobs]

    @classmethod
    def get_by_employer(cls, employer_id: int) -> list[dict]:
        conn = get_db_connection()
        jobs = conn.execute("SELECT * FROM jobs WHERE employer_id = ? ORDER BY created_at DESC", (employer_id,)).fetchall()
        conn.close()
        return [dict(j) for j in jobs]

    @classmethod
    def update_job(cls, job_id: int, **kwargs) -> dict:
        conn = get_db_connection()
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ["title", "company", "location", "job_type", "salary_min", "salary_max", "category", "description", "requirements", "is_active"]:
                fields.append(f"{key} = ?")
                values.append(value)

        if fields:
            values.append(job_id)
            query = f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, values)
            conn.commit()
        conn.close()
        return cls.get_by_id(job_id)

    @classmethod
    def delete_job(cls, job_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        return rows > 0
