from typing import Optional
from src.agents.rag_agent import RAGAgent
from src.agents.agent_config import AgentConfig


class AgentFactory:
    """
    Factory class for creating and managing agent instances
    """

    @staticmethod
    def create_rag_agent(config: Optional[AgentConfig] = None) -> RAGAgent:
        """
        Create a RAGAgent instance with the specified configuration

        Args:
            config: Optional agent configuration. If not provided, uses default config.

        Returns:
            RAGAgent instance
        """
        return RAGAgent(config=config)

    @staticmethod
    def create_default_rag_agent() -> RAGAgent:
        """
        Create a RAGAgent instance with default configuration

        Returns:
            RAGAgent instance with default configuration
        """
        return RAGAgent(config=AgentConfig())

    @classmethod
    def create_configured_rag_agent(
        cls,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: Optional[int] = None,
        timeout: Optional[int] = None,
        min_context_relevance: Optional[float] = None,
        answer_confidence_threshold: Optional[float] = None,
        citation_extraction_enabled: Optional[bool] = None
    ) -> RAGAgent:
        """
        Create a RAGAgent instance with specific configuration parameters

        Args:
            model_name: OpenAI model to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            max_retries: Maximum number of retries
            timeout: Timeout for operations
            min_context_relevance: Minimum relevance for context
            answer_confidence_threshold: Minimum confidence for answers
            citation_extraction_enabled: Whether to extract citations

        Returns:
            RAGAgent instance with specified configuration
        """
        config_params = {}
        if model_name is not None:
            config_params["model_name"] = model_name
        if temperature is not None:
            config_params["temperature"] = temperature
        if max_tokens is not None:
            config_params["max_tokens"] = max_tokens
        if max_retries is not None:
            config_params["max_retries"] = max_retries
        if timeout is not None:
            config_params["timeout"] = timeout
        if min_context_relevance is not None:
            config_params["min_context_relevance"] = min_context_relevance
        if answer_confidence_threshold is not None:
            config_params["answer_confidence_threshold"] = answer_confidence_threshold
        if citation_extraction_enabled is not None:
            config_params["citation_extraction_enabled"] = citation_extraction_enabled

        config = AgentConfig(**config_params) if config_params else AgentConfig()
        return RAGAgent(config=config)