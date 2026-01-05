from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration settings
    """
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # LLM Provider Settings
    llm_provider: str = "openai"  # Can be "openai", "gemini", "openrouter", etc.

    # OpenAI Settings (for backward compatibility)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"

    # OpenRouter Settings
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "qwen/qwen-2.5-7b-instruct"


    # Cohere Settings
    cohere_api_key: str = ""
    cohere_model: str = "embed-multilingual-v2.0"

    # Qdrant Settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "documents"  # This will be overridden by environment variable
    qdrant_api_key: Optional[str] = None
    qdrant_url: Optional[str] = None

    # Module 04 (Retrieval Service) Settings
    retrieval_service_url: str = "http://localhost:8001"

    # Service Settings
    default_top_k: int = 5
    default_score_threshold: float = 0.5
    max_query_length: int = 1000
    max_top_k: int = 100

    # Conversation Settings
    conversation_expiry_hours: int = 2
    max_conversation_turns: int = 25

    # Rate Limiting
    rate_limit_per_minute: int = 30
    rate_limit_per_hour: int = 500

    # Logging Settings
    log_level: str = "DEBUG"
    log_json_format: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Create a singleton instance
settings = Settings()
