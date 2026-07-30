"""
Centralized logging configuration for FeedbackIQ.
"""
import logging
import sys
from app.config.settings import get_settings

settings = get_settings()

def setup_logging() -> None:
    """Sets up the global logging configuration."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Standard format: timestamp | level | logger | message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Standard output handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers to prevent duplicate logs
    root_logger.handlers = []
    root_logger.addHandler(stdout_handler)

    # Set specific third-party logger levels to avoid spam
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
