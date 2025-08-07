"""
Logging utilities for the Artemis framework.

Provides a configured logger instance with consistent formatting and levels.
Uses loguru for advanced logging capabilities.
"""

from loguru import logger as _logger
import sys

# Configure logger with consistent formatting
logger = _logger

# Remove default handler and add our custom one
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)


def set_level(level: str) -> None:
    """Set the logging level for all handlers."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level.upper()
    )
