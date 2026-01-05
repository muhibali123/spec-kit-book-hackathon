import pytest
from unittest.mock import AsyncMock, Mock
from src.services.retrieval_service import RetrievalService
from src.clients.cohere_client import CohereClient
from src.clients.qdrant_client import QdrantClient
from src.services.filtering_service import FilteringService
from src.models.data_models import RetrievedDocument
from src.utils.exceptions import ValidationError


class TestRetrievalService:
    @pytest.mark.asyncio
    async def test_retrieval_service_initialization(self):
        """Test that RetrievalService initializes correctly with dependencies"""
        mock_cohere = Mock(spec=CohereClient)
        mock_qdrant = Mock(spec=QdrantClient)
        mock_filtering = Mock(spec=FilteringService)

        service = RetrievalService(
            cohere_client=mock_cohere,
            qdrant_client=mock_qdrant,
            filtering_service=mock_filtering
        )

        assert service.cohere_client == mock_cohere
        assert service.qdrant_client == mock_qdrant
        assert service.filtering_service == mock_filtering

    @pytest.mark.asyncio
    async def test_retrieve_documents_success(self):
        """Test successful document retrieval"""
        # Create mock dependencies
        mock_cohere = AsyncMock()
        mock_qdrant = AsyncMock()
        mock_filtering = Mock(spec=FilteringService)

        # Mock embedding response
        mock_embedding_response = Mock()
        mock_embedding_response.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere.generate_embeddings.return_value = mock_embedding_response

        # Mock search results
        mock_search_results = [
            RetrievedDocument(
                id="doc1",
                payload={"text": "test content", "source": "test.pdf"},
                score=0.9
            ),
            RetrievedDocument(
                id="doc2",
                payload={"text": "more content", "source": "test2.pdf"},
                score=0.7
            )
        ]
        mock_qdrant.search.return_value = mock_search_results

        # Mock filtering service methods
        mock_filtering.filter_by_score_threshold = AsyncMock(return_value=mock_search_results)
        mock_filtering.filter_by_metadata = AsyncMock(return_value=mock_search_results)
        mock_filtering.rank_documents = AsyncMock(return_value=mock_search_results)

        service = RetrievalService(
            cohere_client=mock_cohere,
            qdrant_client=mock_qdrant,
            filtering_service=mock_filtering
        )

        results = await service.retrieve_documents(
            query="test query",
            top_k=5,
            score_threshold=0.5
        )

        assert len(results) == 2
        assert results[0].id == "doc1"
        assert results[1].id == "doc2"

        # Verify that all steps were called
        mock_cohere.generate_embeddings.assert_called_once_with(["test query"])
        mock_qdrant.search.assert_called_once()
        mock_filtering.filter_by_score_threshold.assert_called_once()
        mock_filtering.rank_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_documents_with_filters(self):
        """Test document retrieval with filters applied"""
        mock_cohere = AsyncMock()
        mock_qdrant = AsyncMock()
        mock_filtering = Mock(spec=FilteringService)

        # Mock embedding response
        mock_embedding_response = Mock()
        mock_embedding_response.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere.generate_embeddings.return_value = mock_embedding_response

        # Mock search results
        mock_search_results = [
            RetrievedDocument(
                id="doc1",
                payload={"text": "test content", "source": "test.pdf", "category": "tech"},
                score=0.9
            )
        ]
        mock_qdrant.search.return_value = mock_search_results

        # Mock filtering service methods
        mock_filtering.filter_by_score_threshold = AsyncMock(return_value=mock_search_results)
        mock_filtering.filter_by_metadata = AsyncMock(return_value=mock_search_results)
        mock_filtering.rank_documents = AsyncMock(return_value=mock_search_results)

        service = RetrievalService(
            cohere_client=mock_cohere,
            qdrant_client=mock_qdrant,
            filtering_service=mock_filtering
        )

        results = await service.retrieve_documents(
            query="test query",
            top_k=5,
            score_threshold=0.5,
            filters={"category": "tech"}
        )

        assert len(results) == 1
        assert results[0].payload["category"] == "tech"

        # Verify that metadata filtering was called since filters were provided
        mock_filtering.filter_by_metadata.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_documents_validation_error_empty_query(self):
        """Test that validation error is raised for empty query"""
        mock_cohere = Mock(spec=CohereClient)
        mock_qdrant = Mock(spec=QdrantClient)
        mock_filtering = Mock(spec=FilteringService)

        service = RetrievalService(
            cohere_client=mock_cohere,
            qdrant_client=mock_qdrant,
            filtering_service=mock_filtering
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.retrieve_documents(
                query="",
                top_k=5,
                score_threshold=0.5
            )

        assert "Query cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retrieve_documents_validation_error_long_query(self):
        """Test that validation error is raised for query that is too long"""
        mock_cohere = Mock(spec=CohereClient)
        mock_qdrant = Mock(spec=QdrantClient)
        mock_filtering = Mock(spec=FilteringService)

        service = RetrievalService(
            cohere_client=mock_cohere,
            qdrant_client=mock_qdrant,
            filtering_service=mock_filtering
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.retrieve_documents(
                query="a" * 1001,  # Too long query
                top_k=5,
                score_threshold=0.5
            )

        assert "exceeds maximum of 1000 characters" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retrieve_documents_validation_error_invalid_top_k(self):
        """Test that validation error is raised for invalid top_k value"""
        mock_cohere = Mock(spec=CohereClient)
        mock_qdrant = Mock(spec=QdrantClient)
        mock_filtering = Mock(spec=FilteringService)

        service = RetrievalService(
            cohere_client=mock_cohere,
            qdrant_client=mock_qdrant,
            filtering_service=mock_filtering
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.retrieve_documents(
                query="test query",
                top_k=0,  # Invalid: less than 1
                score_threshold=0.5
            )

        assert "top_k must be between 1 and 100" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            await service.retrieve_documents(
                query="test query",
                top_k=101,  # Invalid: greater than 100
                score_threshold=0.5
            )

        assert "top_k must be between 1 and 100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retrieve_documents_validation_error_invalid_score_threshold(self):
        """Test that validation error is raised for invalid score_threshold value"""
        mock_cohere = Mock(spec=CohereClient)
        mock_qdrant = Mock(spec=QdrantClient)
        mock_filtering = Mock(spec=FilteringService)

        service = RetrievalService(
            cohere_client=mock_cohere,
            qdrant_client=mock_qdrant,
            filtering_service=mock_filtering
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.retrieve_documents(
                query="test query",
                top_k=5,
                score_threshold=-0.1  # Invalid: less than 0.0
            )

        assert "score_threshold must be between 0.0 and 1.0" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            await service.retrieve_documents(
                query="test query",
                top_k=5,
                score_threshold=1.1  # Invalid: greater than 1.0
            )

        assert "score_threshold must be between 0.0 and 1.0" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_preprocess_query(self):
        """Test query preprocessing functionality"""
        mock_cohere = Mock(spec=CohereClient)
        mock_qdrant = Mock(spec=QdrantClient)
        mock_filtering = Mock(spec=FilteringService)

        service = RetrievalService(
            cohere_client=mock_cohere,
            qdrant_client=mock_qdrant,
            filtering_service=mock_filtering
        )

        # Test normal query
        result = service._preprocess_query("  test   query  ")
        assert result == "test query"

        # Test query with special characters (should be removed)
        result = service._preprocess_query("test <query> {test}")
        assert result == "test query test"

    @pytest.mark.asyncio
    async def test_preprocess_query_empty(self):
        """Test that preprocessing raises error for empty query"""
        mock_cohere = Mock(spec=CohereClient)
        mock_qdrant = Mock(spec=QdrantClient)
        mock_filtering = Mock(spec=FilteringService)

        service = RetrievalService(
            cohere_client=mock_cohere,
            qdrant_client=mock_qdrant,
            filtering_service=mock_filtering
        )

        with pytest.raises(ValidationError) as exc_info:
            service._preprocess_query("")

        assert "Query cannot be empty" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            service._preprocess_query("   ")

        assert "Query cannot be empty" in str(exc_info.value)