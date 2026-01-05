import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.retrieval_service import RetrievalService
from src.services.filtering_service import FilteringService
from src.clients.cohere_client import CohereClient
from src.clients.qdrant_client import QdrantClient
from src.models.data_models import RetrievedDocument, EmbeddingResponse


class TestRetrievalIntegration:
    @pytest.mark.asyncio
    async def test_full_retrieval_flow(self):
        """Test the complete retrieval flow with mocked dependencies"""
        # Create mocked clients
        mock_cohere_client = AsyncMock(spec=CohereClient)
        mock_qdrant_client = AsyncMock(spec=QdrantClient)
        mock_filtering_service = MagicMock(spec=FilteringService)

        # Mock embedding response
        mock_embedding_response = EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3, 0.4]],
            texts_count=1
        )
        mock_cohere_client.generate_embeddings.return_value = mock_embedding_response

        # Mock search results
        mock_search_results = [
            RetrievedDocument(
                id="doc_1",
                payload={
                    "text": "This is a relevant document about renewable energy",
                    "source": "renewable_energy.pdf",
                    "page": 1,
                    "author": "Smith"
                },
                score=0.85
            ),
            RetrievedDocument(
                id="doc_2",
                payload={
                    "text": "Another document about sustainable energy sources",
                    "source": "sustainability.pdf",
                    "page": 5,
                    "author": "Johnson"
                },
                score=0.78
            )
        ]
        mock_qdrant_client.search.return_value = mock_search_results

        # Mock filtering service
        mock_filtering_service.filter_by_score_threshold.return_value = mock_search_results
        mock_filtering_service.filter_by_metadata.return_value = mock_search_results
        mock_filtering_service.rank_documents.return_value = mock_search_results

        # Create retrieval service with mocked dependencies
        service = RetrievalService(
            cohere_client=mock_cohere_client,
            qdrant_client=mock_qdrant_client,
            filtering_service=mock_filtering_service
        )

        # Test the full retrieval flow
        query = "renewable energy sources"
        results = await service.retrieve_documents(
            query=query,
            top_k=5,
            score_threshold=0.5
        )

        # Verify the flow worked correctly
        assert len(results) == 2
        assert all(isinstance(doc, RetrievedDocument) for doc in results)
        assert all(doc.score >= 0.5 for doc in results)

        # Verify the calls were made in the right order
        mock_cohere_client.generate_embeddings.assert_called_once_with([query])
        mock_qdrant_client.search.assert_called_once()
        mock_filtering_service.filter_by_score_threshold.assert_called()
        mock_filtering_service.rank_documents.assert_called()

    @pytest.mark.asyncio
    async def test_retrieval_with_filters(self):
        """Test retrieval with metadata filters"""
        # Create mocked clients
        mock_cohere_client = AsyncMock(spec=CohereClient)
        mock_qdrant_client = AsyncMock(spec=QdrantClient)
        mock_filtering_service = MagicMock(spec=FilteringService)

        # Mock responses
        mock_embedding_response = EmbeddingResponse(
            embeddings=[[0.5, 0.6, 0.7, 0.8]],
            texts_count=1
        )
        mock_cohere_client.generate_embeddings.return_value = mock_embedding_response

        mock_search_results = [
            RetrievedDocument(id="doc_1", payload={"author": "Smith", "category": "tech"}, score=0.9),
            RetrievedDocument(id="doc_2", payload={"author": "Johnson", "category": "science"}, score=0.8),
            RetrievedDocument(id="doc_3", payload={"author": "Smith", "category": "tech"}, score=0.7)
        ]
        mock_qdrant_client.search.return_value = mock_search_results

        # Mock filtering service to apply filters
        def mock_filter_by_metadata(docs, filters):
            if filters.get("author") == "Smith":
                return [doc for doc in docs if doc.payload.get("author") == "Smith"]
            return docs

        mock_filtering_service.filter_by_score_threshold.return_value = mock_search_results
        mock_filtering_service.filter_by_metadata.side_effect = mock_filter_by_metadata
        mock_filtering_service.rank_documents.return_value = mock_search_results

        service = RetrievalService(
            cohere_client=mock_cohere_client,
            qdrant_client=mock_qdrant_client,
            filtering_service=mock_filtering_service
        )

        # Test with filters
        results = await service.retrieve_documents(
            query="test query",
            top_k=5,
            score_threshold=0.6,
            filters={"author": "Smith"}
        )

        # Should only return documents by Smith with score >= 0.6
        assert len(results) == 2
        assert all(doc.payload["author"] == "Smith" for doc in results)
        assert all(doc.score >= 0.6 for doc in results)

    @pytest.mark.asyncio
    async def test_retrieval_validation_errors(self):
        """Test that validation errors are properly raised"""
        mock_cohere_client = AsyncMock(spec=CohereClient)
        mock_qdrant_client = AsyncMock(spec=QdrantClient)
        mock_filtering_service = MagicMock(spec=FilteringService)

        service = RetrievalService(
            cohere_client=mock_cohere_client,
            qdrant_client=mock_qdrant_client,
            filtering_service=mock_filtering_service
        )

        # Test empty query
        with pytest.raises(Exception):  # Should raise ValidationError
            await service.retrieve_documents(query="", top_k=5, score_threshold=0.5)

        # Test query too long
        with pytest.raises(Exception):  # Should raise ValidationError
            await service.retrieve_documents(
                query="a" * 1001,  # Exceeds 1000 character limit
                top_k=5,
                score_threshold=0.5
            )

        # Test invalid top_k
        with pytest.raises(Exception):  # Should raise ValidationError
            await service.retrieve_documents(
                query="test",
                top_k=0,  # Less than 1
                score_threshold=0.5
            )

        # Test invalid score_threshold
        with pytest.raises(Exception):  # Should raise ValidationError
            await service.retrieve_documents(
                query="test",
                top_k=5,
                score_threshold=1.5  # Greater than 1.0
            )

    @pytest.mark.asyncio
    async def test_retrieval_error_handling(self):
        """Test error handling in retrieval flow"""
        mock_cohere_client = AsyncMock(spec=CohereClient)
        mock_qdrant_client = AsyncMock(spec=QdrantClient)
        mock_filtering_service = MagicMock(spec=FilteringService)

        # Make cohere client raise an exception
        mock_cohere_client.generate_embeddings.side_effect = Exception("Cohere API error")

        service = RetrievalService(
            cohere_client=mock_cohere_client,
            qdrant_client=mock_qdrant_client,
            filtering_service=mock_filtering_service
        )

        # Should propagate the exception
        with pytest.raises(Exception, match="Cohere API error"):
            await service.retrieve_documents(
                query="test query",
                top_k=5,
                score_threshold=0.5
            )

    @pytest.mark.asyncio
    async def test_retrieval_with_circuit_breaker(self):
        """Test that retrieval works with circuit breaker"""
        mock_cohere_client = AsyncMock(spec=CohereClient)
        mock_qdrant_client = AsyncMock(spec=QdrantClient)
        mock_filtering_service = MagicMock(spec=FilteringService)

        # Mock successful responses
        mock_embedding_response = EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3]],
            texts_count=1
        )
        mock_cohere_client.generate_embeddings.return_value = mock_embedding_response

        mock_search_results = [
            RetrievedDocument(id="doc_1", payload={"text": "test"}, score=0.8)
        ]
        mock_qdrant_client.search.return_value = mock_search_results

        mock_filtering_service.filter_by_score_threshold.return_value = mock_search_results
        mock_filtering_service.rank_documents.return_value = mock_search_results

        service = RetrievalService(
            cohere_client=mock_cohere_client,
            qdrant_client=mock_qdrant_client,
            filtering_service=mock_filtering_service
        )

        # This should work fine with the circuit breaker in place
        results = await service.retrieve_documents(
            query="test query",
            top_k=5,
            score_threshold=0.5
        )

        assert len(results) == 1
        assert results[0].id == "doc_1"