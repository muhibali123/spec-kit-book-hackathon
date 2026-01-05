"""
Circuit breaker pattern implementation for the retrieval service.
"""
import time
import asyncio
from enum import Enum
from typing import Callable, Any, Optional, Awaitable


class CircuitState(Enum):
    """
    Possible states of the circuit breaker.
    """
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Failure threshold exceeded, requests blocked
    HALF_OPEN = "half_open"  # Testing if service has recovered


class CircuitBreakerError(Exception):
    """
    Exception raised when the circuit breaker is open.
    """
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation to prevent cascading failures.
    """

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: type = Exception):
        """
        Initialize the circuit breaker.

        Args:
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Time in seconds to wait before allowing a test request
            expected_exception: Exception type that counts as a failure
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call the function with circuit breaker protection.

        Args:
            func: Function to call
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function call

        Raises:
            CircuitBreakerError: If the circuit is open
            Exception: Any exception raised by the function when circuit is closed
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN. {self.failure_count} failures recorded."
                )

        try:
            result = func(*args, **kwargs)

            # If successful and in half-open state, reset the circuit
            if self.state == CircuitState.HALF_OPEN:
                self._on_success()

            return result

        except self.expected_exception as e:
            self._on_failure()
            raise e

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call the async function with circuit breaker protection.

        Args:
            func: Async function to call
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function call

        Raises:
            CircuitBreakerError: If the circuit is open
            Exception: Any exception raised by the function when circuit is closed
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN. {self.failure_count} failures recorded."
                )

        try:
            result = await func(*args, **kwargs)

            # If successful and in half-open state, reset the circuit
            if self.state == CircuitState.HALF_OPEN:
                self._on_success()

            return result

        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _on_failure(self) -> None:
        """
        Handle a failure by updating the circuit breaker state.
        """
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold and self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN

    def _on_success(self) -> None:
        """
        Handle a success by resetting the circuit breaker state.
        """
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def _should_attempt_reset(self) -> bool:
        """
        Check if enough time has passed to attempt resetting the circuit.

        Returns:
            True if it's time to attempt reset, False otherwise
        """
        if self.last_failure_time is None:
            return True

        return time.time() - self.last_failure_time >= self.recovery_timeout

    def reset(self) -> None:
        """
        Manually reset the circuit breaker to closed state.
        """
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def force_open(self) -> None:
        """
        Manually force the circuit breaker to open state.
        """
        self.state = CircuitState.OPEN