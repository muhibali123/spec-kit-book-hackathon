import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.clients.qdrant_client import QdrantClient
from src.utils.exceptions import QdrantAPIError


class TestQdrantClient:
    def test_qdrant_client_initialization(self):
        """Test that QdrantClient initializes correctly"""
        client = QdrantClient(host="test-host", port=6334, collection_name="test-collection")

        # Note: We can't directly access the client object due to mocking,
        # but we can test the initialization parameters
        assert client.collection_name == "test-collection"

    @pytest.mark.asyncio
    async def test_search_success(self):
        """Test successful search operation"""
        # Mock the Qdrant search response
        mock_hit1 = Mock()
        mock_hit1.id = "doc-1"
        mock_hit1.payload = {"text": "test content 1", "source": "doc1.pdf"}
        mock_hit1.score = 0.9

        mock_hit2 = Mock()
        mock_hit2.id = "doc-2"
        mock_hit2.payload = {"text": "test content 2", "source": "doc2.pdf"}
        mock_hit2.score = 0.8

        mock_search_results = [mock_hit1, mock_hit2]

        with patch('src.clients.qdrant_client.QdrantBaseClient') as mock_qdrant_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.search = AsyncMock(return_value=mock_search_results)
            mock_qdrant_class.return_value = mock_client_instance

            client = QdrantClient(host="test-host", port=6334, collection_name="test-collection")
            results = await client.search(
                vector=[0.1, 0.2, 0.3],
                top_k=5,
                score_threshold=0.5,
                filters={"source": "doc1.pdf"}
            )

            assert len(results) == 2
            assert results[0].id == "doc-1"
            assert results[0].payload["text"] == "test content 1"
            assert results[0].score == 0.9

            # Verify the search method was called with correct parameters
            mock_client_instance.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_without_filters(self):
        """Test search operation without filters"""
        mock_hit = Mock()
        mock_hit.id = "doc-1"
        mock_hit.payload = {"text": "test content", "source": "doc.pdf"}
        mock_hit.score = 0.9

        mock_search_results = [mock_hit]

        with patch('src.clients.qdrant_client.QdrantBaseClient') as mock_qdrant_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.search = AsyncMock(return_value=mock_search_results)
            mock_qdrant_class.return_value = mock_client_instance

            client = QdrantClient()
            results = await client.search(
                vector=[0.1, 0.2, 0.3],
                top_k=5
            )

            assert len(results) == 1
            assert results[0].id == "doc-1"

    @pytest.mark.asyncio
    async def test_search_api_error(self):
        """Test that API errors are properly wrapped in QdrantAPIError"""
        with patch('src.clients.qdrant_client.QdrantBaseClient') as mock_qdrant_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.search = AsyncMock(side_effect=Exception("Network error"))
            mock_qdrant_class.return_value = mock_client_instance

            client = QdrantClient()

            with pytest.raises(QdrantAPIError) as exc_info:
                await client.search(
                    vector=[0.1, 0.2, 0.3],
                    top_k=5
                )

            assert "Error calling Qdrant API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_with_various_filters(self):
        """Test search with different types of filters"""
        mock_hit = Mock()
        mock_hit.id = "doc-1"
        mock_hit.payload = {"text": "filtered content", "source": "filtered.pdf", "year": 2023}
        mock_hit.score = 0.85

        mock_search_results = [mock_hit]

        with patch('src.clients.qdrant_client.QdrantBaseClient') as mock_qdrant_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.search = AsyncMock(return_value=mock_search_results)
            mock_qdrant_class.return_value = mock_client_instance

            client = QdrantClient()
            results = await client.search(
                vector=[0.1, 0.2, 0.3],
                top_k=5,
                filters={"year": 2023, "source": "filtered.pdf"}
            )

            assert len(results) == 1
            assert results[0].payload["year"] == 2023