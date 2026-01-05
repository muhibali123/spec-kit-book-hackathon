import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.utils.exceptions import (
    CohereAPIError,
    QdrantAPIError,
    ValidationError,
    ExternalServiceError
)


class TestErrorScenarios:
    """Integration tests for error handling scenarios"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_cohere_api_error_handling(self):
        """Test that Cohere API errors are properly handled and return 502"""
        # Mock the cohere client to raise an exception
        with patch('src.services.retrieval_service.CohereClient') as mock_cohere:
            mock_cohere_instance = AsyncMock()
            mock_cohere_instance.generate_embeddings.side_effect = CohereAPIError("API key invalid")
            mock_cohere.return_value = mock_cohere_instance

            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 5, "score_threshold": 0.5}
            )

            assert response.status_code == 502
            assert response.json()["error_code"] == "COHERE_API_ERROR"
            assert "details" in response.json()

    def test_qdrant_api_error_handling(self):
        """Test that Qdrant API errors are properly handled and return 502"""
        # Mock the qdrant client to raise an exception
        with patch('src.services.retrieval_service.QdrantClient') as mock_qdrant:
            mock_qdrant_instance = AsyncMock()
            mock_qdrant_instance.search.side_effect = QdrantAPIError("Connection failed")
            mock_qdrant.return_value = mock_qdrant_instance

            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 5, "score_threshold": 0.5}
            )

            assert response.status_code == 502
            assert response.json()["error_code"] == "QDRANT_API_ERROR"
            assert "details" in response.json()

    def test_validation_error_handling(self):
        """Test that validation errors are properly handled and return 422"""
        # Test with empty query
        response = self.client.post(
            "/v1/retrieve",
            json={"query": "", "top_k": 5, "score_threshold": 0.5}
        )

        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"

        # Test with query too long
        long_query = "test " * 300  # Should exceed 1000 character limit
        response = self.client.post(
            "/v1/retrieve",
            json={"query": long_query, "top_k": 5, "score_threshold": 0.5}
        )

        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"

        # Test with invalid top_k
        response = self.client.post(
            "/v1/retrieve",
            json={"query": "test query", "top_k": 0, "score_threshold": 0.5}
        )

        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"

        # Test with invalid score_threshold
        response = self.client.post(
            "/v1/retrieve",
            json={"query": "test query", "top_k": 5, "score_threshold": -0.5}
        )

        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"

    def test_external_service_error_handling(self):
        """Test that external service errors are properly handled"""
        # Mock the retrieval service to raise an external service error
        with patch('src.api.v1.endpoints.retrieval.RetrievalService') as mock_retrieval_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.retrieve_documents.side_effect = ExternalServiceError("Service temporarily unavailable")
            mock_retrieval_service.return_value = mock_service_instance

            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 5, "score_threshold": 0.5}
            )

            assert response.status_code == 503
            assert response.json()["error_code"] == "EXTERNAL_SERVICE_ERROR"

    def test_health_check_with_cohere_error(self):
        """Test health check when Cohere service is unavailable"""
        with patch('src.api.v1.endpoints.retrieval.CohereClient') as mock_cohere:
            mock_cohere_instance = AsyncMock()
            mock_cohere_instance.generate_embeddings.side_effect = CohereAPIError("API unavailable")
            mock_cohere.return_value = mock_cohere_instance

            response = self.client.get("/v1/health")

            # Health check should still work even if external services fail
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"  # The service itself is healthy, but external services may not be

    def test_health_check_with_qdrant_error(self):
        """Test health check when Qdrant service is unavailable"""
        with patch('src.api.v1.endpoints.retrieval.QdrantClient') as mock_qdrant:
            mock_qdrant_instance = AsyncMock()
            mock_qdrant_instance.search.side_effect = QdrantAPIError("Connection failed")
            mock_qdrant.return_value = mock_qdrant_instance

            response = self.client.get("/v1/health")

            # Health check should still work even if external services fail
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"  # The service itself is healthy, but external services may not be

    def test_request_validation_error(self):
        """Test handling of FastAPI request validation errors"""
        # Send request with missing required fields
        response = self.client.post(
            "/v1/retrieve",
            json={"invalid_field": "test"}  # Missing required query field
        )

        assert response.status_code == 422
        assert response.json()["error_code"] == "REQUEST_VALIDATION_ERROR"

    def test_unexpected_error_handling(self):
        """Test handling of unexpected errors"""
        with patch('src.api.v1.endpoints.retrieval.RetrievalService') as mock_retrieval_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.retrieve_documents.side_effect = RuntimeError("Unexpected error")
            mock_retrieval_service.return_value = mock_service_instance

            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 5, "score_threshold": 0.5}
            )

            assert response.status_code == 500
            assert response.json()["error_code"] == "INTERNAL_ERROR"
            assert response.json()["details"] == "An unexpected error occurred"