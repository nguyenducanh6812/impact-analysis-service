"""
Logging configuration for the Impact Analysis Service.
Centralized logging setup following DRY principles.
"""
from loguru import logger
import sys
from app.core.config import settings


def setup_logging():
    """Configure loguru logger with application settings."""

    # Remove default handler
    logger.remove()

    # Add custom handler with format from settings
    logger.add(
        sys.stdout,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True
    )

    # Add file handler for production
    if not settings.debug:
        logger.add(
            "logs/impact_analysis_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="30 days",
            level=settings.log_level,
            format=settings.log_format
        )

    return logger


# Initialize logger
log = setup_logging()
