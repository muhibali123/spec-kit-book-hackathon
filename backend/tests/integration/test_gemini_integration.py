"""
Integration tests for the Gemini LLM adapter with the RAG agent.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.adapters.llm.gemini_adapter import GeminiAdapter
from src.adapters.llm.llm_adapter import LLMResponse
from src.agents.rag_agent import RAGAgent
from src.agents.agent_config import AgentConfig
from src.models.data_models import RetrievedContext, ContextChunk


class TestGeminiIntegration:
    """Integration tests for Gemini adapter with RAG agent."""

    @pytest.mark.asyncio
    async def test_rag_agent_with_gemini_adapter(self):
        """Test that RAG agent works with Gemini adapter."""
        # Create a mock Gemini adapter
        mock_adapter = Mock(spec=GeminiAdapter)

        # Mock the response for chat completions
        mock_response = Mock(spec=LLMResponse)
        mock_response.choices = [
            {
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': 'This is a test answer from Gemini'
                },
                'finish_reason': 'stop'
            }
        ]
        mock_response.to_dict = lambda: {
            'choices': mock_response.choices,
            'model': 'gemini-test',
            'object': 'chat.completion',
            'usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30}
        }

        mock_adapter.chat_completions_create = Mock(return_value=mock_response)

        # Create agent config for Gemini
        config = AgentConfig(
            llm_provider="gemini",
            model_name="gemini-test"
        )

        # Create RAG agent with the mock adapter
        agent = RAGAgent(config=config, llm_adapter=mock_adapter)

        # Create test context
        test_context = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="test-1",
                    content="This is test content for the RAG system.",
                    source_document="test_doc.pdf",
                    relevance_score=0.9
                )
            ],
            relevance_scores=[0.9]
        )

        # Test generate_answer
        result = await agent.generate_answer(
            query="What is this test about?",
            retrieved_context=test_context
        )

        assert "test answer from Gemini" in result
        mock_adapter.chat_completions_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_rag_agent_validation_with_gemini(self):
        """Test that RAG agent validation works with Gemini adapter."""
        # Create a mock Gemini adapter
        mock_adapter = Mock(spec=GeminiAdapter)

        # Mock the response for validation
        mock_response = Mock(spec=LLMResponse)
        mock_response.choices = [
            {
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': 'VALID'
                },
                'finish_reason': 'stop'
            }
        ]
        mock_response.to_dict = lambda: {
            'choices': mock_response.choices,
            'model': 'gemini-test',
            'object': 'chat.completion',
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }

        mock_adapter.chat_completions_create = Mock(return_value=mock_response)

        # Create agent config for Gemini
        config = AgentConfig(
            llm_provider="gemini",
            model_name="gemini-test"
        )

        # Create RAG agent with the mock adapter
        agent = RAGAgent(config=config, llm_adapter=mock_adapter)

        # Create test context
        test_context = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="test-1",
                    content="This is test content for the RAG system.",
                    source_document="test_doc.pdf",
                    relevance_score=0.9
                )
            ],
            relevance_scores=[0.9]
        )

        # Test validate_answer
        result = await agent.validate_answer(
            query="What is this test about?",
            answer="This is a test answer",
            retrieved_context=test_context
        )

        assert result is True
        mock_adapter.chat_completions_create.assert_called()

    @pytest.mark.asyncio
    async def test_rag_agent_citation_extraction_with_gemini(self):
        """Test that RAG agent citation extraction works with Gemini adapter."""
        # Create a mock Gemini adapter
        mock_adapter = Mock(spec=GeminiAdapter)

        # Mock the response for citation extraction
        mock_response = Mock(spec=LLMResponse)
        mock_response.choices = [
            {
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': '[{"source_id": "doc1", "source_title": "Test Document", "excerpt": "test content", "relevance_score": 0.9}]'
                },
                'finish_reason': 'stop'
            }
        ]
        mock_response.to_dict = lambda: {
            'choices': mock_response.choices,
            'model': 'gemini-test',
            'object': 'chat.completion',
            'usage': {'prompt_tokens': 10, 'completion_tokens': 30, 'total_tokens': 40}
        }

        mock_adapter.chat_completions_create = Mock(return_value=mock_response)

        # Create agent config for Gemini
        config = AgentConfig(
            llm_provider="gemini",
            model_name="gemini-test"
        )

        # Create RAG agent with the mock adapter
        agent = RAGAgent(config=config, llm_adapter=mock_adapter)

        # Create test context
        test_context = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="test-1",
                    content="This is test content for the RAG system.",
                    source_document="test_doc.pdf",
                    relevance_score=0.9
                )
            ],
            relevance_scores=[0.9]
        )

        # Test extract_citations
        result = await agent.extract_citations(
            answer="This is based on the test content.",
            retrieved_context=test_context
        )

        assert len(result) == 1
        assert result[0]['source_id'] == 'doc1'
        mock_adapter.chat_completions_create.assert_called()