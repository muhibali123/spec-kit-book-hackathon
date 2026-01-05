"""
Metrics utilities for the retrieval service
Provides metrics collection and monitoring capabilities
"""
import time
from typing import Dict, Any, Callable, Optional
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum


class MetricType(Enum):
    """Types of metrics that can be collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Represents a single metric"""
    name: str
    type: MetricType
    value: float
    labels: Dict[str, str]
    description: str


class MetricsCollector:
    """
    Simple metrics collector for the retrieval service
    In a production environment, you would typically use Prometheus or similar
    """

    def __init__(self):
        self._metrics: Dict[str, Metric] = {}
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}

    def increment_counter(self, name: str, labels: Dict[str, str] = None, amount: float = 1.0):
        """Increment a counter metric"""
        labels = labels or {}
        key = f"{name}_" + "_".join([f"{k}={v}" for k, v in sorted(labels.items())])

        if key not in self._counters:
            self._counters[key] = 0.0
        self._counters[key] += amount

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric"""
        labels = labels or {}
        key = f"{name}_" + "_".join([f"{k}={v}" for k, v in sorted(labels.items())])
        self._gauges[key] = value

    def get_counter(self, name: str, labels: Dict[str, str] = None) -> float:
        """Get the current value of a counter"""
        labels = labels or {}
        key = f"{name}_" + "_".join([f"{k}={v}" for k, v in sorted(labels.items())])
        return self._counters.get(key, 0.0)

    def get_gauge(self, name: str, labels: Dict[str, str] = None) -> float:
        """Get the current value of a gauge"""
        labels = labels or {}
        key = f"{name}_" + "_".join([f"{k}={v}" for k, v in sorted(labels.items())])
        return self._gauges.get(key, 0.0)

    def get_metrics(self) -> Dict[str, float]:
        """Get all collected metrics"""
        all_metrics = {}
        all_metrics.update(self._counters)
        all_metrics.update(self._gauges)
        return all_metrics


# Global metrics collector instance
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return _metrics_collector


def increment_api_call_counter(endpoint: str, method: str, status_code: int):
    """Increment the API call counter with labels"""
    labels = {
        "endpoint": endpoint,
        "method": method,
        "status_code": str(status_code)
    }
    _metrics_collector.increment_counter("api_calls_total", labels)


def set_active_requests_gauge(count: int, endpoint: str = None):
    """Set the active requests gauge"""
    labels = {"endpoint": endpoint} if endpoint else {}
    _metrics_collector.set_gauge("active_requests", count, labels)


def record_retrieval_duration(duration: float):
    """Record the duration of a retrieval operation"""
    _metrics_collector.increment_counter("retrieval_duration_seconds_total", amount=duration)


def increment_retrieval_counter(success: bool = True):
    """Increment the retrieval counter"""
    labels = {"success": str(success).lower()}
    _metrics_collector.increment_counter("retrieval_operations_total", labels)


@contextmanager
def track_duration(metric_name: str, labels: Dict[str, str] = None):
    """
    Context manager to track the duration of an operation

    Usage:
    with track_duration("operation_duration", {"operation": "retrieval"}):
        # Your code here
        pass
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        labels = labels or {}
        labels["metric_name"] = metric_name
        _metrics_collector.increment_counter(f"{metric_name}_seconds_total", labels, duration)


def time_function(metric_name: str, labels: Dict[str, str] = None):
    """
    Decorator to time a function and record its duration

    Usage:
    @time_function("retrieval_duration", {"operation": "search"})
    def my_function():
        pass
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            with track_duration(metric_name, labels):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def collect_health_metrics() -> Dict[str, Any]:
    """Collect health-related metrics"""
    metrics = _metrics_collector.get_metrics()

    # Add computed metrics
    total_api_calls = sum(v for k, v in metrics.items() if k.startswith('api_calls_total'))
    retrieval_operations = sum(v for k, v in metrics.items() if k.startswith('retrieval_operations_total'))

    health_metrics = {
        "total_api_calls": total_api_calls,
        "retrieval_operations": retrieval_operations,
        "active_metrics": len(metrics),
        "timestamp": time.time()
    }

    return health_metrics