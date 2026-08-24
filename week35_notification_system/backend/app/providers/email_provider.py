import re
import uuid
import logging
from app.providers.base_provider import BaseNotificationProvider

logger = logging.getLogger(__name__)

class EmailNotificationProvider(BaseNotificationProvider):
    """
    Email Notification Provider (Supports Mock SMTP & Format Validation).
    """

    def channel_name(self) -> str:
        return "email"

    def validate_recipient(self, recipient: str) -> bool:
        if not recipient or not isinstance(recipient, str):
            return False
        # Basic email regex pattern
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        return bool(re.match(pattern, recipient.strip()))

    def send(self, recipient: str, content: str, subject: str = None) -> dict:
        recipient_clean = recipient.strip()
        if not self.validate_recipient(recipient_clean):
            return {
                "success": False,
                "message_id": None,
                "error": f"Invalid email address recipient format: '{recipient}'"
            }

        msg_id = f"email_{uuid.uuid4().hex[:12]}"
        subj = subject or "Notification Alert"

        logger.info(f"[EMAIL PROVIDER] Dispatching to {recipient_clean} | Subject: '{subj}' | MsgID: {msg_id}")
        
        # Simulated successful SMTP dispatch
        return {
            "success": True,
            "message_id": msg_id,
            "error": None
        }
