"""
Unit tests for the LLM adapter factory.
"""
import pytest
from unittest.mock import patch, Mock
from src.adapters.llm.adapter_factory import create_llm_adapter
from src.adapters.llm.gemini_adapter import GeminiAdapter
from src.adapters.llm.openai_adapter import OpenAIAdapter
from src.config.settings import Settings


class TestAdapterFactory:
    """Test suite for LLM adapter factory functions."""

    def test_create_gemini_adapter(self, monkeypatch):
        """Test creating a Gemini adapter."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_MODEL", "gemini-test")

        adapter = create_llm_adapter("gemini")

        assert isinstance(adapter, GeminiAdapter)
        assert adapter.model_name == "gemini-test"

    def test_create_gemini_adapter_with_settings(self, monkeypatch):
        """Test creating a Gemini adapter using settings."""
        # Mock settings
        with patch('src.adapters.llm.adapter_factory.settings') as mock_settings:
            mock_settings.llm_provider = "gemini"
            mock_settings.gemini_api_key = "test-key"
            mock_settings.gemini_model = "gemini-test"

            adapter = create_llm_adapter()

            assert isinstance(adapter, GeminiAdapter)

    def test_create_openai_adapter(self):
        """Test creating an OpenAI adapter."""
        # This test requires that OpenAI key is available or mocked
        with patch('src.adapters.llm.openai_adapter.settings') as mock_settings:
            mock_settings.openai_api_key = "test-key"
            mock_settings.openai_model = "gpt-test"

            adapter = create_llm_adapter("openai")

            assert isinstance(adapter, OpenAIAdapter)

    def test_create_unsupported_provider_raises_error(self):
        """Test that creating an unsupported provider raises an error."""
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            create_llm_adapter("unsupported_provider")

    def test_create_gemini_adapter_without_api_key_raises_error(self, monkeypatch):
        """Test that creating a Gemini adapter without API key raises an error."""
        # Temporarily clear the environment variable
        original_key = monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
            create_llm_adapter("gemini")

        # Restore if it was originally set
        if original_key:
            monkeypatch.setenv("GEMINI_API_KEY", original_key)