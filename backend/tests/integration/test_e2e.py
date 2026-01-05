import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.models.request_models import QueryRequest


class TestEndToEnd:
    """End-to-end tests for the retrieval service"""

    def setup_method(self):
        self.client = TestClient(app)

    @pytest.mark.asyncio
    async def test_complete_retrieval_flow(self):
        """Test the complete retrieval flow from API request to response"""
        # Mock the external services to avoid actual API calls
        with patch('src.services.retrieval_service.CohereClient') as mock_cohere, \
             patch('src.services.retrieval_service.QdrantClient') as mock_qdrant, \
             patch('src.services.filtering_service.FilteringService') as mock_filtering:

            # Setup mock responses
            mock_cohere_instance = AsyncMock()
            mock_cohere_instance.generate_embeddings.return_value = AsyncMock()
            mock_cohere_instance.generate_embeddings.return_value.embeddings = [[0.1, 0.2, 0.3]]
            mock_cohere.return_value = mock_cohere_instance

            mock_qdrant_instance = AsyncMock()
            mock_qdrant_instance.search.return_value = []
            mock_qdrant.return_value = mock_qdrant_instance

            mock_filtering_instance = AsyncMock()
            mock_filtering_instance.filter_by_score_threshold.return_value = []
            mock_filtering_instance.filter_by_metadata.return_value = []
            mock_filtering_instance.rank_documents.return_value = []
            mock_filtering.return_value = mock_filtering_instance

            # Make the API request
            response = self.client.post(
                "/v1/retrieve",
                json={
                    "query": "test query for e2e test",
                    "top_k": 5,
                    "score_threshold": 0.5,
                    "filters": {"category": "science"}
                }
            )

            # Verify the response
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert "query" in data
            assert data["query"] == "test query for e2e test"

    @pytest.mark.asyncio
    async def test_retrieval_with_various_parameters(self):
        """Test retrieval with different parameter combinations"""
        with patch('src.services.retrieval_service.CohereClient') as mock_cohere, \
             patch('src.services.retrieval_service.QdrantClient') as mock_qdrant, \
             patch('src.services.filtering_service.FilteringService') as mock_filtering:

            # Setup mocks
            mock_cohere_instance = AsyncMock()
            mock_cohere_instance.generate_embeddings.return_value = AsyncMock()
            mock_cohere_instance.generate_embeddings.return_value.embeddings = [[0.1, 0.2, 0.3]]
            mock_cohere.return_value = mock_cohere_instance

            mock_qdrant_instance = AsyncMock()
            mock_qdrant_instance.search.return_value = []
            mock_qdrant.return_value = mock_qdrant_instance

            mock_filtering_instance = AsyncMock()
            mock_filtering_instance.filter_by_score_threshold.return_value = []
            mock_filtering_instance.filter_by_metadata.return_value = []
            mock_filtering_instance.rank_documents.return_value = []
            mock_filtering.return_value = mock_filtering_instance

            # Test with different parameters
            test_cases = [
                {"query": "short", "top_k": 1, "score_threshold": 0.1},
                {"query": "medium length query", "top_k": 10, "score_threshold": 0.8},
                {"query": "another test query", "top_k": 3, "score_threshold": 0.3, "filters": {"author": "test"}}
            ]

            for i, test_case in enumerate(test_cases):
                response = self.client.post("/v1/retrieve", json=test_case)
                assert response.status_code == 200, f"Test case {i+1} failed"
                data = response.json()
                assert "results" in data
                assert "query" in data

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_api_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Retrieval & Context Filtering Service" in data["message"]

    @pytest.mark.asyncio
    async def test_retrieval_with_empty_results(self):
        """Test retrieval when no results are found"""
        with patch('src.services.retrieval_service.CohereClient') as mock_cohere, \
             patch('src.services.retrieval_service.QdrantClient') as mock_qdrant, \
             patch('src.services.filtering_service.FilteringService') as mock_filtering:

            # Setup mocks to return empty results
            mock_cohere_instance = AsyncMock()
            mock_cohere_instance.generate_embeddings.return_value = AsyncMock()
            mock_cohere_instance.generate_embeddings.return_value.embeddings = [[0.1, 0.2, 0.3]]
            mock_cohere.return_value = mock_cohere_instance

            mock_qdrant_instance = AsyncMock()
            mock_qdrant_instance.search.return_value = []
            mock_qdrant.return_value = mock_qdrant_instance

            mock_filtering_instance = AsyncMock()
            mock_filtering_instance.filter_by_score_threshold.return_value = []
            mock_filtering_instance.filter_by_metadata.return_value = []
            mock_filtering_instance.rank_documents.return_value = []
            mock_filtering.return_value = mock_filtering_instance

            response = self.client.post(
                "/v1/retrieve",
                json={"query": "query with no results", "top_k": 5, "score_threshold": 0.9}
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) == 0

    @pytest.mark.asyncio
    async def test_retrieval_with_filters(self):
        """Test retrieval with various filter combinations"""
        with patch('src.services.retrieval_service.CohereClient') as mock_cohere, \
             patch('src.services.retrieval_service.QdrantClient') as mock_qdrant, \
             patch('src.services.filtering_service.FilteringService') as mock_filtering:

            # Setup mocks
            mock_cohere_instance = AsyncMock()
            mock_cohere_instance.generate_embeddings.return_value = AsyncMock()
            mock_cohere_instance.generate_embeddings.return_value.embeddings = [[0.1, 0.2, 0.3]]
            mock_cohere.return_value = mock_cohere_instance

            mock_qdrant_instance = AsyncMock()
            mock_qdrant_instance.search.return_value = []
            mock_qdrant.return_value = mock_qdrant_instance

            mock_filtering_instance = AsyncMock()
            mock_filtering_instance.filter_by_score_threshold.return_value = []
            mock_filtering_instance.filter_by_metadata.return_value = []
            mock_filtering_instance.rank_documents.return_value = []
            mock_filtering.return_value = mock_filtering_instance

            # Test different filter scenarios
            filter_test_cases = [
                {"category": "technology"},
                {"author": "john", "year": 2023},
                {"source": "arxiv", "category": "science", "year": 2024}
            ]

            for i, filters in enumerate(filter_test_cases):
                response = self.client.post(
                    "/v1/retrieve",
                    json={
                        "query": f"test query {i}",
                        "top_k": 5,
                        "score_threshold": 0.5,
                        "filters": filters
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert "results" in data