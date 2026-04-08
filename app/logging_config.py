import os
import logging
import sys
import queue
import json
from logging.handlers import QueueHandler, QueueListener

# Create a global log queue
log_queue = queue.Queue(-1)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            # "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Optional fields (if present)
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "method"):
            log_record["method"] = record.method
        if hasattr(record, "endpoint"):
            log_record["endpoint"] = record.endpoint
        if hasattr(record, "status_code"):
            log_record["status_code"] = record.status_code
        if hasattr(record, "duration"):
            log_record["duration"] = record.duration
        if hasattr(record, "client_addr"):
            log_record["client_ip"] = record.client_addr
        if hasattr(record, "country"):
            log_record["country"] = record.country
        if hasattr(record, "path"):
            log_record["path"] = record.path
        if hasattr(record, "http_version"):
            log_record["http_version"] = record.http_version
        return json.dumps(log_record)


def setup_logging(for_docker=True):
    root_logger = logging.getLogger()
    level = logging.INFO if os.getenv("ENV") == "dev" else logging.WARNING
    root_logger.setLevel(level)

    # # Formatter (structured, readable)
    # formatter = logging.Formatter(
    #     fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    # )
    formatter = JsonFormatter()
    # Output handler (stdout for Docker)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # # Configure slowapi logger
    # slowapi_logger = logging.getLogger("slowapi")
    # slowapi_logger.addHandler(console_handler)
    # slowapi_logger.setLevel(logging.INFO)

    root_logger.handlers.clear()
    if for_docker:
        root_logger.addHandler(console_handler)
        return

    # Queue handler (non-blocking)
    queue_handler = QueueHandler(log_queue)
    root_logger.addHandler(queue_handler)

    # Listener (runs in background thread)
    listener = QueueListener(log_queue, console_handler)
    listener.start()
    return listener
