import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db, get_db_connection
from app.models.template_model import TemplateModel
from app.models.user_preference_model import UserPreferenceModel

def seed_database():
    print("[SEED] Initializing database schema...")
    init_db()

    conn = get_db_connection()
    existing = conn.execute("SELECT COUNT(*) as count FROM templates").fetchone()
    if existing["count"] > 0:
        print("[SEED] Database templates already seeded. Skipping.")
        conn.close()
        return

    conn.close()

    print("[SEED] Seeding notification templates (Email, SMS, Webhook)...")
    TemplateModel.create_template(
        name="welcome_email",
        channel="email",
        subject="Welcome to TechJobs Platform, {{ username }}! 🎉",
        body_template="Hi {{ username }},\n\nWelcome to TechJobs! Your account ({{ email }}) has been created successfully. Explore exciting tech job opportunities today!"
    )

    TemplateModel.create_template(
        name="job_application_submitted",
        channel="email",
        subject="Application Received: {{ job_title }} at {{ company }}",
        body_template="Hello {{ applicant_name }},\n\nYour application for '{{ job_title }}' at {{ company }} has been submitted successfully. The recruitment team will review your resume shortly."
    )

    TemplateModel.create_template(
        name="security_alert_sms",
        channel="sms",
        subject=None,
        body_template="[Security Alert] New sign-in detected on your account {{ username }} from {{ location }} at {{ time }}."
    )

    TemplateModel.create_template(
        name="application_status_webhook",
        channel="webhook",
        subject=None,
        body_template="Notification Event: Application {{ app_id }} status changed to '{{ status }}' for user {{ user_id }}."
    )

    print("[SEED] Seeding default user channel preferences...")
    UserPreferenceModel.set_user_preferences(user_id=1, email_enabled=True, sms_enabled=True, webhook_enabled=True)
    UserPreferenceModel.set_user_preferences(user_id=2, email_enabled=True, sms_enabled=False, webhook_enabled=True)

    print("[SEED] Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
