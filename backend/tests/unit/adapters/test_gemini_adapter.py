"""
Unit tests for the Gemini LLM adapter.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.adapters.llm.gemini_adapter import GeminiAdapter
from src.adapters.llm.llm_adapter import LLMResponse


class TestGeminiAdapter:
    """Test suite for GeminiAdapter class."""

    def test_initialization_with_api_key(self):
        """Test that GeminiAdapter initializes correctly with API key."""
        adapter = GeminiAdapter(api_key="test-key", model_name="gemini-pro")

        assert adapter.api_key == "test-key"
        assert adapter.model_name == "gemini-pro"

    def test_initialization_with_env_variable(self, monkeypatch):
        """Test that GeminiAdapter uses environment variable for API key if not provided."""
        monkeypatch.setenv("GEMINI_API_KEY", "env-key")
        monkeypatch.setenv("GEMINI_MODEL", "gemini-test")

        adapter = GeminiAdapter()

        assert adapter.api_key == "env-key"
        assert adapter.model_name == "gemini-test"

    def test_initialization_without_api_key_raises_error(self):
        """Test that GeminiAdapter raises error when no API key is provided."""
        import os
        # Temporarily clear the environment variable if it exists
        original_key = os.environ.get("GEMINI_API_KEY")
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

        try:
            with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is required"):
                GeminiAdapter(api_key=None)
        finally:
            # Restore original environment variable if it existed
            if original_key is not None:
                os.environ["GEMINI_API_KEY"] = original_key

    @patch('src.adapters.llm.gemini_adapter.genai')
    @patch('src.adapters.llm.gemini_adapter.GenerativeModel')
    @pytest.mark.asyncio
    async def test_chat_completions_create_success(self, mock_generative_model, mock_genai):
        """Test successful chat completion creation."""
        # Mock the Gemini API components
        mock_model_instance = Mock()
        mock_chat = Mock()
        mock_response = Mock()

        # Set up the response content
        mock_content = Mock()
        mock_content.text = "This is a test response"
        mock_response.text = "This is a test response"
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].content = Mock()
        mock_response.candidates[0].content.parts = [Mock()]
        mock_response.candidates[0].content.parts[0].text = "This is a test response"

        mock_chat.send_message.return_value = mock_response
        mock_model_instance.start_chat.return_value = mock_chat
        mock_generative_model.return_value = mock_model_instance

        adapter = GeminiAdapter(api_key="test-key")

        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello, how are you?"}
        ]

        result = await adapter.chat_completions_create(
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )

        assert isinstance(result, LLMResponse)
        assert len(result.choices) > 0

    @patch('src.adapters.llm.gemini_adapter.genai')
    @patch('src.adapters.llm.gemini_adapter.GenerativeModel')
    @pytest.mark.asyncio
    async def test_chat_completions_create_with_error_handling(self, mock_generative_model, mock_genai):
        """Test chat completion creation with error handling."""
        # Mock the Gemini API to raise an exception
        mock_generative_model.side_effect = Exception("API Error")

        adapter = GeminiAdapter(api_key="test-key")

        messages = [
            {"role": "user", "content": "Hello"}
        ]

        result = await adapter.chat_completions_create(messages=messages)

        assert isinstance(result, LLMResponse)
        assert len(result.choices) > 0
        assert "Error calling Gemini API" in result.choices[0]['message']['content']

    @patch('src.adapters.llm.gemini_adapter.genai')
    @patch('src.adapters.llm.gemini_adapter.GenerativeModel')
    @pytest.mark.asyncio
    async def test_embeddings_create_basic(self, mock_generative_model, mock_genai):
        """Test embeddings creation (basic functionality)."""
        adapter = GeminiAdapter(api_key="test-key")

        result = await adapter.embeddings_create(input_text="test input")

        assert isinstance(result, LLMResponse)
        assert 'data' in result.to_dict()
        # Note: This is a placeholder implementation since Gemini doesn't have native embedding API