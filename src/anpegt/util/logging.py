"""Structured JSON logging for ANPEGT-POL."""

import json
import logging
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "cycle_id"):
            log_entry["cycle_id"] = record.cycle_id
        if hasattr(record, "agent_id"):
            log_entry["agent_id"] = record.agent_id
        return json.dumps(log_entry, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(f"anpegt.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
