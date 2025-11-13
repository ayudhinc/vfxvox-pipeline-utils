"""Logging setup and utilities for VFXVox Pipeline Utils."""

import logging
import sys
from pathlib import Path
from typing import Optional


# Track if logging has been configured
_logging_configured = False


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    log_format: Optional[str] = None,
    force: bool = False,
) -> None:
    """Configure logging for the toolkit.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        log_format: Optional custom log format string
        force: Force reconfiguration even if already configured
    """
    global _logging_configured

    if _logging_configured and not force:
        return

    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create handlers
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_file = Path(log_file)
        # Create parent directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers,
        force=force,
    )

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    # Ensure logging is configured with defaults if not already done
    if not _logging_configured:
        setup_logging()

    return logging.getLogger(name)


def reset_logging() -> None:
    """Reset logging configuration.

    Useful for testing or when you need to reconfigure logging.
    """
    global _logging_configured

    # Remove all handlers from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    _logging_configured = False
