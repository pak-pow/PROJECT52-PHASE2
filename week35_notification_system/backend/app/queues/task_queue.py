import queue
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from app.models.notification_model import NotificationModel
from app.models.user_preference_model import UserPreferenceModel
from app.providers.email_provider import EmailNotificationProvider
from app.providers.sms_provider import SMSNotificationProvider
from app.providers.webhook_provider import WebhookNotificationProvider
from app.config.settings import Config

logger = logging.getLogger(__name__)

class NotificationQueue:
    """
    Asynchronous Thread-Safe Notification Task Queue & Worker Thread Pool Manager.
    """

    def __init__(self, max_workers: int = 4):
        self.task_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="notif_worker")
        self.providers = {
            "email": EmailNotificationProvider(),
            "sms": SMSNotificationProvider(),
            "webhook": WebhookNotificationProvider()
        }
        self._running = True

    def enqueue(self, notification_id: int):
        """Enqueue notification ID for asynchronous processing"""
        self.task_queue.put(notification_id)
        self.executor.submit(self._process_task, notification_id)

    def _process_task(self, notification_id: int):
        """Worker task execution pipeline"""
        notif = NotificationModel.get_by_id(notification_id)
        if not notif:
            logger.error(f"[QUEUE WORKER] Notification ID {notification_id} not found in database.")
            return

        user_id = notif["user_id"]
        channel = notif["channel"].lower()
        recipient = notif["recipient"]
        content = notif["content"]
        subject = notif.get("subject")

        # 1. Check User Channel Preference
        if not UserPreferenceModel.is_channel_enabled(user_id, channel):
            logger.info(f"[QUEUE WORKER] User ID {user_id} opted out of {channel.upper()} channel. Skipping Notif #{notification_id}.")
            NotificationModel.update_status(
                notif_id=notification_id,
                status="Skipped",
                error_message=f"User opted out of {channel} notifications."
            )
            return

        # 2. Get Channel Provider
        provider = self.providers.get(channel)
        if not provider:
            logger.error(f"[QUEUE WORKER] Provider for channel '{channel}' not supported.")
            NotificationModel.update_status(
                notif_id=notification_id,
                status="Failed",
                error_message=f"Unsupported notification channel: {channel}"
            )
            return

        # 3. Update Status to Processing
        NotificationModel.update_status(notif_id=notification_id, status="Processing")

        # 4. Dispatch with Retry Attempts
        attempts = 0
        max_attempts = Config.MAX_RETRY_ATTEMPTS
        success = False
        last_error = None

        while attempts < max_attempts and not success:
            attempts += 1
            result = provider.send(recipient=recipient, content=content, subject=subject)

            if result["success"]:
                success = True
                NotificationModel.update_status(
                    notif_id=notification_id,
                    status="Sent",
                    attempts=attempts
                )
                logger.info(f"[QUEUE WORKER] Notif #{notification_id} dispatched successfully via {channel.upper()} (MsgID: {result.get('message_id')}).")
            else:
                last_error = result.get("error")
                logger.warning(f"[QUEUE WORKER] Attempt {attempts}/{max_attempts} failed for Notif #{notification_id}: {last_error}")
                if attempts < max_attempts:
                    time.sleep(0.2 * (2 ** attempts)) # Exponential backoff retry delay

        if not success:
            NotificationModel.update_status(
                notif_id=notification_id,
                status="Failed",
                error_message=last_error or "Dispatch attempts exhausted.",
                attempts=attempts
            )
            logger.error(f"[QUEUE WORKER] Notif #{notification_id} FAILED after {attempts} attempts.")

    def shutdown(self):
        """Shutdown worker thread pool cleanly"""
        self._running = False
        self.executor.shutdown(wait=True)

# Global singleton queue instance
notification_queue = NotificationQueue()
