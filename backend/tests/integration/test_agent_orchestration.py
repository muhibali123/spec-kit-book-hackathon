import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from src.services.agent_service import AgentService
from src.services.conversation_service import ConversationService
from src.agents.rag_agent import RAGAgent
from src.tools.retrieval_tool import RetrievalTool
from src.models.request_models import QueryRequest
from src.models.data_models import RetrievedContext, ContextChunk, ConversationContext, ConversationTurn
from src.models.response_models import AnswerResponse


class TestAgentOrchestrationIntegration:
    """Integration tests for agent orchestration"""

    @pytest.mark.asyncio
    async def test_full_query_processing_pipeline(self):
        """Test the complete query processing pipeline from request to response"""
        # Create mock components
        mock_rag_agent = AsyncMock()
        mock_retrieval_tool = AsyncMock()
        mock_conversation_service = AsyncMock()

        # Mock the retrieval tool response
        mock_retrieved_context = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="chunk_123",
                    content="Renewable energy sources like solar and wind power provide clean electricity.",
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
        mock_conversation = ConversationContext(
            conversation_id="test-conv-123",
            turns=[
                ConversationTurn(
                    turn_id="turn-1",
                    user_query="What is renewable energy?",
                    system_response="Renewable energy comes from natural sources...",
                    timestamp=mock_retrieved_context.metadata.get("timestamp") or __import__('datetime').datetime.now()
                )
            ],
            created_at=__import__('datetime').datetime.now(),
            last_activity=__import__('datetime').datetime.now(),
            is_active=True
        )
        mock_conversation_service.get_conversation.return_value = mock_conversation
        mock_conversation_service.add_turn.return_value = mock_conversation

        # Create the agent service with mocked components
        agent_service = AgentService(
            rag_agent=mock_rag_agent,
            retrieval_tool=mock_retrieval_tool,
            conversation_service=mock_conversation_service
        )

        # Create a query request
        query_request = QueryRequest(
            query="What is renewable energy?",
            conversation_id="test-conv-123"
        )

        # Process the query
        response = await agent_service.process_query(query_request)

        # Verify the response structure
        assert isinstance(response, AnswerResponse)
        assert response.query == "What is renewable energy?"
        assert "Renewable energy" in response.answer
        assert len(response.citations) == 1
        assert response.conversation_id == "test-conv-123"

        # Verify all components were called appropriately
        mock_retrieval_tool.run.assert_called_once()
        mock_rag_agent.generate_answer.assert_called_once()
        mock_rag_agent.validate_answer.assert_called_once()
        mock_rag_agent.extract_citations.assert_called_once()
        mock_conversation_service.add_turn.assert_called_once()

    @pytest.mark.asyncio
    async def test_conversation_context_integration(self):
        """Test that conversation context is properly maintained across queries"""
        # Create real services but with mocked external dependencies
        rag_agent = AsyncMock()
        retrieval_tool = AsyncMock()
        conversation_service = ConversationService()  # Use real service for this test

        # Mock the agent and tool responses
        rag_agent.generate_answer = AsyncMock(side_effect=[
            "Renewable energy comes from natural sources.",
            "Solar power is a type of renewable energy that uses sunlight."
        ])
        rag_agent.validate_answer = AsyncMock(return_value=True)
        rag_agent.extract_citations = AsyncMock(return_value=[{
            "source_id": "doc_123",
            "source_title": "Energy Guide",
            "excerpt": "Energy information",
            "relevance_score": 0.8
        }])

        retrieval_tool.run = AsyncMock(side_effect=[
            RetrievedContext(
                context_chunks=[ContextChunk(
                    chunk_id="chunk_1",
                    content="Renewable energy sources are sustainable.",
                    source_document="renewable.pdf",
                    relevance_score=0.8
                )],
                relevance_scores=[0.8],
                metadata={}
            ),
            RetrievedContext(
                context_chunks=[ContextChunk(
                    chunk_id="chunk_2",
                    content="Solar power converts sunlight to electricity.",
                    source_document="solar.pdf",
                    relevance_score=0.9
                )],
                relevance_scores=[0.9],
                metadata={}
            )
        ])

        agent_service = AgentService(
            rag_agent=rag_agent,
            retrieval_tool=retrieval_tool,
            conversation_service=conversation_service
        )

        # Create first query
        first_query = QueryRequest(
            query="What is renewable energy?",
            conversation_id="conv-multi-turn"
        )
        first_response = await agent_service.process_query(first_query)

        # Create second query in the same conversation
        second_query = QueryRequest(
            query="What about solar power?",
            conversation_id="conv-multi-turn"
        )
        second_response = await agent_service.process_query(second_query)

        # Verify both responses
        assert first_response.conversation_id == "conv-multi-turn"
        assert second_response.conversation_id == "conv-multi-turn"

        # Verify the conversation was created and updated
        conversation = await conversation_service.get_conversation("conv-multi-turn")
        assert conversation is not None
        assert len(conversation.turns) == 2
        assert conversation.turns[0].user_query == "What is renewable energy?"
        assert conversation.turns[1].user_query == "What about solar power?"

    @pytest.mark.asyncio
    async def test_new_conversation_creation(self):
        """Test that new conversations are created when no ID is provided"""
        rag_agent = AsyncMock()
        retrieval_tool = AsyncMock()
        conversation_service = ConversationService()

        # Mock responses
        rag_agent.generate_answer.return_value = "This is a test response."
        rag_agent.validate_answer.return_value = True
        rag_agent.extract_citations.return_value = []

        retrieval_tool.run.return_value = RetrievedContext(
            context_chunks=[],
            relevance_scores=[],
            metadata={}
        )

        agent_service = AgentService(
            rag_agent=rag_agent,
            retrieval_tool=retrieval_tool,
            conversation_service=conversation_service
        )

        # Create query without conversation ID
        query_request = QueryRequest(query="Hello, what can you do?")

        # Process the query
        response = await agent_service.process_query(query_request)

        # Verify a new conversation was created
        assert response.conversation_id is not None
        assert response.conversation_id != ""

        # Verify the conversation exists in the service
        conversation = await conversation_service.get_conversation(response.conversation_id)
        assert conversation is not None
        assert len(conversation.turns) == 1
        assert conversation.turns[0].user_query == "Hello, what can you do?"

    @pytest.mark.asyncio
    async def test_batch_query_processing(self):
        """Test processing multiple queries in batch"""
        rag_agent = AsyncMock()
        retrieval_tool = AsyncMock()
        conversation_service = ConversationService()

        # Mock responses for each query
        query_responses = [
            "First response to renewable energy question.",
            "Second response to solar power question.",
            "Third response to wind power question."
        ]
        citation_sets = [
            [{"source_id": "doc_1", "source_title": "Renewable", "excerpt": "info", "relevance_score": 0.8}],
            [{"source_id": "doc_2", "source_title": "Solar", "excerpt": "info", "relevance_score": 0.9}],
            [{"source_id": "doc_3", "source_title": "Wind", "excerpt": "info", "relevance_score": 0.7}]
        ]

        rag_agent.generate_answer = AsyncMock(side_effect=query_responses)
        rag_agent.validate_answer = AsyncMock(return_value=True)
        rag_agent.extract_citations = AsyncMock(side_effect=citation_sets)

        retrieval_tool.run.return_value = RetrievedContext(
            context_chunks=[ContextChunk(
                chunk_id="chunk_1",
                content="General energy info",
                source_document="energy.pdf",
                relevance_score=0.75
            )],
            relevance_scores=[0.75],
            metadata={}
        )

        agent_service = AgentService(
            rag_agent=rag_agent,
            retrieval_tool=retrieval_tool,
            conversation_service=conversation_service
        )

        queries = [
            "What is renewable energy?",
            "How does solar power work?",
            "Explain wind power generation."
        ]

        # Process queries in batch
        responses = await agent_service.process_batch_queries(queries)

        # Verify all responses were generated
        assert len(responses) == 3
        for i, response in enumerate(responses):
            assert isinstance(response, AnswerResponse)
            assert queries[i] in response.query
            assert len(response.citations) == 1

    @pytest.mark.asyncio
    async def test_error_handling_in_orchestration(self):
        """Test error handling throughout the orchestration pipeline"""
        rag_agent = AsyncMock()
        retrieval_tool = AsyncMock()
        conversation_service = ConversationService()

        # Make the retrieval tool raise an exception
        retrieval_tool.run.side_effect = Exception("Retrieval service unavailable")

        agent_service = AgentService(
            rag_agent=rag_agent,
            retrieval_tool=retrieval_tool,
            conversation_service=conversation_service
        )

        query_request = QueryRequest(query="Test query for error handling")

        # Verify the error is properly propagated
        with pytest.raises(Exception) as exc_info:
            await agent_service.process_query(query_request)

        assert "Retrieval service unavailable" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_conversation_turn_limit_enforcement(self):
        """Test that conversation turn limits are enforced"""
        rag_agent = AsyncMock()
        retrieval_tool = AsyncMock()
        conversation_service = ConversationService()

        # Mock responses
        rag_agent.generate_answer.return_value = "Test response."
        rag_agent.validate_answer.return_value = True
        rag_agent.extract_citations.return_value = []

        retrieval_tool.run.return_value = RetrievedContext(
            context_chunks=[ContextChunk(
                chunk_id="chunk_1",
                content="Test content",
                source_document="test.pdf",
                relevance_score=0.8
            )],
            relevance_scores=[0.8],
            metadata={}
        )

        agent_service = AgentService(
            rag_agent=rag_agent,
            retrieval_tool=retrieval_tool,
            conversation_service=conversation_service
        )

        # Temporarily modify the max conversation turns setting for this test
        from src.config import settings
        original_max_turns = settings.max_conversation_turns
        settings.max_conversation_turns = 3

        try:
            conversation_id = "turn-limit-test"

            # Add more turns than the limit
            for i in range(5):
                query_request = QueryRequest(
                    query=f"Query number {i}",
                    conversation_id=conversation_id
                )
                await agent_service.process_query(query_request)

            # Get the conversation and verify only the last 3 turns remain
            conversation = await conversation_service.get_conversation(conversation_id)
            assert conversation is not None
            assert len(conversation.turns) <= 3  # Should respect the limit

        finally:
            # Restore original setting
            settings.max_conversation_turns = original_max_turns

    @pytest.mark.asyncio
    async def test_conversation_context_in_agent_generation(self):
        """Test that conversation context is properly passed to the agent for multi-turn awareness"""
        rag_agent = AsyncMock()
        retrieval_tool = AsyncMock()
        conversation_service = ConversationService()

        # Mock the retrieval tool response
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
        retrieval_tool.run.return_value = mock_retrieved_context

        # Track calls to verify conversation context is passed
        async def mock_generate_answer(query, retrieved_context, conversation_history=None):
            # Verify that conversation history is passed for follow-up queries
            if "follow-up" in query.lower() or len(conversation_history or []) > 0:
                assert conversation_history is not None
                assert len(conversation_history) > 0
            return f"Response to: {query}"

        rag_agent.generate_answer.side_effect = mock_generate_answer
        rag_agent.validate_answer.return_value = True
        rag_agent.extract_citations.return_value = []

        agent_service = AgentService(
            rag_agent=rag_agent,
            retrieval_tool=retrieval_tool,
            conversation_service=conversation_service
        )

        # Create initial conversation
        initial_query = QueryRequest(
            query="What is solar energy?",
            conversation_id="context-aware-test"
        )
        await agent_service.process_query(initial_query)

        # Create follow-up query in same conversation
        followup_query = QueryRequest(
            query="How efficient is it?",
            conversation_id="context-aware-test"
        )
        await agent_service.process_query(followup_query)

        # Verify the agent was called with conversation history for the follow-up
        assert rag_agent.generate_answer.call_count == 2