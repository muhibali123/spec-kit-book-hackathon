"""
Retry logic utility for the embeddings generation module.
"""
import time
import random
import asyncio
from typing import Callable, Any, Union, Type
from functools import wraps


def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    allowed_exceptions: tuple = (Exception,)
):
    """
    Decorator that implements retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        jitter: Whether to add random jitter to the delay
        allowed_exceptions: Tuple of exceptions that trigger a retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # No more retries left
                        break

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)

                    # Add jitter if enabled
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)

                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s...")

                    time.sleep(delay)

            # If we've exhausted all retries, raise the last exception
            raise last_exception

        return wrapper
    return decorator


async def async_retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    allowed_exceptions: tuple = (Exception,)
):
    """
    Async decorator that implements retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        jitter: Whether to add random jitter to the delay
        allowed_exceptions: Tuple of exceptions that trigger a retry
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except allowed_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # No more retries left
                        break

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)

                    # Add jitter if enabled
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)

                    print(f"Async attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s...")

                    await asyncio.sleep(delay)

            # If we've exhausted all retries, raise the last exception
            raise last_exception

        return async_wrapper
    return decorator


class RetryHandler:
    """
    A utility class for handling retry logic with configurable parameters.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        allowed_exceptions: tuple = (Exception,)
    ):
        """
        Initialize the retry handler with configuration.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_factor: Multiplier for delay after each retry
            jitter: Whether to add random jitter to the delay
            allowed_exceptions: Tuple of exceptions that trigger a retry
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.allowed_exceptions = allowed_exceptions

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function execution
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except self.allowed_exceptions as e:
                last_exception = e

                if attempt == self.max_retries:
                    # No more retries left
                    break

                # Calculate delay with exponential backoff
                delay = min(self.base_delay * (self.backoff_factor ** attempt), self.max_delay)

                # Add jitter if enabled
                if self.jitter:
                    delay = delay * (0.5 + random.random() * 0.5)

                print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s...")

                time.sleep(delay)

        # If we've exhausted all retries, raise the last exception
        raise last_exception

    async def execute_async_with_retry(self, func, *args, **kwargs):
        """
        Execute an async function with retry logic.

        Args:
            func: Async function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function execution
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except self.allowed_exceptions as e:
                last_exception = e

                if attempt == self.max_retries:
                    # No more retries left
                    break

                # Calculate delay with exponential backoff
                delay = min(self.base_delay * (self.backoff_factor ** attempt), self.max_delay)

                # Add jitter if enabled
                if self.jitter:
                    delay = delay * (0.5 + random.random() * 0.5)

                print(f"Async attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s...")

                await asyncio.sleep(delay)

        # If we've exhausted all retries, raise the last exception
        raise last_exception