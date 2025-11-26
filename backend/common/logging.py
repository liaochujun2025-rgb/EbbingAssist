import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Render log records as JSON with common fields."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Merge extra fields if provided
        for key, value in record.__dict__.items():
            if key.startswith(("_", "args", "msg", "levelname", "levelno", "msecs", "relativeCreated",
                               "created", "name", "thread", "threadName", "process", "processName",
                               "pathname", "filename", "module", "funcName", "lineno", "exc_info",
                               "exc_text", "stack_info", "stacklevel")):
                continue
            payload[key] = value
        return json.dumps(payload, ensure_ascii=False)
