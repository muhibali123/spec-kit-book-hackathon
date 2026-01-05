import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from src.clients.retrieval_client import RetrievalClient
from src.models.data_models import RetrievedContext, ContextChunk


class TestRetrievalClient:
    """Test the RetrievalClient class"""

    def test_retrieval_client_initialization(self):
        """Test that RetrievalClient can be initialized with default parameters"""
        client = RetrievalClient()

        assert client.base_url is not None
        assert client.timeout == 30
        assert client.max_retries == 3
        assert client.retry_delay == 1.0

    def test_retrieval_client_initialization_with_custom_params(self):
        """Test that RetrievalClient can be initialized with custom parameters"""
        client = RetrievalClient(
            base_url="http://custom-retrieval-service:8000",
            timeout=60,
            max_retries=5,
            retry_delay=2.0
        )

        assert client.base_url == "http://custom-retrieval-service:8000"
        assert client.timeout == 60
        assert client.max_retries == 5
        assert client.retry_delay == 2.0

    @patch('httpx.AsyncClient')
    @patch('src.config.settings.settings')
    async def test_retrieve_context_success(self, mock_settings, mock_async_client_class):
        """Test successful context retrieval"""
        # Mock settings
        mock_settings.retrieval_service_url = "http://retrieval-service:8000"
        mock_settings.default_top_k = 5
        mock_settings.default_score_threshold = 0.5

        # Mock the AsyncClient
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "chunk_123",
                    "text": "Renewable energy provides clean electricity without emissions.",
                    "source": "renewable_energy.pdf",
                    "section": "Section 2.1",
                    "score": 0.85,
                    "metadata": {"page": 5}
                }
            ],
            "metadata": {"search_time": 0.2}
        }
        mock_client_instance.post.return_value = mock_response

        client = RetrievalClient()
        result = await client.retrieve_context(query="What is renewable energy?")

        # Verify the request was made correctly
        mock_client_instance.post.assert_called_once_with(
            "http://retrieval-service:8000/v1/retrieve",
            json={
                "query": "What is renewable energy?",
                "top_k": 5,
                "score_threshold": 0.5,
                "filters": {},
                "include_metadata": True
            },
            headers={"Content-Type": "application/json"}
        )

        # Verify the result
        assert isinstance(result, RetrievedContext)
        assert len(result.context_chunks) == 1
        assert result.context_chunks[0].chunk_id == "chunk_123"
        assert result.context_chunks[0].content == "Renewable energy provides clean electricity without emissions."
        assert result.context_chunks[0].source_document == "renewable_energy.pdf"
        assert result.context_chunks[0].relevance_score == 0.85
        assert result.metadata == {"search_time": 0.2}

    @patch('httpx.AsyncClient')
    @patch('src.config.settings.settings')
    async def test_retrieve_context_with_custom_params(self, mock_settings, mock_async_client_class):
        """Test context retrieval with custom parameters"""
        # Mock settings
        mock_settings.retrieval_service_url = "http://retrieval-service:8000"
        mock_settings.default_top_k = 5
        mock_settings.default_score_threshold = 0.5

        # Mock the AsyncClient
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "results": [],
            "metadata": {}
        }
        mock_client_instance.post.return_value = mock_response

        client = RetrievalClient()
        result = await client.retrieve_context(
            query="What is renewable energy?",
            top_k=10,
            score_threshold=0.7,
            filters={"category": "scientific"}
        )

        # Verify the request was made with custom parameters
        mock_client_instance.post.assert_called_once_with(
            "http://retrieval-service:8000/v1/retrieve",
            json={
                "query": "What is renewable energy?",
                "top_k": 10,
                "score_threshold": 0.7,
                "filters": {"category": "scientific"},
                "include_metadata": True
            },
            headers={"Content-Type": "application/json"}
        )

    @patch('httpx.AsyncClient')
    @patch('src.config.settings.settings')
    async def test_retrieve_context_http_error(self, mock_settings, mock_async_client_class):
        """Test context retrieval with HTTP error"""
        # Mock settings
        mock_settings.retrieval_service_url = "http://retrieval-service:8000"
        mock_settings.default_top_k = 5
        mock_settings.default_score_threshold = 0.5

        # Mock the AsyncClient to raise an HTTP error
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500)
        )
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_client_instance.post.return_value = mock_response

        client = RetrievalClient(max_retries=0)  # No retries for this test
        with pytest.raises(Exception) as exc_info:
            await client.retrieve_context(query="What is renewable energy?")

        assert "Retrieval service returned error 500" in str(exc_info.value)

    @patch('httpx.AsyncClient')
    @patch('src.config.settings.settings')
    async def test_retrieve_context_connection_error(self, mock_settings, mock_async_client_class):
        """Test context retrieval with connection error"""
        # Mock settings
        mock_settings.retrieval_service_url = "http://retrieval-service:8000"
        mock_settings.default_top_k = 5
        mock_settings.default_score_threshold = 0.5

        # Mock the AsyncClient to raise a connection error
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

        mock_client_instance.post.side_effect = httpx.RequestError("Connection failed", request=MagicMock())

        client = RetrievalClient(max_retries=0)  # No retries for this test
        with pytest.raises(Exception) as exc_info:
            await client.retrieve_context(query="What is renewable energy?")

        assert "Failed to connect to retrieval service" in str(exc_info.value)

    @patch('httpx.AsyncClient')
    @patch('src.config.settings.settings')
    async def test_health_check_success(self, mock_settings, mock_async_client_class):
        """Test successful health check"""
        # Mock settings
        mock_settings.retrieval_service_url = "http://retrieval-service:8000"

        # Mock the AsyncClient
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client_instance.get.return_value = mock_response

        client = RetrievalClient()
        result = await client.health_check()

        assert result is True
        mock_client_instance.get.assert_called_once_with("http://retrieval-service:8000/v1/health")

    @patch('httpx.AsyncClient')
    @patch('src.config.settings.settings')
    async def test_health_check_failure(self, mock_settings, mock_async_client_class):
        """Test failed health check"""
        # Mock settings
        mock_settings.retrieval_service_url = "http://retrieval-service:8000"

        # Mock the AsyncClient to simulate failure
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

        mock_client_instance.get.side_effect = Exception("Connection failed")

        client = RetrievalClient()
        result = await client.health_check()

        assert result is False

    @patch('src.clients.retrieval_client.RetrievalClient.retrieve_context')
    async def test_batch_retrieve_context(self, mock_retrieve_context):
        """Test batch retrieval of context"""
        # Mock the retrieve_context method to return different results for different queries
        async def mock_retrieve_side_effect(query, **kwargs):
            # Create mock results based on the query
            chunk = ContextChunk(
                chunk_id=f"chunk_{hash(query) % 1000}",
                content=f"Content for query: {query}",
                source_document="test.pdf",
                relevance_score=0.8
            )
            return RetrievedContext(
                context_chunks=[chunk],
                relevance_scores=[0.8],
                metadata={"query": query}
            )

        mock_retrieve_context.side_effect = mock_retrieve_side_effect

        client = RetrievalClient()
        queries = ["Query 1", "Query 2", "Query 3"]
        results = await client.batch_retrieve_context(queries)

        assert len(results) == 3
        assert all(isinstance(result, RetrievedContext) for result in results)
        mock_retrieve_context.call_count == 3  # Should be called once for each query

    @patch('httpx.AsyncClient')
    @patch('src.config.settings.settings')
    async def test_retrieve_context_retry_logic(self, mock_settings, mock_async_client_class):
        """Test that retry logic works correctly"""
        # Mock settings
        mock_settings.retrieval_service_url = "http://retrieval-service:8000"
        mock_settings.default_top_k = 5
        mock_settings.default_score_threshold = 0.5

        # Mock the AsyncClient to fail initially then succeed
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

        # First two calls will fail, third will succeed
        responses = [
            httpx.RequestError("Connection failed", request=MagicMock()),
            httpx.RequestError("Connection failed", request=MagicMock()),
        ]

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "results": [{"id": "chunk_123", "text": "Success after retries", "source": "doc.pdf", "score": 0.9}],
            "metadata": {}
        }

        # Set up the side_effect to raise errors for first 2 calls, then return success
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise httpx.RequestError("Connection failed", request=MagicMock())
            else:
                return mock_response

        mock_client_instance.post.side_effect = side_effect

        # Create client with 3 retries and short delay to speed up test
        client = RetrievalClient(max_retries=3, retry_delay=0.01)
        result = await client.retrieve_context(query="Test query after retries")

        assert result is not None
        assert len(result.context_chunks) == 1
        assert result.context_chunks[0].content == "Success after retries"
        assert call_count == 3  # Should have succeeded on the 3rd attempt


class TestRetrievalToolIntegration:
    """Test integration between RetrievalClient and RetrievalTool"""

    @patch('src.clients.retrieval_client.RetrievalClient.retrieve_context')
    async def test_retrieval_tool_uses_client(self, mock_retrieve_context):
        """Test that RetrievalTool properly uses RetrievalClient"""
        from src.tools.retrieval_tool import RetrievalTool
        from src.clients.retrieval_client import RetrievalClient

        # Mock the retrieve_context method
        mock_result = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="chunk_123",
                    content="Test content",
                    source_document="test.pdf",
                    relevance_score=0.8
                )
            ],
            relevance_scores=[0.8],
            metadata={}
        )
        mock_retrieve_context.return_value = mock_result

        # Create a retrieval client and tool
        client = RetrievalClient(base_url="http://test:8000")
        tool = RetrievalTool(retrieval_client=client)

        # Call the tool
        result = await tool.run(query="Test query", top_k=5)

        # Verify the client method was called
        mock_retrieve_context.assert_called_once_with(
            query="Test query",
            top_k=5,
            score_threshold=0.5,  # default from settings
            filters={}
        )
        assert result == mock_result