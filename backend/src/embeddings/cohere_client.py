"""
Cohere API client wrapper for the embeddings generation module.
"""
import cohere
from typing import List, Dict, Any
from src.config.environment import config
from src.utils.retry import retry_with_exponential_backoff
from src.embeddings.logger import logger
from src.utils.circuit_breaker import CircuitBreaker, CircuitBreakerError
import logging


class CohereClientError(Exception):
    """
    Custom exception for Cohere client errors.
    """
    pass


class CohereRateLimitError(CohereClientError):
    """
    Exception for Cohere rate limit errors.
    """
    pass


class CohereAuthenticationError(CohereClientError):
    """
    Exception for Cohere authentication errors.
    """
    pass


class CohereServerError(CohereClientError):
    """
    Exception for Cohere server errors.
    """
    pass


class CohereClient:
    """
    Wrapper around the Cohere API for generating embeddings.
    """

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the Cohere client.

        Args:
            api_key: Cohere API key (uses config if not provided)
            model: Embedding model to use (uses config if not provided)
        """
        self.api_key = api_key or config.cohere_api_key
        self.model = model or config.cohere_model

        if not self.api_key:
            raise ValueError("Cohere API key is required")

        self.client = cohere.Client(self.api_key)

        # Initialize circuit breaker for extreme failure scenarios
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0,  # 60 seconds
            expected_exception=(CohereRateLimitError, CohereServerError)
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)

        Raises:
            CohereClientError: If the API call fails
            CircuitBreakerError: If the circuit breaker is open
        """
        # Use the circuit breaker to protect against cascading failures
        return self.circuit_breaker.call(self._generate_embeddings_with_retry, texts)

    @retry_with_exponential_backoff(
        max_retries=config.max_retries,
        base_delay=config.retry_delay / 1000.0,  # Convert to seconds
        allowed_exceptions=(CohereRateLimitError, CohereServerError)
    )
    def _generate_embeddings_with_retry(self, texts: List[str]) -> List[List[float]]:
        """
        Internal method to generate embeddings with retry logic.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)

        Raises:
            CohereClientError: If the API call fails
        """
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document"  # Appropriate for document search use case
            )

            if not response or not response.embeddings:
                raise CohereClientError("No embeddings returned from Cohere API")

            return response.embeddings

        except cohere.core.ApiError as e:
            # Handle different types of API errors
            status_code = e.status_code if hasattr(e, 'status_code') else None

            if status_code == 401:
                error_msg = f"Cohere authentication error: Invalid API key"
                logger.log_error("authentication_error", error_msg, status_code=status_code)
                raise CohereAuthenticationError(error_msg) from e
            elif status_code == 429:
                error_msg = f"Cohere rate limit error: Too many requests"
                logger.log_error("rate_limit_error", error_msg, status_code=status_code)
                raise CohereRateLimitError(error_msg) from e
            elif 500 <= status_code < 600:
                error_msg = f"Cohere server error: {str(e)}"
                logger.log_error("server_error", error_msg, status_code=status_code)
                raise CohereServerError(error_msg) from e
            else:
                error_msg = f"Cohere API error (status {status_code}): {str(e)}"
                logger.log_error("api_error", error_msg, status_code=status_code)
                raise CohereClientError(error_msg) from e

        except Exception as e:
            error_msg = f"Cohere API error: {str(e)}"
            logger.log_error("api_error", error_msg, error_type=type(e).__name__)
            raise CohereClientError(error_msg) from e

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model being used.

        Returns:
            Dictionary containing model information
        """
        # For now, we'll return basic model info
        # In a real implementation, this might call the Cohere API to get model details
        return {
            "model_name": self.model,
            "dimensions": self._get_expected_dimensions()  # This would come from API in real implementation
        }

    def _get_expected_dimensions(self) -> int:
        """
        Get the expected dimensions for the current model.
        This is a simplified implementation - in reality, you'd query the API for this info.

        Returns:
            Expected embedding dimension count
        """
        # Different Cohere models have different dimensions
        # embed-english-v3.0: typically 1024 or 384 dimensions depending on settings
        # This is a simplified mapping - in practice, you'd get this from the API
        if "v3" in self.model:
            # For v3 models, default to 1024, though it can be configured differently
            return 1024
        else:
            # Default for other models
            return 1024