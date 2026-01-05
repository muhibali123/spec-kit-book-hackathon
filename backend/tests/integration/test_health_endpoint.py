import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from src.main import app


class TestHealthEndpointIntegration:
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
        timestamp_str = data["timestamp"]
        # Remove the 'Z' and add '+00:00' for proper ISO format parsing
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
        datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

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

    def test_health_endpoint_method_not_allowed(self, client):
        """Test that health endpoint only allows GET method"""
        # Try POST method (should not be allowed)
        response = client.post("/v1/health", json={})
        assert response.status_code == 405  # Method not allowed

        # Try PUT method (should not be allowed)
        response = client.put("/v1/health", json={})
        assert response.status_code == 405  # Method not allowed

        # Try DELETE method (should not be allowed)
        response = client.delete("/v1/health")
        assert response.status_code == 405  # Method not allowed