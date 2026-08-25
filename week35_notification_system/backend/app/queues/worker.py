import logging
from app.queues.task_queue import notification_queue

logger = logging.getLogger(__name__)

def enqueue_notification_job(notification_id: int):
    """
    Public helper to dispatch notification ID into background worker queue.
    """
    logger.info(f"[DISPATCHER] Enqueuing notification ID {notification_id} into async worker queue...")
    notification_queue.enqueue(notification_id)
