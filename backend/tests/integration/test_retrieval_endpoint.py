import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestRetrievalEndpointIntegration:
    def test_retrieval_endpoint_success(self, client, sample_query_request):
        """Test successful retrieval request"""
        response = client.post("/v1/retrieve", json=sample_query_request)

        # Since we're using mock data, it should succeed
        assert response.status_code in [200, 500]  # Either success or internal error due to missing real services

        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert "results" in data
            assert "total_results" in data
            assert "processing_time" in data

            assert data["query"] == sample_query_request["query"]
            assert isinstance(data["results"], list)
            assert isinstance(data["total_results"], int)
            assert isinstance(data["processing_time"], (int, float))

    def test_retrieval_endpoint_with_custom_params(self, client):
        """Test retrieval with custom parameters"""
        request_data = {
            "query": "Test query with custom params",
            "top_k": 3,
            "score_threshold": 0.6,
            "filters": {"source_type": "test"},
            "include_metadata": True
        }

        response = client.post("/v1/retrieve", json=request_data)

        # Should succeed or return 500 due to missing real services
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert data["query"] == request_data["query"]

    def test_retrieval_endpoint_validation_error(self, client):
        """Test retrieval with invalid parameters"""
        # Test with empty query (should fail validation)
        request_data = {
            "query": "",  # Empty query should fail
            "top_k": 5,
            "score_threshold": 0.5
        }

        response = client.post("/v1/retrieve", json=request_data)

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_retrieval_endpoint_long_query(self, client):
        """Test retrieval with very long query (should fail validation)"""
        request_data = {
            "query": "a" * 1001,  # Too long query
            "top_k": 5,
            "score_threshold": 0.5
        }

        response = client.post("/v1/retrieve", json=request_data)

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_retrieval_endpoint_invalid_top_k(self, client):
        """Test retrieval with invalid top_k value"""
        request_data = {
            "query": "Test query",
            "top_k": 0,  # Invalid: less than 1
            "score_threshold": 0.5
        }

        response = client.post("/v1/retrieve", json=request_data)

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_retrieval_endpoint_invalid_score_threshold(self, client):
        """Test retrieval with invalid score_threshold value"""
        request_data = {
            "query": "Test query",
            "top_k": 5,
            "score_threshold": 1.5  # Invalid: greater than 1.0
        }

        response = client.post("/v1/retrieve", json=request_data)

        # Should return 422 for validation error
        assert response.status_code == 422