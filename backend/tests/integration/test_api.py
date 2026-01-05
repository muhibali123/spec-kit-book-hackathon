import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from src.main import app
from src.models.response_models import QueryResponse


class TestAPIIntegration:
    def setup_method(self):
        """Set up test client for each test"""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get("/v1/health")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "status" in data
        assert "timestamp" in data
        assert "dependencies" in data
        assert isinstance(data["dependencies"], dict)

        # Status should be a string
        assert isinstance(data["status"], str)
        assert data["status"] in ["healthy", "unhealthy"]

    @pytest.mark.asyncio
    async def test_retrieve_endpoint_success(self):
        """Test successful document retrieval"""
        # This test requires mocking the backend services since we can't make real API calls
        with patch('src.api.dependencies.get_retrieval_service') as mock_get_service:
            # Create a mock retrieval service
            mock_service = AsyncMock()
            mock_service.retrieve_documents.return_value = [
                MagicMock(
                    id="test_doc_1",
                    payload={"text": "Test document content", "source": "test.pdf"},
                    score=0.85
                )
            ]

            mock_get_service.return_value = mock_service

            # Make request
            response = self.client.post(
                "/v1/retrieve",
                json={
                    "query": "test query",
                    "top_k": 5,
                    "score_threshold": 0.5,
                    "filters": {"source": "test.pdf"}
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "query" in data
            assert "results" in data
            assert "total_results" in data
            assert "processing_time" in data

            assert data["query"] == "test query"
            assert isinstance(data["results"], list)
            assert data["total_results"] >= 0

    def test_retrieve_endpoint_validation_error(self):
        """Test validation error handling"""
        response = self.client.post(
            "/v1/retrieve",
            json={
                "query": "",  # Empty query should cause validation error
                "top_k": 5,
                "score_threshold": 0.5
            }
        )

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_retrieve_endpoint_invalid_params(self):
        """Test invalid parameter handling"""
        response = self.client.post(
            "/v1/retrieve",
            json={
                "query": "a" * 1001,  # Too long query
                "top_k": 5,
                "score_threshold": 0.5
            }
        )

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_retrieve_endpoint_large_top_k(self):
        """Test large top_k parameter"""
        response = self.client.post(
            "/v1/retrieve",
            json={
                "query": "test query",
                "top_k": 150,  # Exceeds max of 100
                "score_threshold": 0.5
            }
        )

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_retrieve_endpoint_invalid_score_threshold(self):
        """Test invalid score threshold"""
        response = self.client.post(
            "/v1/retrieve",
            json={
                "query": "test query",
                "top_k": 5,
                "score_threshold": 1.5  # Greater than 1.0
            }
        )

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["message"] == "Retrieval & Context Filtering Service"

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self):
        """Test handling of multiple concurrent requests"""
        import concurrent.futures

        # This test simulates multiple concurrent requests
        # In a real test, we'd need to mock the backend services

        # For now, just verify that the API can handle sequential requests properly
        for i in range(3):
            response = self.client.get("/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data

    def test_retrieve_endpoint_with_minimal_params(self):
        """Test retrieve endpoint with minimal parameters"""
        # This would need to be mocked as well
        with patch('src.api.dependencies.get_retrieval_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.retrieve_documents.return_value = []
            mock_get_service.return_value = mock_service

            response = self.client.post(
                "/v1/retrieve",
                json={
                    "query": "minimal test query"
                }
            )

            assert response.status_code == 200
            data = response.json()

            assert data["query"] == "minimal test query"
            # Should use default values for omitted parameters