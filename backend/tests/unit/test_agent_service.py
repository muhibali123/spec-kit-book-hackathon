import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from src.services.agent_service import AgentService
from src.services.conversation_service import ConversationService
from src.agents.rag_agent import RAGAgent
from src.tools.retrieval_tool import RetrievalTool
from src.models.request_models import QueryRequest
from src.models.response_models import AnswerResponse, Citation
from src.models.data_models import RetrievedContext, ContextChunk, ConversationContext, ConversationTurn
from src.config.settings import settings


class TestAgentService:
    """Test the AgentService class"""

    def test_agent_service_initialization(self):
        """Test that AgentService can be initialized with default components"""
        service = AgentService()

        assert service.rag_agent is not None
        assert service.retrieval_tool is not None
        assert service.conversation_service is not None

    def test_agent_service_initialization_with_custom_components(self):
        """Test that AgentService can be initialized with custom components"""
        mock_rag_agent = Mock()
        mock_retrieval_tool = Mock()
        mock_conversation_service = Mock()

        service = AgentService(
            rag_agent=mock_rag_agent,
            retrieval_tool=mock_retrieval_tool,
            conversation_service=mock_conversation_service
        )

        assert service.rag_agent == mock_rag_agent
        assert service.retrieval_tool == mock_retrieval_tool
        assert service.conversation_service == mock_conversation_service

    @pytest.mark.asyncio
    async def test_process_query_success(self):
        """Test successful query processing"""
        # Create mock components
        mock_rag_agent = AsyncMock()
        mock_retrieval_tool = AsyncMock()
        mock_conversation_service = AsyncMock()

        # Mock the retrieval tool response
        mock_retrieved_context = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="chunk_123",
                    content="Renewable energy provides clean electricity without emissions.",
                    source_document="renewable_energy.pdf",
                    relevance_score=0.85
                )
            ],
            relevance_scores=[0.85],
            metadata={}
        )
        mock_retrieval_tool.run.return_value = mock_retrieved_context

        # Mock the RAG agent responses
        mock_rag_agent.generate_answer.return_value = "Renewable energy comes from natural sources that are replenished faster than they are consumed."
        mock_rag_agent.validate_answer.return_value = True
        mock_rag_agent.extract_citations.return_value = [
            {
                "source_id": "doc_123",
                "source_title": "Renewable Energy Basics",
                "excerpt": "Renewable energy sources like solar and wind power provide clean electricity.",
                "relevance_score": 0.85
            }
        ]

        # Mock conversation service
        mock_conversation_service.get_conversation.return_value = None
        mock_conversation_service.create_conversation.return_value = ConversationContext(
            conversation_id="test-conv-123",
            turns=[],
            created_at=Mock(),
            last_activity=Mock(),
            is_active=True
        )

        service = AgentService(
            rag_agent=mock_rag_agent,
            retrieval_tool=mock_retrieval_tool,
            conversation_service=mock_conversation_service
        )

        # Create query request
        query_request = QueryRequest(
            query="What is renewable energy?",
            top_k=5,
            score_threshold=0.7
        )

        # Process the query
        response = await service.process_query(query_request)

        # Verify the response
        assert isinstance(response, AnswerResponse)
        assert response.query == "What is renewable energy?"
        assert "Renewable energy" in response.answer
        assert len(response.citations) == 1
        assert response.conversation_id is not None

        # Verify all components were called
        mock_retrieval_tool.run.assert_called_once()
        mock_rag_agent.generate_answer.assert_called_once()
        mock_rag_agent.validate_answer.assert_called_once()
        mock_rag_agent.extract_citations.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_query_with_existing_conversation(self):
        """Test query processing with existing conversation context"""
        mock_rag_agent = AsyncMock()
        mock_retrieval_tool = AsyncMock()
        mock_conversation_service = AsyncMock()

        # Mock retrieved context
        mock_retrieved_context = RetrievedContext(
            context_chunks=[ContextChunk(
                chunk_id="chunk_1",
                content="Solar energy information",
                source_document="solar.pdf",
                relevance_score=0.9
            )],
            relevance_scores=[0.9],
            metadata={}
        )
        mock_retrieval_tool.run.return_value = mock_retrieved_context

        # Mock RAG agent
        mock_rag_agent.generate_answer.return_value = "Solar power is a renewable energy source."
        mock_rag_agent.validate_answer.return_value = True
        mock_rag_agent.extract_citations.return_value = []

        # Mock conversation with history
        conversation = ConversationContext(
            conversation_id="existing-conv",
            turns=[
                ConversationTurn(
                    turn_id="turn-1",
                    user_query="What is renewable energy?",
                    system_response="Renewable energy comes from natural sources.",
                    timestamp=Mock()
                )
            ],
            created_at=Mock(),
            last_activity=Mock(),
            is_active=True
        )
        mock_conversation_service.get_conversation.return_value = conversation
        mock_conversation_service.add_turn.return_value = conversation

        service = AgentService(
            rag_agent=mock_rag_agent,
            retrieval_tool=mock_retrieval_tool,
            conversation_service=mock_conversation_service
        )

        query_request = QueryRequest(
            query="How about solar power?",
            conversation_id="existing-conv"
        )

        response = await service.process_query(query_request)

        # Verify response and that conversation was updated
        assert response.conversation_id == "existing-conv"
        mock_conversation_service.add_turn.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_query_answer_validation_failure(self):
        """Test query processing when answer validation fails"""
        mock_rag_agent = AsyncMock()
        mock_retrieval_tool = AsyncMock()
        mock_conversation_service = AsyncMock()

        # Mock retrieved context
        mock_retrieved_context = RetrievedContext(
            context_chunks=[ContextChunk(
                chunk_id="chunk_1",
                content="Test content",
                source_document="test.pdf",
                relevance_score=0.8
            )],
            relevance_scores=[0.8],
            metadata={}
        )
        mock_retrieval_tool.run.return_value = mock_retrieved_context

        # Mock RAG agent with validation failure
        mock_rag_agent.generate_answer.return_value = "This is an invalid answer not based on context."
        mock_rag_agent.validate_answer.return_value = False  # Validation fails
        mock_rag_agent.extract_citations.return_value = []

        mock_conversation_service.get_conversation.return_value = None

        service = AgentService(
            rag_agent=mock_rag_agent,
            retrieval_tool=mock_retrieval_tool,
            conversation_service=mock_conversation_service
        )

        query_request = QueryRequest(query="Test query for validation")

        response = await service.process_query(query_request)

        # Verify that when validation fails, a standard response is given
        assert "cannot provide a reliable answer" in response.answer.lower()

    @pytest.mark.asyncio
    async def test_validate_and_process_query_valid_input(self):
        """Test validation and processing of valid query"""
        mock_rag_agent = AsyncMock()
        mock_retrieval_tool = AsyncMock()
        mock_conversation_service = AsyncMock()

        # Mock responses
        mock_retrieved_context = RetrievedContext(
            context_chunks=[ContextChunk(
                chunk_id="chunk_1",
                content="Valid content",
                source_document="valid.pdf",
                relevance_score=0.8
            )],
            relevance_scores=[0.8],
            metadata={}
        )
        mock_retrieval_tool.run.return_value = mock_retrieved_context
        mock_rag_agent.generate_answer.return_value = "Valid response."
        mock_rag_agent.validate_answer.return_value = True
        mock_rag_agent.extract_citations.return_value = []

        service = AgentService(
            rag_agent=mock_rag_agent,
            retrieval_tool=mock_retrieval_tool,
            conversation_service=mock_conversation_service
        )

        query_request = QueryRequest(query="Valid query")

        response = await service.validate_and_process_query(query_request)

        assert isinstance(response, AnswerResponse)
        assert response.query == "Valid query"

    @pytest.mark.asyncio
    async def test_validate_and_process_query_empty_query(self):
        """Test validation fails for empty query"""
        service = AgentService()

        query_request = QueryRequest(query="")

        with pytest.raises(ValueError) as exc_info:
            await service.validate_and_process_query(query_request)

        assert "Query cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_and_process_query_whitespace_query(self):
        """Test validation fails for whitespace-only query"""
        service = AgentService()

        query_request = QueryRequest(query="   ")

        with pytest.raises(ValueError) as exc_info:
            await service.validate_and_process_query(query_request)

        assert "Query cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_and_process_query_too_long_query(self):
        """Test validation fails for query exceeding maximum length"""
        service = AgentService()

        # Create a query that exceeds the max length
        long_query = "a" * (settings.max_query_length + 1)
        query_request = QueryRequest(query=long_query)

        with pytest.raises(ValueError) as exc_info:
            await service.validate_and_process_query(query_request)

        assert "Query exceeds maximum length" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_batch_queries(self):
        """Test processing multiple queries in batch"""
        mock_rag_agent = AsyncMock()
        mock_retrieval_tool = AsyncMock()
        mock_conversation_service = AsyncMock()

        # Mock responses
        mock_retrieved_context = RetrievedContext(
            context_chunks=[ContextChunk(
                chunk_id="chunk_1",
                content="Test content",
                source_document="test.pdf",
                relevance_score=0.8
            )],
            relevance_scores=[0.8],
            metadata={}
        )
        mock_retrieval_tool.run.return_value = mock_retrieved_context
        mock_rag_agent.generate_answer = AsyncMock(side_effect=[
            "Response to query 1",
            "Response to query 2",
            "Response to query 3"
        ])
        mock_rag_agent.validate_answer.return_value = True
        mock_rag_agent.extract_citations.return_value = []

        service = AgentService(
            rag_agent=mock_rag_agent,
            retrieval_tool=mock_retrieval_tool,
            conversation_service=mock_conversation_service
        )

        queries = ["Query 1", "Query 2", "Query 3"]

        responses = await service.process_batch_queries(queries)

        assert len(responses) == 3
        for i, response in enumerate(responses):
            assert isinstance(response, AnswerResponse)
            assert f"Response to query {i+1}" in response.answer

    @pytest.mark.asyncio
    async def test_retrieve_context_internal_method(self):
        """Test the internal _retrieve_context method"""
        mock_retrieval_tool = AsyncMock()
        mock_retrieved_context = RetrievedContext(
            context_chunks=[ContextChunk(
                chunk_id="chunk_1",
                content="Test content",
                source_document="test.pdf",
                relevance_score=0.8
            )],
            relevance_scores=[0.8],
            metadata={}
        )
        mock_retrieval_tool.run.return_value = mock_retrieved_context

        service = AgentService(retrieval_tool=mock_retrieval_tool)

        query_request = QueryRequest(
            query="Test query",
            top_k=5,
            score_threshold=0.7,
            filters={"category": "test"}
        )

        retrieved_context = await service._retrieve_context(query_request)

        assert retrieved_context == mock_retrieved_context
        mock_retrieval_tool.run.assert_called_once_with(
            query="Test query",
            top_k=5,
            score_threshold=0.7,
            filters={"category": "test"}
        )

    @pytest.mark.asyncio
    async def test_citation_processing(self):
        """Test that citations are properly processed and converted"""
        mock_rag_agent = AsyncMock()
        mock_retrieval_tool = AsyncMock()
        mock_conversation_service = AsyncMock()

        # Mock retrieved context
        mock_retrieved_context = RetrievedContext(
            context_chunks=[ContextChunk(
                chunk_id="chunk_1",
                content="Test content",
                source_document="test.pdf",
                relevance_score=0.8
            )],
            relevance_scores=[0.8],
            metadata={}
        )
        mock_retrieval_tool.run.return_value = mock_retrieved_context

        # Mock RAG agent with detailed citations
        mock_rag_agent.generate_answer.return_value = "Answer based on context."
        mock_rag_agent.validate_answer.return_value = True
        mock_rag_agent.extract_citations.return_value = [
            {
                "source_id": "doc_123",
                "source_title": "Test Document",
                "excerpt": "This is a relevant excerpt",
                "page_number": 5,
                "section_reference": "Section 2.1",
                "relevance_score": 0.85
            }
        ]

        service = AgentService(
            rag_agent=mock_rag_agent,
            retrieval_tool=mock_retrieval_tool,
            conversation_service=mock_conversation_service
        )

        query_request = QueryRequest(query="Citation test")

        response = await service.process_query(query_request)

        # Verify citation was properly converted
        assert len(response.citations) == 1
        citation = response.citations[0]
        assert citation.source_id == "doc_123"
        assert citation.source_title == "Test Document"
        assert citation.excerpt == "This is a relevant excerpt"
        assert citation.page_number == 5
        assert citation.section_reference == "Section 2.1"
        assert citation.relevance_score == 0.85

    @pytest.mark.asyncio
    async def test_conversation_creation_for_new_queries(self):
        """Test that new conversations are created for queries without conversation ID"""
        mock_rag_agent = AsyncMock()
        mock_retrieval_tool = AsyncMock()
        mock_conversation_service = AsyncMock()

        # Mock responses
        mock_retrieved_context = RetrievedContext(
            context_chunks=[ContextChunk(
                chunk_id="chunk_1",
                content="Test content",
                source_document="test.pdf",
                relevance_score=0.8
            )],
            relevance_scores=[0.8],
            metadata={}
        )
        mock_retrieval_tool.run.return_value = mock_retrieved_context
        mock_rag_agent.generate_answer.return_value = "Test response."
        mock_rag_agent.validate_answer.return_value = True
        mock_rag_agent.extract_citations.return_value = []

        # Mock conversation creation
        created_conversation = ConversationContext(
            conversation_id="new-conv-123",
            turns=[],
            created_at=Mock(),
            last_activity=Mock(),
            is_active=True
        )
        mock_conversation_service.create_conversation.return_value = created_conversation

        service = AgentService(
            rag_agent=mock_rag_agent,
            retrieval_tool=mock_retrieval_tool,
            conversation_service=mock_conversation_service
        )

        query_request = QueryRequest(query="New conversation query")

        response = await service.process_query(query_request)

        # Verify a new conversation was created
        assert response.conversation_id == "new-conv-123"
        mock_conversation_service.create_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_propagation_from_components(self):
        """Test that errors from components are properly propagated"""
        mock_retrieval_tool = AsyncMock()
        mock_retrieval_tool.run.side_effect = Exception("Retrieval failed")

        service = AgentService(retrieval_tool=mock_retrieval_tool)

        query_request = QueryRequest(query="Error test query")

        with pytest.raises(Exception) as exc_info:
            await service.process_query(query_request)

        assert "Retrieval failed" in str(exc_info.value)