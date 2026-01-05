"""
Factory module for creating LLM adapters based on configuration.
"""
from typing import Union
from src.config.settings import settings
from .llm_adapter import LLMAdapter


def create_llm_adapter(provider: str = None) -> LLMAdapter:
    """
    Factory function to create the appropriate LLM adapter based on configuration.

    Args:
        provider: LLM provider to use. If None, uses the configured default.

    Returns:
        LLMAdapter instance for the specified provider
    """
    if provider is None:
        provider = settings.llm_provider.lower()

    if provider == "openrouter":
        # Validate that OpenRouter API key is available
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required when using OpenRouter provider")

        from .openrouter_adapter import OpenRouterAdapter
        # Use the specified OpenRouter model or default to qwen
        model_to_use = settings.openrouter_model if settings.openrouter_model else "qwen/qwen-2.5-7b-instruct"
        return OpenRouterAdapter(
            api_key=settings.openrouter_api_key,
            model_name=model_to_use
        )
    elif provider == "openai":
        # For backward compatibility, we'll create a separate OpenAI adapter
        # For now, we'll raise an error to indicate this needs to be implemented
        from .openai_adapter import OpenAIAdapter
        return OpenAIAdapter()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def get_default_llm_adapter() -> LLMAdapter:
    """
    Get the default LLM adapter based on the application settings.

    Returns:
        LLMAdapter instance configured with default settings
    """
    return create_llm_adapter()