from abc import ABC, abstractmethod

class BaseNotificationProvider(ABC):
    """
    Abstract Base Class for Multi-Channel Notification Dispatchers.
    """

    @abstractmethod
    def channel_name(self) -> str:
        """Return the unique channel string ('email', 'sms', 'webhook')"""
        pass

    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """Validate recipient address/number format"""
        pass

    @abstractmethod
    def send(self, recipient: str, content: str, subject: str = None) -> dict:
        """
        Execute dispatch delivery.
        Must return dict: { "success": bool, "message_id": str, "error": str/None }
        """
        pass
