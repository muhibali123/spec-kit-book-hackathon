from typing import List, Dict, Any, Optional
import time
import re
from src.models.data_models import RetrievedDocument
from src.clients.cohere_client import CohereClient
from src.clients.qdrant_client import QdrantClient
from src.services.filtering_service import FilteringService
from src.utils.exceptions import ValidationError
from src.utils.logging import get_logger, log_retrieval_request


class RetrievalService:
    """
    Service for handling document retrieval logic
    Orchestrates embedding generation, similarity search, and result filtering
    """

    def __init__(self, cohere_client: CohereClient, qdrant_client: QdrantClient, filtering_service: FilteringService, logger=None):
        self.cohere_client = cohere_client
        self.qdrant_client = qdrant_client
        self.filtering_service = filtering_service
        self.logger = logger or get_logger(__name__)

    def _preprocess_query(self, query: str) -> str:
        """
        Preprocess the query by cleaning and normalizing it
        """
        if not query or not query.strip():
            raise ValidationError("Query cannot be empty")

        # Remove extra whitespace
        query = ' '.join(query.split())

        # Basic sanitization - remove potentially harmful characters
        # In a real implementation, you might want more sophisticated sanitization
        query = re.sub(r'[<>{}]', '', query)

        return query.strip()

    def _validate_parameters(self, query: str, top_k: int, score_threshold: float) -> None:
        """
        Validate input parameters
        """
        if not query or len(query.strip()) == 0:
            raise ValidationError("Query cannot be empty")

        if len(query) > 1000:  # As per the spec requirement
            raise ValidationError(f"Query length exceeds maximum of 1000 characters: {len(query)}")

        if top_k < 1 or top_k > 100:  # As per the spec requirement
            raise ValidationError(f"top_k must be between 1 and 100: {top_k}")

        if score_threshold < 0.0 or score_threshold > 1.0:  # As per the spec requirement
            raise ValidationError(f"score_threshold must be between 0.0 and 1.0: {score_threshold}")

    async def retrieve_documents(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDocument]:
        """
        Main method to retrieve relevant documents for a query
        Orchestrates the full retrieval process:
        1. Validate input parameters
        2. Preprocess the query
        3. Generate embeddings for the query using Cohere
        4. Perform similarity search against Qdrant
        5. Apply filtering based on score threshold and metadata filters
        6. Return the filtered and ranked results
        """
        import time
        start_time = time.time()

        self.logger.info(f"Starting document retrieval for query of length {len(query)}", extra={
            "event": "retrieval_start",
            "query_length": len(query),
            "top_k": top_k,
            "score_threshold": score_threshold
        })

        try:
            # Validate input parameters
            self._validate_parameters(query, top_k, score_threshold)

            # Preprocess the query
            processed_query = self._preprocess_query(query)

            # Generate embedding for the query
            embedding_start = time.time()
            embedding_response = await self.cohere_client.generate_embeddings([processed_query])
            query_embedding = embedding_response.embeddings[0]
            embedding_time = time.time() - embedding_start

            self.logger.debug("Embedding generation completed", extra={
                "event": "embedding_generation",
                "embedding_time": embedding_time,
                "embedding_length": len(query_embedding) if query_embedding else 0
            })

            # Perform similarity search in Qdrant
            search_start = time.time()
            search_results = await self.qdrant_client.search(
                vector=query_embedding,
                top_k=top_k * 2,  # Get more results than needed for filtering
                score_threshold=score_threshold,
                filters=filters
            )
            search_time = time.time() - search_start

            self.logger.debug("Similarity search completed", extra={
                "event": "similarity_search",
                "search_time": search_time,
                "search_results_count": len(search_results)
            })

            # Apply score threshold filtering
            filter_start = time.time()
            filtered_by_score = await self.filtering_service.filter_by_score_threshold(
                search_results,
                score_threshold
            )

            # Apply metadata filtering if filters are provided
            if filters:
                filtered_results = await self.filtering_service.filter_by_metadata(
                    filtered_by_score,
                    filters
                )
            else:
                filtered_results = filtered_by_score

            # Rank the results by score
            ranked_results = await self.filtering_service.rank_documents(filtered_results)

            # Limit to the requested top_k
            final_results = ranked_results[:top_k]
            filter_time = time.time() - filter_start

            total_time = time.time() - start_time

            self.logger.info(f"Document retrieval completed successfully with {len(final_results)} results", extra={
                "event": "retrieval_success",
                "results_count": len(final_results),
                "total_time": total_time,
                "embedding_time": embedding_time,
                "search_time": search_time,
                "filter_time": filter_time
            })

            # Log retrieval metrics using the utility function
            log_retrieval_request(
                self.logger,
                query,
                top_k,
                score_threshold,
                total_time,
                len(final_results),
                {
                    "filters_applied": bool(filters),
                    "original_search_results": len(search_results),
                    "filtered_results": len(filtered_by_score)
                }
            )

            return final_results
        except Exception as e:
            total_time = time.time() - start_time
            self.logger.error(f"Document retrieval failed: {str(e)}", extra={
                "event": "retrieval_error",
                "error_type": type(e).__name__,
                "total_time": total_time
            })
            raise