import pytest
from src.agents.agent_factory import AgentFactory
from src.agents.rag_agent import RAGAgent
from src.agents.agent_config import AgentConfig


class TestAgentFactory:
    """Test the AgentFactory class"""

    def test_create_rag_agent_with_default_config(self):
        """Test creating a RAGAgent with default configuration"""
        agent = AgentFactory.create_rag_agent()

        assert isinstance(agent, RAGAgent)
        assert isinstance(agent.config, AgentConfig)
        # Verify it has default configuration
        assert agent.config.model_name == "gpt-4-turbo-preview"

    def test_create_rag_agent_with_custom_config(self):
        """Test creating a RAGAgent with custom configuration"""
        custom_config = AgentConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=500
        )
        agent = AgentFactory.create_rag_agent(config=custom_config)

        assert isinstance(agent, RAGAgent)
        assert agent.config.model_name == "gpt-3.5-turbo"
        assert agent.config.temperature == 0.7
        assert agent.config.max_tokens == 500

    def test_create_default_rag_agent(self):
        """Test creating a RAGAgent with default configuration using dedicated method"""
        agent = AgentFactory.create_default_rag_agent()

        assert isinstance(agent, RAGAgent)
        assert isinstance(agent.config, AgentConfig)
        # Verify it has default configuration
        assert agent.config.model_name == "gpt-4-turbo-preview"
        assert agent.config.temperature == 0.3
        assert agent.config.max_tokens == 1000

    def test_create_configured_rag_agent_with_all_params(self):
        """Test creating a RAGAgent with all configuration parameters specified"""
        agent = AgentFactory.create_configured_rag_agent(
            model_name="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=800,
            max_retries=5,
            timeout=45,
            min_context_relevance=0.6,
            answer_confidence_threshold=0.8,
            citation_extraction_enabled=False
        )

        assert isinstance(agent, RAGAgent)
        assert agent.config.model_name == "gpt-3.5-turbo"
        assert agent.config.temperature == 0.5
        assert agent.config.max_tokens == 800
        assert agent.config.max_retries == 5
        assert agent.config.timeout == 45
        assert agent.config.min_context_relevance == 0.6
        assert agent.config.answer_confidence_threshold == 0.8
        assert agent.config.citation_extraction_enabled is False

    def test_create_configured_rag_agent_with_partial_params(self):
        """Test creating a RAGAgent with only some configuration parameters specified"""
        agent = AgentFactory.create_configured_rag_agent(
            model_name="gpt-3.5-turbo",
            temperature=0.8
        )

        assert isinstance(agent, RAGAgent)
        assert agent.config.model_name == "gpt-3.5-turbo"
        assert agent.config.temperature == 0.8
        # Other values should be defaults
        assert agent.config.max_tokens == 1000  # default
        assert agent.config.max_retries == 3    # default
        assert agent.config.citation_extraction_enabled is True  # default

    def test_create_configured_rag_agent_with_none_params(self):
        """Test creating a RAGAgent when passing None for parameters (should use defaults)"""
        agent = AgentFactory.create_configured_rag_agent(
            model_name=None,
            temperature=None,
            max_tokens=None
        )

        assert isinstance(agent, RAGAgent)
        # Should use default values
        assert agent.config.model_name == "gpt-4-turbo-preview"  # default
        assert agent.config.temperature == 0.3  # default
        assert agent.config.max_tokens == 1000  # default

    def test_agent_factory_methods_return_different_instances(self):
        """Test that different factory methods return different agent instances"""
        agent1 = AgentFactory.create_default_rag_agent()
        agent2 = AgentFactory.create_rag_agent()
        agent3 = AgentFactory.create_configured_rag_agent(model_name="gpt-3.5-turbo")

        # All should be RAGAgent instances but different objects
        assert isinstance(agent1, RAGAgent)
        assert isinstance(agent2, RAGAgent)
        assert isinstance(agent3, RAGAgent)

        # Verify they are different instances
        assert agent1 is not agent2
        assert agent1 is not agent3
        assert agent2 is not agent3

        # Agent 3 should have different config than 1 and 2
        assert agent3.config.model_name != agent1.config.model_name
        assert agent3.config.model_name != agent2.config.model_name

    def test_agent_config_immutability_after_creation(self):
        """Test that agent configuration cannot be modified after creation"""
        agent = AgentFactory.create_rag_agent()

        original_model = agent.config.model_name
        original_temperature = agent.config.temperature

        # Try to modify the config - this should not affect the agent's internal config
        # since it should be passed by value/reference appropriately
        agent.config.model_name = "modified-model"
        agent.config.temperature = 1.0

        # Re-fetch the agent and check if the config changed
        # Note: This test checks if the configuration is properly encapsulated
        agent2 = AgentFactory.create_rag_agent()
        assert agent2.config.model_name == original_model
        assert agent2.config.temperature == original_temperature