import os
import logging
import json
from logging.handlers import TimedRotatingFileHandler


def setup_logging(log_name: str):
    """
    Sets up a logger with both a rotating file handler and a JSON file handler.

    :param log_name: Name of the log file (without extension).
    :return: Configured logger instance.
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Standard log file
    log_filename = os.path.join(log_dir, f"{log_name}.log")
    handler = TimedRotatingFileHandler(
        log_filename, when="midnight", interval=1, backupCount=30,
        encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # JSON log file
    json_log_filename = os.path.join(log_dir, f"{log_name}.json")

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "function": record.funcName,
                "message": record.getMessage()
            }
            return json.dumps(log_entry, ensure_ascii=False)

    json_handler = logging.FileHandler(
        json_log_filename, mode="a", encoding="utf-8")
    json_handler.setFormatter(JsonFormatter())

    # Configure logger
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(json_handler)
    logger.addHandler(logging.StreamHandler())

    return logger
