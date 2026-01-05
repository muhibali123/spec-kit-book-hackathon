"""
Structured logging utilities for the embeddings generation module.
"""
import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
import json


class StructuredLogger:
    """
    Provides structured logging for the embeddings generation module.
    """

    def __init__(self, name: str = "embeddings", level: int = logging.INFO):
        """
        Initialize the structured logger.

        Args:
            name: Name of the logger
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create formatter for structured logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # Add handler if not already added
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)

    def log_event(self, event_type: str, message: str, **kwargs) -> None:
        """
        Log an event with structured data.

        Args:
            event_type: Type of the event (e.g., 'api_call', 'batch_processed', 'error')
            message: Human-readable message
            **kwargs: Additional structured data
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "message": message,
            **kwargs
        }

        # Log as JSON string for structured format
        self.logger.info(json.dumps(log_data))

    def log_api_call(self, model: str, batch_size: int, duration_ms: float,
                     success: bool, **kwargs) -> None:
        """
        Log a Cohere API call event.

        Args:
            model: The embedding model used
            batch_size: Number of texts in the batch
            duration_ms: API call duration in milliseconds
            success: Whether the call was successful
            **kwargs: Additional data
        """
        self.log_event(
            event_type="cohere_api_call",
            message=f"API call to {model} completed",
            model=model,
            batch_size=batch_size,
            duration_ms=duration_ms,
            success=success,
            **kwargs
        )

    def log_batch_processed(self, batch_id: str, total_chunks: int,
                          successful: int, failed: int, duration_ms: float, **kwargs) -> None:
        """
        Log a batch processing event.

        Args:
            batch_id: Unique identifier for the batch
            total_chunks: Total number of chunks in the batch
            successful: Number of successfully processed chunks
            failed: Number of failed chunks
            duration_ms: Processing duration in milliseconds
            **kwargs: Additional data
        """
        self.log_event(
            event_type="batch_processed",
            message=f"Batch {batch_id} processed",
            batch_id=batch_id,
            total_chunks=total_chunks,
            successful=successful,
            failed=failed,
            duration_ms=duration_ms,
            **kwargs
        )

    def log_error(self, error_type: str, message: str, **kwargs) -> None:
        """
        Log an error with structured data.

        Args:
            error_type: Type of the error
            message: Error message
            **kwargs: Additional data
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "error",
            "error_type": error_type,
            "message": message,
            **kwargs
        }

        self.logger.error(json.dumps(log_data))

    def log_chunk_failure(self, chunk_id: str, error_message: str, attempt: int = 1, **kwargs) -> None:
        """
        Log a chunk processing failure.

        Args:
            chunk_id: ID of the failed chunk
            error_message: Error message
            attempt: Attempt number (for retry tracking)
            **kwargs: Additional data
        """
        self.log_event(
            event_type="chunk_failure",
            message=f"Chunk {chunk_id} failed on attempt {attempt}",
            chunk_id=chunk_id,
            error_message=error_message,
            attempt=attempt,
            **kwargs
        )

    def log_process_start(self, process_id: str, total_chunks: int, **kwargs) -> None:
        """
        Log the start of an embedding generation process.

        Args:
            process_id: Unique identifier for the process
            total_chunks: Total number of chunks to process
            **kwargs: Additional data
        """
        self.log_event(
            event_type="process_start",
            message=f"Starting process {process_id} for {total_chunks} chunks",
            process_id=process_id,
            total_chunks=total_chunks,
            **kwargs
        )

    def log_process_complete(self, process_id: str, successful: int, failed: int,
                           duration_ms: float, **kwargs) -> None:
        """
        Log the completion of an embedding generation process.

        Args:
            process_id: Unique identifier for the process
            successful: Number of successfully processed chunks
            failed: Number of failed chunks
            duration_ms: Total processing duration in milliseconds
            **kwargs: Additional data
        """
        self.log_event(
            event_type="process_complete",
            message=f"Process {process_id} completed",
            process_id=process_id,
            successful=successful,
            failed=failed,
            duration_ms=duration_ms,
            success_rate=successful / (successful + failed) if (successful + failed) > 0 else 0,
            **kwargs
        )

    def log_audit_trail(self, process_id: str, chunk_id: str, action: str,
                       original_value: Any = None, new_value: Any = None, **kwargs) -> None:
        """
        Log an audit trail entry for tracking potential modifications.

        Args:
            process_id: Unique identifier for the process
            chunk_id: ID of the chunk being processed
            action: Action being performed (e.g., 'text_preserved', 'metadata_preserved')
            original_value: Original value before processing
            new_value: New value after processing
            **kwargs: Additional audit information
        """
        self.log_event(
            event_type="audit_trail",
            message=f"Audit trail for {action} on chunk {chunk_id}",
            process_id=process_id,
            chunk_id=chunk_id,
            action=action,
            original_value=original_value,
            new_value=new_value,
            **kwargs
        )

    def log_data_integrity_check(self, process_id: str, chunk_id: str,
                               check_type: str, is_valid: bool, **kwargs) -> None:
        """
        Log a data integrity check result.

        Args:
            process_id: Unique identifier for the process
            chunk_id: ID of the chunk being checked
            check_type: Type of integrity check (e.g., 'text_integrity', 'metadata_integrity')
            is_valid: Whether the integrity check passed
            **kwargs: Additional information
        """
        self.log_event(
            event_type="data_integrity_check",
            message=f"Data integrity check {check_type} for chunk {chunk_id}: {'PASS' if is_valid else 'FAIL'}",
            process_id=process_id,
            chunk_id=chunk_id,
            check_type=check_type,
            is_valid=is_valid,
            **kwargs
        )


# Global logger instance
logger = StructuredLogger()