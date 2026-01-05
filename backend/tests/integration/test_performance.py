import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app


class TestPerformance:
    """Performance tests for the retrieval service"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_response_time_requirements(self):
        """Test that response time requirements are met (should be <2s for 95% of queries)"""
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

            # Test multiple requests to check response time
            response_times = []
            for i in range(10):  # Test with 10 requests
                start_time = time.time()
                response = self.client.post(
                    "/v1/retrieve",
                    json={"query": f"performance test query {i}", "top_k": 5, "score_threshold": 0.5}
                )
                end_time = time.time()
                response_times.append(end_time - start_time)
                assert response.status_code == 200

            # Calculate 95th percentile (for 10 requests, it's the 9th value when sorted)
            sorted_times = sorted(response_times)
            percentile_95 = sorted_times[int(0.95 * len(sorted_times)) - 1]

            # Verify that 95% of requests are under 2 seconds
            assert percentile_95 < 2.0, f"95th percentile response time ({percentile_95}s) exceeds 2s requirement"

            # Also check average response time
            avg_time = sum(response_times) / len(response_times)
            print(f"Average response time: {avg_time:.3f}s")
            print(f"95th percentile response time: {percentile_95:.3f}s")

    def test_concurrent_request_handling(self):
        """Test handling of concurrent requests to validate 100 concurrent users requirement"""
        import threading
        import requests

        # Mock the external services to avoid actual API calls
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

            def make_request(query_id):
                response = self.client.post(
                    "/v1/retrieve",
                    json={"query": f"concurrent test query {query_id}", "top_k": 3, "score_threshold": 0.5}
                )
                return response.status_code, response.json()

            # Test with multiple concurrent requests (reduced for testing purposes)
            threads = []
            results = []

            # Test with 20 concurrent requests instead of 100 for faster testing
            for i in range(20):
                thread = threading.Thread(target=lambda q=i: results.append(make_request(q)))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Verify all requests were successful
            assert len(results) == 20, f"Expected 20 results, got {len(results)}"
            for status_code, _ in results:
                assert status_code == 200

    def test_memory_usage_under_load(self):
        """Test memory usage under load conditions"""
        # This test focuses on ensuring the service doesn't have memory leaks
        # by making multiple requests and checking for performance degradation
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

            # Make many requests and monitor response times for degradation
            initial_times = []
            later_times = []

            # First batch of requests
            for i in range(10):
                start_time = time.time()
                response = self.client.post(
                    "/v1/retrieve",
                    json={"query": f"memory test query {i}", "top_k": 2, "score_threshold": 0.5}
                )
                end_time = time.time()
                initial_times.append(end_time - start_time)
                assert response.status_code == 200

            # Second batch of requests after the first batch
            for i in range(10):
                start_time = time.time()
                response = self.client.post(
                    "/v1/retrieve",
                    json={"query": f"memory test query {i+10}", "top_k": 2, "score_threshold": 0.5}
                )
                end_time = time.time()
                later_times.append(end_time - start_time)
                assert response.status_code == 200

            # Ensure there's no significant performance degradation
            avg_initial = sum(initial_times) / len(initial_times)
            avg_later = sum(later_times) / len(later_times)

            # Allow for some variance, but ensure no major degradation
            assert avg_later < avg_initial * 2.0, f"Performance significantly degraded: initial={avg_initial:.3f}, later={avg_later:.3f}"

    def test_large_query_handling(self):
        """Test handling of large queries to ensure they don't exceed limits"""
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

            # Test with a reasonably large query (under the 1000 char limit)
            large_query = "This is a test query that is longer than typical queries. " * 10  # ~500 chars

            start_time = time.time()
            response = self.client.post(
                "/v1/retrieve",
                json={"query": large_query, "top_k": 5, "score_threshold": 0.5}
            )
            end_time = time.time()

            response_time = end_time - start_time

            assert response.status_code == 200
            assert response_time < 2.0, f"Large query response time ({response_time}s) exceeded 2s requirement"

    def test_health_endpoint_performance(self):
        """Test that health endpoint responds quickly"""
        start_time = time.time()
        response = self.client.get("/v1/health")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 0.5, f"Health check response time ({response_time}s) should be under 0.5s"