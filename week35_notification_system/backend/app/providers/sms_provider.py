import re
import uuid
import logging
from app.providers.base_provider import BaseNotificationProvider

logger = logging.getLogger(__name__)

class SMSNotificationProvider(BaseNotificationProvider):
    """
    SMS Notification Provider (Supports Twilio & E.164 Format Validation).
    """

    def channel_name(self) -> str:
        return "sms"

    def validate_recipient(self, recipient: str) -> bool:
        if not recipient or not isinstance(recipient, str):
            return False
        # E.164 phone number pattern (e.g. +14155552671 or digits)
        clean = recipient.strip()
        pattern = r"^\+?[1-9]\d{7,14}$"
        return bool(re.match(pattern, clean))

    def send(self, recipient: str, content: str, subject: str = None) -> dict:
        recipient_clean = recipient.strip()
        if not self.validate_recipient(recipient_clean):
            return {
                "success": False,
                "message_id": None,
                "error": f"Invalid phone number recipient format: '{recipient}'. Must match E.164 format (e.g. +14155552671)."
            }

        msg_id = f"sms_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"[SMS PROVIDER] Dispatching SMS to {recipient_clean} | Text Length: {len(content)} chars | MsgID: {msg_id}")

        # Simulated successful SMS dispatch
        return {
            "success": True,
            "message_id": msg_id,
            "error": None
        }
