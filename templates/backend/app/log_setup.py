import logging
from functools import lru_cache
import sys

# Define a logging format
LOG_FORMAT = (
    "\033[1;36m{asctime} {name} {levelname}\033[0m {message}"
)

LOG_FORMAT1 = (
    "\x1b[90m{asctime} {name} {levelname}\x1b[0m {message}"
)

@lru_cache  # Ensures the logger is only created once
def get_app_logger(logger_name: str = "app-main") -> logging.Logger:
    # Suppress SQLAlchemy logging
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    
    logger = logging.getLogger(logger_name)  # Shared logger
    logger.setLevel(logging.DEBUG)
    
    # Disable propagation to prevent messages from bubbling up to parent loggers
    logger.propagate = False

    # Remove any existing StreamHandlers to ensure we set up our own
    handlers_to_remove = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
    for handler in handlers_to_remove:
        logger.removeHandler(handler)

    # Set up our StreamHandler with the desired configuration
    formatter = logging.Formatter(
        fmt=LOG_FORMAT1 if logger_name.endswith('worker') else LOG_FORMAT,
        datefmt="%H:%M:%S",
        style="{",
    )

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

