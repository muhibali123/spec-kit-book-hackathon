from qdrant_client import AsyncQdrantClient as QdrantBaseClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
from src.models.data_models import QdrantSearchRequest, RetrievedDocument
from src.utils.exceptions import QdrantAPIError
from src.utils.circuit_breaker import CircuitBreaker, CircuitBreakerError


class QdrantClient:
    """
    Client for interacting with Qdrant vector database for similarity search
    """

    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "documents", api_key: str = None, url: str = None):
        if url:
            # Initialize without fastembed features to avoid dependency issues
            self.client = QdrantBaseClient(url=url, api_key=api_key, prefer_grpc=False)
        else:
            # Initialize without fastembed features to avoid dependency issues
            self.client = QdrantBaseClient(host=host, port=port, api_key=api_key, prefer_grpc=False)
        self.collection_name = collection_name
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0, expected_exception=QdrantAPIError)

    async def search(
        self,
        vector: List[float],
        top_k: int,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDocument]:
        """
        Perform similarity search in Qdrant database
        Includes circuit breaker protection
        """
        async def _search_with_circuit_breaker():
            try:
                # Prepare filters if provided
                qdrant_filters = None
                if filters:
                    filter_conditions = []
                    for key, value in filters.items():
                        filter_conditions.append(
                            models.FieldCondition(
                                key=key,
                                match=models.MatchValue(value=value)
                            )
                        )

                    if filter_conditions:
                        qdrant_filters = models.Filter(
                            must=filter_conditions
                        )

                # Use the correct query method for current Qdrant client
                # The AsyncQdrantClient has query_points method with specific parameters
                search_params = {
                    "collection_name": self.collection_name,
                    "query": vector,  # Current API uses query instead of query_vector
                    "limit": top_k,
                    "with_payload": True,  # Return payload data
                    "with_vectors": False,  # Don't return vectors to save bandwidth
                }

                # Add score threshold if provided
                if score_threshold is not None:
                    search_params["score_threshold"] = score_threshold

                # Add filters if provided
                if qdrant_filters is not None:
                    search_params["query_filter"] = qdrant_filters  # Use query_filter instead of filter

                # Execute the query
                query_response = await self.client.query_points(**search_params)

                # Convert Qdrant query response to our RetrievedDocument format
                # The query_points method returns a QueryResponse object with 'points' attribute
                results = []
                for hit in query_response.points:  # Use the points attribute of QueryResponse
                    # Standard ScoredPoint format for current Qdrant client
                    results.append(
                        RetrievedDocument(
                            id=hit.id,
                            payload=hit.payload,
                            score=hit.score
                        )
                    )

                return results
            except Exception as e:
                raise QdrantAPIError(f"Error calling Qdrant API: {str(e)}")

        # Use the circuit breaker to protect the API call
        try:
            return await self.circuit_breaker.call_async(_search_with_circuit_breaker)
        except CircuitBreakerError:
            raise QdrantAPIError("Qdrant API is temporarily unavailable due to circuit breaker protection")