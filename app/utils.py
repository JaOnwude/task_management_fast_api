import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaskCompletion")


def log_completion_report(task_id: int, task_title: str, user_id: int) -> None:
    """Simulates generating/logging a task completion report in the background."""
    timestamp = datetime.utcnow().isoformat()
    logger.info(
        f"=== COMPLETION REPORT ===\n"
        f"Timestamp: {timestamp}\n"
        f"Task ID  : {task_id}\n"
        f"Title    : {task_title}\n"
        f"Assigned User ID: {user_id}\n"
        f"Status   : Successfully completed\n"
        f"========================="
    )