def serialize_job(job_dict: dict) -> dict:
    if not job_dict:
        return {}
    return {
        "id": job_dict.get("id"),
        "employer_id": job_dict.get("employer_id"),
        "title": job_dict.get("title"),
        "company": job_dict.get("company"),
        "location": job_dict.get("location"),
        "job_type": job_dict.get("job_type"),
        "salary_min": job_dict.get("salary_min"),
        "salary_max": job_dict.get("salary_max"),
        "category": job_dict.get("category"),
        "description": job_dict.get("description"),
        "requirements": job_dict.get("requirements"),
        "is_active": bool(job_dict.get("is_active")),
        "created_at": str(job_dict.get("created_at"))
    }

def serialize_application(app_dict: dict) -> dict:
    if not app_dict:
        return {}
    return {
        "id": app_dict.get("id"),
        "job_id": app_dict.get("job_id"),
        "job_title": app_dict.get("job_title"),
        "job_company": app_dict.get("job_company"),
        "applicant_id": app_dict.get("applicant_id"),
        "applicant_name": app_dict.get("applicant_name"),
        "applicant_email": app_dict.get("applicant_email"),
        "resume_path": app_dict.get("resume_path"),
        "cover_letter": app_dict.get("cover_letter"),
        "status": app_dict.get("status"),
        "applied_at": str(app_dict.get("applied_at"))
    }
