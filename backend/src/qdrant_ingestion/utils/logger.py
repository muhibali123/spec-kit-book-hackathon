"""
Comprehensive logging module for the Qdrant ingestion system.
"""
import logging
import sys
from typing import Any, Dict
from datetime import datetime


class QdrantIngestionLogger:
    """
    A comprehensive logging module for Qdrant ingestion with structured logging.
    """

    def __init__(self, name: str = "qdrant_ingestion", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Prevent adding multiple handlers if logger already exists
        if not self.logger.handlers:
            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)

            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)

            # Add handler to logger
            self.logger.addHandler(console_handler)

    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log an info message."""
        self.logger.info(message, extra=extra or {})

    def error(self, message: str, extra: Dict[str, Any] = None):
        """Log an error message."""
        self.logger.error(message, extra=extra or {})

    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log a warning message."""
        self.logger.warning(message, extra=extra or {})

    def debug(self, message: str, extra: Dict[str, Any] = None):
        """Log a debug message."""
        self.logger.debug(message, extra=extra or {})

    def log_ingestion_event(
        self,
        event_type: str,
        collection_name: str,
        record_count: int = 0,
        success_count: int = 0,
        error_count: int = 0,
        duration_ms: float = 0.0
    ):
        """Log a structured ingestion event."""
        event_data = {
            "event_type": event_type,
            "collection_name": collection_name,
            "timestamp": datetime.utcnow().isoformat(),
            "record_count": record_count,
            "success_count": success_count,
            "error_count": error_count,
            "duration_ms": duration_ms
        }

        if error_count > 0:
            self.logger.error(f"Ingestion event: {event_type}", extra=event_data)
        else:
            self.logger.info(f"Ingestion event: {event_type}", extra=event_data)


# Global logger instance
default_logger = QdrantIngestionLogger()


def get_logger(name: str = "qdrant_ingestion") -> QdrantIngestionLogger:
    """
    Get a configured logger instance.
    """
    return QdrantIngestionLogger(name)