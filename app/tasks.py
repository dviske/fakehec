from app import scheduler
from app.models import Message
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def cleanup_old_messages():
    """Remove messages older than 7 days"""
    try:
        Message.remove_old_messages()
        print("Successfully cleaned up old messages")
        logger.info(f"Successfully cleaned up old messages at {datetime.now()}")
    except Exception as e:
        logger.error(f"Error cleaning up old messages: {str(e)}")

def init_scheduler():
    """Initialize scheduled tasks"""
    with scheduler.app.app_context():
        scheduler.add_job(
            id='cleanup_old_messages',
            func=cleanup_old_messages,
            trigger='cron',
            hour=13,  # Run at midnight
            minute=35
        )