import cohere
import time
import random
from typing import List
from src.models.data_models import EmbeddingRequest, EmbeddingResponse
from src.utils.exceptions import CohereAPIError
from src.utils.circuit_breaker import CircuitBreaker, CircuitBreakerError


class CohereClient:
    """
    Client for interacting with Cohere API for embedding generation
    """

    def __init__(self, api_key: str, model: str = "embed-multilingual-v2.0", max_retries: int = 3, base_delay: float = 1.0):
        self.client = cohere.Client(api_key)
        self.model = model
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0, expected_exception=CohereAPIError)

    async def generate_embeddings(self, texts: List[str]) -> EmbeddingResponse:
        """
        Generate embeddings for the provided texts using Cohere API
        Includes retry logic with exponential backoff and circuit breaker
        """
        def _embed_with_retry():
            last_exception = None

            for attempt in range(self.max_retries + 1):
                try:
                    response = self.client.embed(
                        texts=texts,
                        model=self.model
                    )

                    return EmbeddingResponse(
                        embeddings=response.embeddings,
                        texts_count=len(texts)
                    )
                except Exception as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        # Exponential backoff with jitter
                        delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(delay)
                    else:
                        # All retries exhausted, raise the exception
                        raise CohereAPIError(f"Error calling Cohere API after {self.max_retries + 1} attempts: {str(e)}")

            # This line should not be reached, but included for completeness
            raise CohereAPIError(f"Unexpected error in Cohere API call: {str(last_exception)}")

        # Use the circuit breaker to protect the API call
        try:
            return self.circuit_breaker.call(_embed_with_retry)
        except CircuitBreakerError:
            raise CohereAPIError("Cohere API is temporarily unavailable due to circuit breaker protection")