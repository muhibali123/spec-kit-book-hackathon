"""
Ingestion statistics aggregation module for the Qdrant ingestion system.
"""
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class IngestionMetrics:
    """
    Data class to track ingestion metrics and statistics.
    """
    start_time: float = 0.0
    end_time: float = 0.0
    total_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    batch_count: int = 0
    total_duration_ms: float = 0.0
    records_per_second: float = 0.0
    failed_record_details: List[Dict[str, Any]] = field(default_factory=list)

    def start_timer(self):
        """Start the ingestion timer."""
        self.start_time = time.time()

    def stop_timer(self):
        """Stop the ingestion timer and calculate duration."""
        self.end_time = time.time()
        self.total_duration_ms = (self.end_time - self.start_time) * 1000

        # Calculate records per second if duration is not zero
        if self.total_duration_ms > 0:
            self.records_per_second = (self.successful_records + self.failed_records) / (self.total_duration_ms / 1000)

    def add_batch_stats(self, successful: int, failed: int, failed_details: List[Dict[str, Any]] = None):
        """Add statistics from a batch."""
        self.batch_count += 1
        self.successful_records += successful
        self.failed_records += failed
        self.total_records += successful + failed

        if failed_details:
            self.failed_record_details.extend(failed_details)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to a dictionary for reporting."""
        return {
            "total_records": self.total_records,
            "successful_records": self.successful_records,
            "failed_records": self.failed_records,
            "batch_count": self.batch_count,
            "total_duration_ms": round(self.total_duration_ms, 2),
            "records_per_second": round(self.records_per_second, 2),
            "success_rate": round(
                (self.successful_records / self.total_records * 100) if self.total_records > 0 else 0, 2
            ),
            "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time > 0 else None,
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time > 0 else None
        }


class MetricsAggregator:
    """
    Aggregates and manages ingestion statistics.
    """

    def __init__(self):
        self.current_metrics = IngestionMetrics()
        self.session_start_time = time.time()

    def start_ingestion(self):
        """Start tracking a new ingestion session."""
        self.current_metrics = IngestionMetrics()
        self.current_metrics.start_timer()

    def add_batch_metrics(
        self,
        successful: int,
        failed: int,
        failed_details: List[Dict[str, Any]] = None
    ):
        """Add metrics for a processed batch."""
        self.current_metrics.add_batch_stats(successful, failed, failed_details or [])

    def get_current_metrics(self) -> IngestionMetrics:
        """Get the current metrics object."""
        return self.current_metrics

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        # Stop timer if not already stopped
        if self.current_metrics.end_time == 0:
            self.current_metrics.stop_timer()

        return self.current_metrics.to_dict()

    def reset(self):
        """Reset metrics for a new session."""
        self.current_metrics = IngestionMetrics()