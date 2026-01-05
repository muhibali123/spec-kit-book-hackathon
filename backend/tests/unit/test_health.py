import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from src.main import app


class TestHealthEndpoint:
    def test_health_endpoint_success(self, client):
        """Test that health endpoint returns correct response"""
        response = client.get("/v1/health")

        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "dependencies" in data
        assert isinstance(data["dependencies"], dict)
        assert "cohere_api" in data["dependencies"]
        assert "qdrant_db" in data["dependencies"]

        # The status should be either "healthy" or "unhealthy"
        assert data["status"] in ["healthy", "unhealthy"]

        # The timestamp should be a valid datetime string
        assert datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))

    def test_health_endpoint_structure(self, client):
        """Test that health endpoint returns correct structure"""
        response = client.get("/v1/health")

        assert response.status_code == 200

        data = response.json()

        # Verify all required fields are present
        required_fields = ["status", "timestamp", "dependencies"]
        for field in required_fields:
            assert field in data, f"Field {field} is missing from response"

        # Verify dependencies structure
        dependencies = data["dependencies"]
        assert isinstance(dependencies, dict)
        assert "cohere_api" in dependencies
        assert "qdrant_db" in dependencies
        assert isinstance(dependencies["cohere_api"], bool)
        assert isinstance(dependencies["qdrant_db"], bool)