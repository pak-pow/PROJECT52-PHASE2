import re
import uuid
import logging
from app.providers.base_provider import BaseNotificationProvider

logger = logging.getLogger(__name__)

class WebhookNotificationProvider(BaseNotificationProvider):
    """
    Webhook Push Notification Provider (Delivers HTTP Push Events).
    """

    def channel_name(self) -> str:
        return "webhook"

    def validate_recipient(self, recipient: str) -> bool:
        if not recipient or not isinstance(recipient, str):
            return False
        # HTTP / HTTPS URL regex pattern
        clean = recipient.strip()
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return bool(re.match(pattern, clean, re.IGNORECASE))

    def send(self, recipient: str, content: str, subject: str = None) -> dict:
        recipient_clean = recipient.strip()
        if not self.validate_recipient(recipient_clean):
            return {
                "success": False,
                "message_id": None,
                "error": f"Invalid webhook URL recipient format: '{recipient}'"
            }

        msg_id = f"hook_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"[WEBHOOK PROVIDER] Executing HTTP Push to {recipient_clean} | MsgID: {msg_id}")

        # Simulated successful HTTP Webhook push dispatch
        return {
            "success": True,
            "message_id": msg_id,
            "error": None
        }
