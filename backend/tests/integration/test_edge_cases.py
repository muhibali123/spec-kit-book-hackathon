import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app


class TestEdgeCases:
    """Edge case tests for the retrieval service"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_extremely_long_query_handling(self):
        """Test [US1] Handle extremely long queries that exceed token limits"""
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

            # Test with a query that exceeds the 1000 character limit
            very_long_query = "test " * 300  # This creates a query > 1500 characters

            response = self.client.post(
                "/v1/retrieve",
                json={"query": very_long_query, "top_k": 5, "score_threshold": 0.5}
            )

            # Should return a validation error
            assert response.status_code == 422
            assert "VALIDATION_ERROR" in response.json()["error_code"]

    def test_invalid_malformed_query_handling(self):
        """Test [US1] Handle invalid or malformed queries with appropriate error responses"""
        # Test with empty query
        response = self.client.post(
            "/v1/retrieve",
            json={"query": "", "top_k": 5, "score_threshold": 0.5}
        )
        assert response.status_code == 422

        # Test with only whitespace query
        response = self.client.post(
            "/v1/retrieve",
            json={"query": "   \t\n   ", "top_k": 5, "score_threshold": 0.5}
        )
        assert response.status_code == 422

        # Test with null query
        response = self.client.post(
            "/v1/retrieve",
            json={"query": None, "top_k": 5, "score_threshold": 0.5}
        )
        assert response.status_code == 422

        # Test with non-string query
        response = self.client.post(
            "/v1/retrieve",
            json={"query": 123, "top_k": 5, "score_threshold": 0.5}
        )
        assert response.status_code == 422

    def test_qdrant_unavailability_handling(self):
        """Test [US1] Handle Qdrant vector database unavailability gracefully"""
        with patch('src.services.retrieval_service.CohereClient') as mock_cohere, \
             patch('src.services.retrieval_service.QdrantClient') as mock_qdrant:

            # Setup cohere to work normally
            mock_cohere_instance = AsyncMock()
            mock_cohere_instance.generate_embeddings.return_value = AsyncMock()
            mock_cohere_instance.generate_embeddings.return_value.embeddings = [[0.1, 0.2, 0.3]]
            mock_cohere.return_value = mock_cohere_instance

            # Setup qdrant to raise an exception
            mock_qdrant_instance = AsyncMock()
            mock_qdrant_instance.search.side_effect = Exception("Qdrant connection failed")
            mock_qdrant.return_value = mock_qdrant_instance

            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 5, "score_threshold": 0.5}
            )

            # Should return a 502 error for Qdrant API error
            assert response.status_code == 502
            assert "QDRANT_API_ERROR" in response.json()["error_code"]

    def test_cohere_unavailability_handling(self):
        """Test [US1] Handle Cohere API temporary unavailability with fallbacks"""
        with patch('src.services.retrieval_service.CohereClient') as mock_cohere:

            # Setup cohere to raise an exception
            mock_cohere_instance = AsyncMock()
            mock_cohere_instance.generate_embeddings.side_effect = Exception("Cohere API unavailable")
            mock_cohere.return_value = mock_cohere_instance

            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 5, "score_threshold": 0.5}
            )

            # Should return a 502 error for Cohere API error
            assert response.status_code == 502
            assert "COHERE_API_ERROR" in response.json()["error_code"]

    def test_extreme_parameters_handling(self):
        """Test handling of extreme parameter values"""
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

            # Test with maximum allowed top_k
            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 100, "score_threshold": 0.5}
            )
            assert response.status_code == 200

            # Test with minimum allowed score_threshold
            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 5, "score_threshold": 0.0}
            )
            assert response.status_code == 200

            # Test with maximum allowed score_threshold
            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 5, "score_threshold": 1.0}
            )
            assert response.status_code == 200

    def test_out_of_range_parameters(self):
        """Test handling of out-of-range parameters"""
        # Test with top_k too low
        response = self.client.post(
            "/v1/retrieve",
            json={"query": "test query", "top_k": 0, "score_threshold": 0.5}
        )
        assert response.status_code == 422

        # Test with top_k too high
        response = self.client.post(
            "/v1/retrieve",
            json={"query": "test query", "top_k": 101, "score_threshold": 0.5}
        )
        assert response.status_code == 422

        # Test with negative score_threshold
        response = self.client.post(
            "/v1/retrieve",
            json={"query": "test query", "top_k": 5, "score_threshold": -0.1}
        )
        assert response.status_code == 422

        # Test with score_threshold too high
        response = self.client.post(
            "/v1/retrieve",
            json={"query": "test query", "top_k": 5, "score_threshold": 1.1}
        )
        assert response.status_code == 422

    def test_empty_filters_handling(self):
        """Test handling of empty or null filters"""
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

            # Test with null filters
            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 5, "score_threshold": 0.5, "filters": None}
            )
            assert response.status_code == 200

            # Test with empty filters
            response = self.client.post(
                "/v1/retrieve",
                json={"query": "test query", "top_k": 5, "score_threshold": 0.5, "filters": {}}
            )
            assert response.status_code == 200

    def test_special_characters_in_query(self):
        """Test handling of queries with special characters"""
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

            # Test with special characters
            special_queries = [
                "test query with <html> tags",
                "query with {brackets} and [square] brackets",
                "query with \"quotes\" and 'apostrophes'",
                "query with /slashes/ and \\backslashes\\",
                "query with @symbols #hashtags $money %percent ^carrots &ampersands"
            ]

            for query in special_queries:
                response = self.client.post(
                    "/v1/retrieve",
                    json={"query": query, "top_k": 3, "score_threshold": 0.5}
                )
                assert response.status_code == 200, f"Failed for query: {query}"

    def test_concurrent_requests_with_errors(self):
        """Test handling of multiple concurrent requests when some fail"""
        import threading
        import time

        with patch('src.services.retrieval_service.CohereClient') as mock_cohere, \
             patch('src.services.retrieval_service.QdrantClient') as mock_qdrant, \
             patch('src.services.filtering_service.FilteringService') as mock_filtering:

            # Setup mocks with some randomness for error simulation
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

            results = []

            def make_request(query_id):
                # Alternate between good and bad requests to test mixed scenarios
                if query_id % 3 == 0:  # Every third request will be invalid
                    response = self.client.post(
                        "/v1/retrieve",
                        json={"query": "", "top_k": 5, "score_threshold": 0.5}  # Invalid query
                    )
                else:
                    response = self.client.post(
                        "/v1/retrieve",
                        json={"query": f"valid query {query_id}", "top_k": 2, "score_threshold": 0.5}
                    )
                results.append((query_id, response.status_code))

            # Make concurrent requests
            threads = []
            for i in range(15):
                thread = threading.Thread(target=lambda q=i: make_request(q))
                threads.append(thread)
                thread.start()

            # Wait for all to complete
            for thread in threads:
                thread.join()

            # Verify we have results for all requests
            assert len(results) == 15
            # Check that invalid queries return 422 and valid ones return 200
            for query_id, status_code in results:
                if query_id % 3 == 0:
                    assert status_code == 422  # Invalid queries
                else:
                    assert status_code == 200  # Valid queries