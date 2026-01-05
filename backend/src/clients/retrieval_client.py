from typing import Any, Dict, List, Optional
from src.models.data_models import RetrievedContext, ContextChunk
from src.services.retrieval_service import RetrievalService
from src.config.settings import settings


class RetrievalClient:
    """
    Client for interacting with the Module 04 Retrieval & Context Filtering Service
    """

    def __init__(self, retrieval_service: RetrievalService = None):
        """
        Initialize the retrieval client

        Args:
            retrieval_service: Optional retrieval service instance. If not provided, will create a new one.
        """
        if retrieval_service:
            self.retrieval_service = retrieval_service
        else:
            # Create the retrieval service with its dependencies
            # We'll create the dependencies directly without circular imports
            from src.clients.cohere_client import CohereClient
            from src.clients.qdrant_client import QdrantClient
            from src.services.filtering_service import FilteringService

            # Create the individual components using settings
            cohere_client = CohereClient(
                api_key=settings.cohere_api_key,
                model=settings.cohere_model
            )

            # Use URL if provided, otherwise use host/port
            if settings.qdrant_url:
                qdrant_client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key,
                    collection_name=settings.qdrant_collection
                )
            else:
                qdrant_client = QdrantClient(
                    host=settings.qdrant_host,
                    port=settings.qdrant_port,
                    api_key=settings.qdrant_api_key,
                    collection_name=settings.qdrant_collection
                )

            filtering_service = FilteringService()

            # Create the retrieval service
            self.retrieval_service = RetrievalService(
                cohere_client=cohere_client,
                qdrant_client=qdrant_client,
                filtering_service=filtering_service
            )

    async def retrieve_context(
        self,
        query: str,
        top_k: int = None,
        score_threshold: float = None,
        filters: Dict[str, Any] = None
    ) -> RetrievedContext:
        """
        Retrieve relevant context from the knowledge base with retry logic

        Args:
            query: The search query
            top_k: Number of results to return (default from settings)
            score_threshold: Minimum relevance score threshold (default from settings)
            filters: Optional filters to apply to the search

        Returns:
            Retrieved context containing relevant document chunks
        """
        # Use default values if not provided
        top_k = top_k or settings.default_top_k
        score_threshold = score_threshold or settings.default_score_threshold
        filters = filters or {}

        # Call the retrieval service directly
        retrieved_docs = await self.retrieval_service.retrieve_documents(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
            filters=filters
        )

        # Convert the retrieved documents to our internal data model
        context_chunks = []
        relevance_scores = []

        for doc in retrieved_docs:
            chunk = ContextChunk(
                chunk_id=doc.id,
                content=doc.payload.get('text', '') if isinstance(doc.payload, dict) else str(doc.payload),
                source_document=doc.payload.get('source', '') if isinstance(doc.payload, dict) else '',
                source_section=doc.payload.get('section', None) if isinstance(doc.payload, dict) else None,
                metadata=doc.payload if isinstance(doc.payload, dict) else {},
                relevance_score=doc.score
            )
            context_chunks.append(chunk)
            relevance_scores.append(doc.score)

        retrieved_context = RetrievedContext(
            context_chunks=context_chunks,
            relevance_scores=relevance_scores,
            metadata={"retrieval_method": "local_service"}
        )

        return retrieved_context

    async def health_check(self) -> bool:
        """
        Check if the retrieval service is healthy

        Returns:
            True if the service is healthy, False otherwise
        """
        try:
            # Try to perform a simple retrieval to test the service
            test_docs = await self.retrieval_service.retrieve_documents(
                query="health check",
                top_k=1,
                score_threshold=0.0
            )
            return True
        except Exception:
            return False