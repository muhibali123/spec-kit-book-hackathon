"""
Logging utilities for the retrieval service
Provides structured logging configuration and utilities
"""
import logging
import sys
from typing import Dict, Any
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO", json_format: bool = True) -> logging.Logger:
    """
    Set up structured logging for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON format for logs

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("retrieval_service")

    # Avoid adding handlers if logger is already configured
    if logger.handlers:
        return logger

    # Set the logging level
    logger.setLevel(getattr(logging, log_level.upper()))

    # Create a handler that writes to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))

    if json_format:
        # Create JSON formatter
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ"
        )
    else:
        # Create standard formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the specified name

    Args:
        name: Name of the logger (optional, defaults to "retrieval_service")

    Returns:
        Logger instance
    """
    if name is None:
        name = "retrieval_service"

    return logging.getLogger(name)


def log_api_call(
    logger: logging.Logger,
    endpoint: str,
    method: str,
    duration: float,
    status_code: int,
    user_id: str = None,
    metadata: Dict[str, Any] = None
) -> None:
    """
    Log API call with structured format

    Args:
        logger: Logger instance to use
        endpoint: API endpoint that was called
        method: HTTP method (GET, POST, etc.)
        duration: Duration of the API call in seconds
        status_code: HTTP status code returned
        user_id: Optional user ID for the request
        metadata: Optional additional metadata to log
    """
    log_data = {
        "event": "api_call",
        "endpoint": endpoint,
        "method": method,
        "duration": duration,
        "status_code": status_code
    }

    if user_id:
        log_data["user_id"] = user_id

    if metadata:
        log_data.update(metadata)

    logger.info("API call completed", extra=log_data)


def log_retrieval_request(
    logger: logging.Logger,
    query: str,
    top_k: int,
    score_threshold: float,
    duration: float,
    results_count: int,
    metadata: Dict[str, Any] = None
) -> None:
    """
    Log document retrieval request with structured format

    Args:
        logger: Logger instance to use
        query: The query that was processed
        top_k: Number of top results requested
        score_threshold: Score threshold applied
        duration: Duration of the retrieval in seconds
        results_count: Number of results returned
        metadata: Optional additional metadata to log
    """
    log_data = {
        "event": "retrieval_request",
        "query_length": len(query),
        "top_k": top_k,
        "score_threshold": score_threshold,
        "duration": duration,
        "results_count": results_count
    }

    if metadata:
        log_data.update(metadata)

    logger.info("Document retrieval completed", extra=log_data)


def log_error(
    logger: logging.Logger,
    error_type: str,
    error_message: str,
    endpoint: str = None,
    metadata: Dict[str, Any] = None
) -> None:
    """
    Log error with structured format

    Args:
        logger: Logger instance to use
        error_type: Type/classification of the error
        error_message: Error message
        endpoint: Optional endpoint where error occurred
        metadata: Optional additional metadata to log
    """
    log_data = {
        "event": "error",
        "error_type": error_type,
        "error_message": error_message
    }

    if endpoint:
        log_data["endpoint"] = endpoint

    if metadata:
        log_data.update(metadata)

    logger.error("Error occurred", extra=log_data)