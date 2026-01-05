import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.agents.base_agent import BaseAgent
from src.agents.rag_agent import RAGAgent
from src.agents.agent_config import AgentConfig
from src.models.data_models import RetrievedContext, ContextChunk


class TestBaseAgent:
    """Test the BaseAgent abstract class"""

    def test_base_agent_is_abstract(self):
        """Test that BaseAgent cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseAgent()


class TestRAGAgent:
    """Test the RAGAgent implementation"""

    def test_rag_agent_initialization(self):
        """Test that RAGAgent can be initialized with default config"""
        agent = RAGAgent()

        assert agent.config is not None
        assert isinstance(agent.config, AgentConfig)
        assert agent.client is not None

    def test_rag_agent_initialization_with_config(self):
        """Test that RAGAgent can be initialized with custom config"""
        config = AgentConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=500
        )
        agent = RAGAgent(config)

        assert agent.config.model_name == "gpt-3.5-turbo"
        assert agent.config.temperature == 0.5
        assert agent.config.max_tokens == 500

    @patch('src.agents.rag_agent.OpenAI')
    def test_generate_answer_success(self, mock_openai_class):
        """Test successful answer generation"""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "This is the generated answer."
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        agent = RAGAgent()

        # Create test data
        query = "What are the benefits of renewable energy?"
        chunk = ContextChunk(
            chunk_id="chunk_123",
            content="Renewable energy sources like solar and wind power provide clean electricity without emissions.",
            source_document="renewable_energy.pdf",
            relevance_score=0.85
        )
        retrieved_context = RetrievedContext(
            context_chunks=[chunk],
            relevance_scores=[0.85]
        )

        # Test the method
        import asyncio
        answer = asyncio.run(agent.generate_answer(query, retrieved_context))

        assert answer == "This is the generated answer."
        mock_client.chat.completions.create.assert_called_once()

    @patch('src.agents.rag_agent.OpenAI')
    def test_generate_answer_with_conversation_history(self, mock_openai_class):
        """Test answer generation with conversation history"""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "This is the follow-up answer based on context."
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        agent = RAGAgent()

        # Create test data
        query = "How does it compare to fossil fuels?"
        conversation_history = [
            {
                "user_query": "What is renewable energy?",
                "system_response": "Renewable energy comes from natural sources that are constantly replenished."
            }
        ]
        chunk = ContextChunk(
            chunk_id="chunk_123",
            content="Renewable energy sources produce significantly fewer emissions than fossil fuels.",
            source_document="comparison.pdf",
            relevance_score=0.90
        )
        retrieved_context = RetrievedContext(
            context_chunks=[chunk],
            relevance_scores=[0.90]
        )

        # Test the method
        import asyncio
        answer = asyncio.run(agent.generate_answer(query, retrieved_context, conversation_history))

        assert answer == "This is the follow-up answer based on context."
        # Verify that the call was made (the history should be included in the prompt)
        mock_client.chat.completions.create.assert_called_once()

    @patch('src.agents.rag_agent.OpenAI')
    def test_validate_answer_valid(self, mock_openai_class):
        """Test answer validation returns True for valid answers"""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "VALID"
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        agent = RAGAgent()

        # Create test data
        query = "What are the benefits of renewable energy?"
        answer = "Renewable energy provides clean electricity without emissions."
        chunk = ContextChunk(
            chunk_id="chunk_123",
            content="Renewable energy sources like solar and wind power provide clean electricity without emissions.",
            source_document="renewable_energy.pdf",
            relevance_score=0.85
        )
        retrieved_context = RetrievedContext(
            context_chunks=[chunk],
            relevance_scores=[0.85]
        )

        # Test the method
        import asyncio
        is_valid = asyncio.run(agent.validate_answer(query, answer, retrieved_context))

        assert is_valid is True

    @patch('src.agents.rag_agent.OpenAI')
    def test_validate_answer_invalid(self, mock_openai_class):
        """Test answer validation returns False for invalid answers"""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "INVALID"
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        agent = RAGAgent()

        # Create test data
        query = "What are the benefits of renewable energy?"
        answer = "Fossil fuels are better than renewable energy because they're more reliable."
        chunk = ContextChunk(
            chunk_id="chunk_123",
            content="Renewable energy sources like solar and wind power provide clean electricity without emissions.",
            source_document="renewable_energy.pdf",
            relevance_score=0.85
        )
        retrieved_context = RetrievedContext(
            context_chunks=[chunk],
            relevance_scores=[0.85]
        )

        # Test the method
        import asyncio
        is_valid = asyncio.run(agent.validate_answer(query, answer, retrieved_context))

        assert is_valid is False

    @patch('src.agents.rag_agent.OpenAI')
    def test_extract_citations_success(self, mock_openai_class):
        """Test successful citation extraction"""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = (
            '[{'
            '"source_id": "doc_123",'
            '"source_title": "Renewable Energy Benefits",'
            '"excerpt": "Renewable energy provides clean electricity",'
            '"page_number": 5,'
            '"section_reference": "Section 2.1",'
            '"relevance_score": 0.85'
            '}]'
        )
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        agent = RAGAgent()

        # Create test data
        answer = "Renewable energy provides clean electricity as mentioned in the document."
        chunk = ContextChunk(
            chunk_id="chunk_123",
            content="Renewable energy sources like solar and wind power provide clean electricity without emissions.",
            source_document="renewable_energy.pdf",
            relevance_score=0.85
        )
        retrieved_context = RetrievedContext(
            context_chunks=[chunk],
            relevance_scores=[0.85]
        )

        # Test the method
        import asyncio
        citations = asyncio.run(agent.extract_citations(answer, retrieved_context))

        assert len(citations) == 1
        assert citations[0]["source_id"] == "doc_123"
        assert citations[0]["source_title"] == "Renewable Energy Benefits"
        assert citations[0]["excerpt"] == "Renewable energy provides clean electricity"

    @patch('src.agents.rag_agent.OpenAI')
    def test_extract_citations_empty_response(self, mock_openai_class):
        """Test citation extraction with empty response"""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "[]"
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        agent = RAGAgent()

        # Create test data
        answer = "This is a general answer not based on specific documents."
        chunk = ContextChunk(
            chunk_id="chunk_123",
            content="Some context that wasn't used in the answer.",
            source_document="other.pdf",
            relevance_score=0.30
        )
        retrieved_context = RetrievedContext(
            context_chunks=[chunk],
            relevance_scores=[0.30]
        )

        # Test the method
        import asyncio
        citations = asyncio.run(agent.extract_citations(answer, retrieved_context))

        assert citations == []

    def test_format_context_for_llm(self):
        """Test formatting context for LLM consumption"""
        agent = RAGAgent()

        chunk1 = ContextChunk(
            chunk_id="chunk_123",
            content="Renewable energy provides clean electricity.",
            source_document="renewable_energy.pdf",
            source_section="Section 2.1",
            relevance_score=0.85
        )
        chunk2 = ContextChunk(
            chunk_id="chunk_456",
            content="Solar and wind are the most common renewable sources.",
            source_document="sources.pdf",
            relevance_score=0.75
        )
        retrieved_context = RetrievedContext(
            context_chunks=[chunk1, chunk2],
            relevance_scores=[0.85, 0.75]
        )

        formatted_context = agent._format_context_for_llm(retrieved_context)

        assert "Source: renewable_energy.pdf" in formatted_context
        assert "Section: Section 2.1" in formatted_context
        assert "Content: Renewable energy provides clean electricity." in formatted_context
        assert "Source: sources.pdf" in formatted_context
        assert "Content: Solar and wind are the most common renewable sources." in formatted_context

    def test_format_history_for_llm(self):
        """Test formatting conversation history for LLM consumption"""
        agent = RAGAgent()

        conversation_history = [
            {
                "user_query": "What is renewable energy?",
                "system_response": "Renewable energy comes from natural sources."
            },
            {
                "user_query": "What are examples?",
                "system_response": "Solar and wind are examples of renewable energy."
            }
        ]

        formatted_history = agent._format_history_for_llm(conversation_history)

        assert "Turn 1:" in formatted_history
        assert "User: What is renewable energy?" in formatted_history
        assert "Assistant: Renewable energy comes from natural sources." in formatted_history
        assert "Turn 2:" in formatted_history
        assert "User: What are examples?" in formatted_history
        assert "Assistant: Solar and wind are examples of renewable energy." in formatted_history


class TestAgentConfig:
    """Test the AgentConfig model"""

    def test_agent_config_default_values(self):
        """Test that AgentConfig has correct default values"""
        config = AgentConfig()

        assert config.model_name == "gpt-4-turbo-preview"
        assert config.temperature == 0.3
        assert config.max_tokens == 1000
        assert config.max_retries == 3
        assert config.timeout == 30
        assert config.min_context_relevance == 0.3
        assert config.answer_confidence_threshold == 0.7
        assert config.citation_extraction_enabled is True

    def test_agent_config_custom_values(self):
        """Test that AgentConfig accepts custom values"""
        config = AgentConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=500,
            max_retries=5,
            timeout=60,
            min_context_relevance=0.5,
            answer_confidence_threshold=0.8,
            citation_extraction_enabled=False
        )

        assert config.model_name == "gpt-3.5-turbo"
        assert config.temperature == 0.7
        assert config.max_tokens == 500
        assert config.max_retries == 5
        assert config.timeout == 60
        assert config.min_context_relevance == 0.5
        assert config.answer_confidence_threshold == 0.8
        assert config.citation_extraction_enabled is False

    def test_agent_config_temperature_validation(self):
        """Test AgentConfig temperature validation"""
        with pytest.raises(ValueError):
            AgentConfig(temperature=-0.1)  # min is 0.0

        with pytest.raises(ValueError):
            AgentConfig(temperature=2.1)  # max is 2.0

    def test_agent_config_max_tokens_validation(self):
        """Test AgentConfig max_tokens validation"""
        with pytest.raises(ValueError):
            AgentConfig(max_tokens=99)  # min is 100

        with pytest.raises(ValueError):
            AgentConfig(max_tokens=4001)  # max is 4000

    def test_agent_config_max_retries_validation(self):
        """Test AgentConfig max_retries validation"""
        with pytest.raises(ValueError):
            AgentConfig(max_retries=0)  # min is 1

        with pytest.raises(ValueError):
            AgentConfig(max_retries=11)  # max is 10

    def test_agent_config_timeout_validation(self):
        """Test AgentConfig timeout validation"""
        with pytest.raises(ValueError):
            AgentConfig(timeout=4)  # min is 5

        with pytest.raises(ValueError):
            AgentConfig(timeout=121)  # max is 120

    def test_agent_config_relevance_threshold_validation(self):
        """Test AgentConfig relevance threshold validation"""
        with pytest.raises(ValueError):
            AgentConfig(min_context_relevance=-0.1)  # min is 0.0

        with pytest.raises(ValueError):
            AgentConfig(min_context_relevance=1.1)  # max is 1.0

        with pytest.raises(ValueError):
            AgentConfig(answer_confidence_threshold=-0.1)  # min is 0.0

        with pytest.raises(ValueError):
            AgentConfig(answer_confidence_threshold=1.1)  # max is 1.0