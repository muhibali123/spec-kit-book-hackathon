"""
Logging configuration for the Book Content Extraction & Structuring module.

This module sets up comprehensive logging for error tracking and debugging.
"""

import logging
import sys
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Set up logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
    """
    # Create logger
    logger = logging.getLogger('book_extraction')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_processing_event(logger, event_type: str, message: str, **kwargs):
    """
    Log a processing event with additional context.

    Args:
        logger: Logger instance
        event_type: Type of event (info, warning, error)
        message: Log message
        **kwargs: Additional context information
    """
    log_func = getattr(logger, event_type.lower(), logger.info)
    log_func(f"{message} | Context: {kwargs}")