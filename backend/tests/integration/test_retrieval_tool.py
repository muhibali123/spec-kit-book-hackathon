import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.tools.retrieval_tool import RetrievalTool
from src.clients.retrieval_client import RetrievalClient
from src.models.data_models import RetrievedContext, ContextChunk


class TestRetrievalToolIntegration:
    """Integration tests for the RetrievalTool with real client interactions"""

    @pytest.mark.asyncio
    async def test_retrieval_tool_with_mocked_service(self):
        """Test RetrievalTool with a mocked retrieval service"""
        # Create a mock response that simulates the retrieval service
        mock_retrieved_context = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="chunk_123",
                    content="Renewable energy sources like solar and wind power provide clean electricity without emissions.",
                    source_document="renewable_energy.pdf",
                    source_section="Section 2.1",
                    metadata={"page": 5, "author": "Smith, J."},
                    relevance_score=0.85
                ),
                ContextChunk(
                    chunk_id="chunk_456",
                    content="Solar panels convert sunlight directly into electricity through photovoltaic cells.",
                    source_document="solar_technology.pdf",
                    source_section="Chapter 3",
                    metadata={"page": 12, "author": "Johnson, A."},
                    relevance_score=0.78
                )
            ],
            relevance_scores=[0.85, 0.78],
            metadata={"search_time": 0.234, "total_results": 2}
        )

        # Mock the retrieval client
        mock_client = AsyncMock()
        mock_client.retrieve_context = AsyncMock(return_value=mock_retrieved_context)

        # Create the tool with the mocked client
        tool = RetrievalTool(retrieval_client=mock_client)

        # Execute the tool
        result = await tool.run(
            query="What are renewable energy sources?",
            top_k=5,
            score_threshold=0.7,
            filters={"category": "environmental"}
        )

        # Verify the client was called with correct parameters
        mock_client.retrieve_context.assert_called_once_with(
            query="What are renewable energy sources?",
            top_k=5,
            score_threshold=0.7,
            filters={"category": "environmental"}
        )

        # Verify the result
        assert isinstance(result, RetrievedContext)
        assert len(result.context_chunks) == 2
        assert result.context_chunks[0].chunk_id == "chunk_123"
        assert result.context_chunks[0].source_document == "renewable_energy.pdf"
        assert result.context_chunks[0].relevance_score == 0.85
        assert result.metadata["search_time"] == 0.234

    @pytest.mark.asyncio
    async def test_retrieval_tool_end_to_end_with_real_client_structure(self):
        """Test RetrievalTool using a real client structure but mocked HTTP calls"""
        # Create a real RetrievalClient but mock its HTTP calls
        client = RetrievalClient(base_url="http://fake-retrieval-service:8000")

        # Mock the internal HTTP call
        with patch.object(client, 'retrieve_context') as mock_retrieve:
            expected_result = RetrievedContext(
                context_chunks=[
                    ContextChunk(
                        chunk_id="chunk_789",
                        content="Wind turbines generate electricity by converting kinetic energy from wind into mechanical power.",
                        source_document="wind_energy.pdf",
                        relevance_score=0.92
                    )
                ],
                relevance_scores=[0.92],
                metadata={"query_id": "test-query-123"}
            )
            mock_retrieve.return_value = expected_result

            # Create tool with the real client
            tool = RetrievalTool(retrieval_client=client)

            # Execute the tool
            result = await tool.run(
                query="How do wind turbines work?",
                top_k=3
            )

            # Verify the call was made
            mock_retrieve.assert_called_once_with(
                query="How do wind turbines work?",
                top_k=3,
                score_threshold=0.5,  # default
                filters={}
            )

            # Verify the result
            assert result == expected_result

    @pytest.mark.asyncio
    async def test_retrieval_tool_error_handling_integration(self):
        """Test that RetrievalTool properly handles errors from the client"""
        # Create a client that will raise an exception
        mock_client = AsyncMock()
        mock_client.retrieve_context.side_effect = Exception("Service unavailable")

        tool = RetrievalTool(retrieval_client=mock_client)

        # Verify that the tool properly propagates the error
        with pytest.raises(Exception) as exc_info:
            await tool.run(query="Test query")

        assert "Error in retrieval tool" in str(exc_info.value)
        assert "Service unavailable" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retrieval_tool_with_various_filter_combinations(self):
        """Test RetrievalTool with different filter combinations"""
        mock_retrieved_context = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="chunk_abc",
                    content="Advanced renewable technologies are being developed.",
                    source_document="tech_advances.pdf",
                    relevance_score=0.88
                )
            ],
            relevance_scores=[0.88],
            metadata={}
        )

        mock_client = AsyncMock()
        mock_client.retrieve_context = AsyncMock(return_value=mock_retrieved_context)

        tool = RetrievalTool(retrieval_client=mock_client)

        # Test with no filters
        result1 = await tool.run(query="renewable technology")
        mock_client.retrieve_context.assert_called_with(
            query="renewable technology",
            top_k=5,
            score_threshold=0.5,
            filters={}
        )

        # Test with simple filters
        result2 = await tool.run(
            query="renewable technology",
            filters={"type": "research", "year": 2023}
        )
        mock_client.retrieve_context.assert_called_with(
            query="renewable technology",
            top_k=5,
            score_threshold=0.5,
            filters={"type": "research", "year": 2023}
        )

        # Test with complex filters
        result3 = await tool.run(
            query="renewable technology",
            top_k=10,
            score_threshold=0.6,
            filters={"category": "scientific", "access": "public", "tags": ["renewable", "energy"]}
        )
        mock_client.retrieve_context.assert_called_with(
            query="renewable technology",
            top_k=10,
            score_threshold=0.6,
            filters={"category": "scientific", "access": "public", "tags": ["renewable", "energy"]}
        )

        # All calls should return the same mocked result
        assert result1 == result2 == result3 == mock_retrieved_context

    @pytest.mark.asyncio
    async def test_retrieval_tool_concurrent_calls(self):
        """Test that RetrievalTool can handle concurrent calls properly"""
        # Create different mock results for different queries
        def mock_retrieve_context(query, **kwargs):
            content = f"Content for query: {query}"
            chunk = ContextChunk(
                chunk_id=f"chunk_{hash(query) % 1000}",
                content=content,
                source_document="test_doc.pdf",
                relevance_score=0.75
            )
            return RetrievedContext(
                context_chunks=[chunk],
                relevance_scores=[0.75],
                metadata={"query": query}
            )

        mock_client = AsyncMock()
        mock_client.retrieve_context = AsyncMock(side_effect=mock_retrieve_context)

        tool = RetrievalTool(retrieval_client=mock_client)

        # Make multiple concurrent calls
        queries = ["query 1", "query 2", "query 3", "query 4", "query 5"]
        tasks = [tool.run(query=q) for q in queries]
        results = await asyncio.gather(*tasks)

        # Verify all calls were made
        assert len(results) == 5
        assert all(isinstance(r, RetrievedContext) for r in results)
        assert all(len(r.context_chunks) == 1 for r in results)

        # Verify each result corresponds to its query
        for i, result in enumerate(results):
            expected_content = f"Content for query: {queries[i]}"
            assert result.context_chunks[0].content == expected_content
            assert result.metadata["query"] == queries[i]

        # Verify all calls were made with correct parameters
        assert mock_client.retrieve_context.call_count == 5

    @pytest.mark.asyncio
    async def test_retrieval_tool_integration_with_tool_registry(self):
        """Test RetrievalTool integration with ToolRegistry"""
        from src.tools.tool_registry import ToolRegistry

        # Create a mock client for the tool
        mock_retrieved_context = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="registry_test",
                    content="Testing integration with tool registry",
                    source_document="registry_test.pdf",
                    relevance_score=0.90
                )
            ],
            relevance_scores=[0.90],
            metadata={"source": "registry_test"}
        )

        mock_client = AsyncMock()
        mock_client.retrieve_context = AsyncMock(return_value=mock_retrieved_context)

        # Create the tool
        tool = RetrievalTool(retrieval_client=mock_client)

        # Register the tool in the registry
        registry = ToolRegistry()
        registry.register_tool(tool)

        # Retrieve the tool from the registry
        retrieved_tool = registry.get_tool("retrieval_tool")
        assert retrieved_tool is not None
        assert retrieved_tool.name == "retrieval_tool"

        # Execute the retrieved tool
        result = await retrieved_tool.run(query="Registry integration test")

        # Verify the result
        assert isinstance(result, RetrievedContext)
        assert result.context_chunks[0].chunk_id == "registry_test"
        assert result.context_chunks[0].relevance_score == 0.90

        # Verify the client was called
        mock_client.retrieve_context.assert_called_once_with(
            query="Registry integration test",
            top_k=5,
            score_threshold=0.5,
            filters={}
        )