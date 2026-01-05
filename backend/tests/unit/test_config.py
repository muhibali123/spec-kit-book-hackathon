import os
import pytest
from unittest.mock import patch
from src.config.settings import Settings


class TestSettings:
    def test_settings_default_values(self):
        """Test that settings have correct default values"""
        # Temporarily set required env var for testing
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            settings = Settings()

            assert settings.api_host == "0.0.0.0"
            assert settings.api_port == 8000
            assert settings.openai_model == "gpt-4-turbo-preview"
            assert settings.retrieval_service_url == "http://localhost:8001"
            assert settings.default_top_k == 5
            assert settings.default_score_threshold == 0.5
            assert settings.max_query_length == 1000
            assert settings.max_top_k == 20
            assert settings.conversation_expiry_hours == 2
            assert settings.max_conversation_turns == 25
            assert settings.rate_limit_per_minute == 30
            assert settings.rate_limit_per_hour == 500
            assert settings.log_level == "INFO"
            assert settings.log_json_format is True

    def test_settings_custom_values(self):
        """Test that settings can be overridden with environment variables"""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "API_HOST": "127.0.0.1",
            "API_PORT": "9000",
            "OPENAI_MODEL": "gpt-3.5-turbo",
            "RETRIEVAL_SERVICE_URL": "http://retrieval-service:8000",
            "DEFAULT_TOP_K": "10",
            "DEFAULT_SCORE_THRESHOLD": "0.7",
            "MAX_QUERY_LENGTH": "2000",
            "MAX_TOP_K": "15",
            "CONVERSATION_EXPIRY_HOURS": "4",
            "MAX_CONVERSATION_TURNS": "30",
            "RATE_LIMIT_PER_MINUTE": "50",
            "RATE_LIMIT_PER_HOUR": "1000",
            "LOG_LEVEL": "DEBUG",
            "LOG_JSON_FORMAT": "False"
        }):
            settings = Settings()

            assert settings.api_host == "127.0.0.1"
            assert settings.api_port == 9000
            assert settings.openai_model == "gpt-3.5-turbo"
            assert settings.retrieval_service_url == "http://retrieval-service:8000"
            assert settings.default_top_k == 10
            assert settings.default_score_threshold == 0.7
            assert settings.max_query_length == 2000
            assert settings.max_top_k == 15
            assert settings.conversation_expiry_hours == 4
            assert settings.max_conversation_turns == 30
            assert settings.rate_limit_per_minute == 50
            assert settings.rate_limit_per_hour == 1000
            assert settings.log_level == "DEBUG"
            assert settings.log_json_format is False

    def test_settings_required_fields(self):
        """Test that required fields must be provided"""
        # Test that OPENAI_API_KEY is required
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):  # Could be ValidationError or ValueError depending on Pydantic version
                Settings(_env_file=None)  # Don't load from .env file to test the requirement