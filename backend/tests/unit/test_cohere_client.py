import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from src.clients.cohere_client import CohereClient
from src.utils.exceptions import CohereAPIError


class TestCohereClient:
    def test_cohere_client_initialization(self):
        """Test that CohereClient initializes correctly"""
        client = CohereClient(api_key="test-key", model="test-model")

        assert client.model == "test-model"
        assert client.max_retries == 3  # default
        assert client.base_delay == 1.0  # default

    def test_cohere_client_initialization_with_custom_params(self):
        """Test that CohereClient initializes with custom parameters"""
        client = CohereClient(api_key="test-key", model="test-model", max_retries=5, base_delay=2.0)

        assert client.model == "test-model"
        assert client.max_retries == 5
        assert client.base_delay == 2.0

    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self):
        """Test successful embedding generation"""
        # Mock the cohere client response
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        with patch('src.clients.cohere_client.cohere.Client') as mock_cohere_class:
            mock_client_instance = Mock()
            mock_client_instance.embed.return_value = mock_response
            mock_cohere_class.return_value = mock_client_instance

            client = CohereClient(api_key="test-key")
            result = await client.generate_embeddings(["text1", "text2"])

            assert result.embeddings == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            assert result.texts_count == 2
            mock_client_instance.embed.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_embeddings_with_retry_success(self):
        """Test embedding generation with retry logic that eventually succeeds"""
        # Mock the cohere client to fail on first call and succeed on second
        mock_response = Mock()
        mock_response.embeddings = [[0.7, 0.8, 0.9]]

        with patch('src.clients.cohere_client.cohere.Client') as mock_cohere_class:
            mock_client_instance = Mock()
            mock_client_instance.embed.side_effect = [Exception("API Error"), mock_response]
            mock_cohere_class.return_value = mock_client_instance

            client = CohereClient(api_key="test-key", max_retries=3, base_delay=0.1)
            result = await client.generate_embeddings(["text1"])

            assert result.embeddings == [[0.7, 0.8, 0.9]]
            assert result.texts_count == 1
            # Should have been called twice (first failed, second succeeded)
            assert mock_client_instance.embed.call_count == 2

    @pytest.mark.asyncio
    async def test_generate_embeddings_with_retry_failure(self):
        """Test embedding generation with retry logic that eventually fails"""
        with patch('src.clients.cohere_client.cohere.Client') as mock_cohere_class:
            mock_client_instance = Mock()
            mock_client_instance.embed.side_effect = Exception("API Error")
            mock_cohere_class.return_value = mock_client_instance

            client = CohereClient(api_key="test-key", max_retries=2, base_delay=0.1)

            with pytest.raises(CohereAPIError):
                await client.generate_embeddings(["text1"])

            # Should have been called 3 times (1 initial + 2 retries)
            assert mock_client_instance.embed.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_embeddings_exception_propagation(self):
        """Test that exceptions are properly wrapped in CohereAPIError"""
        with patch('src.clients.cohere_client.cohere.Client') as mock_cohere_class:
            mock_client_instance = Mock()
            mock_client_instance.embed.side_effect = Exception("Network error")
            mock_cohere_class.return_value = mock_client_instance

            client = CohereClient(api_key="test-key")

            with pytest.raises(CohereAPIError) as exc_info:
                await client.generate_embeddings(["text1"])

            assert "Error calling Cohere API" in str(exc_info.value)