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

        for attr in [
            "request_id",
            "method",
            "endpoint",
            "status_code",
            "duration",
            "client_addr",
            "country",
            "path",
            "http_version",
        ]:
            val = getattr(record, attr, None)
            if val:
                log_record[attr] = val

        # IMPORTANT: ensure single JSON layer
        return json.dumps(log_record, ensure_ascii=False)


def setup_logging(
    for_docker=True, level=logging.INFO if os.getenv("ENV") == "dev" else logging.WARNING
):
    root_logger = logging.getLogger()
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
