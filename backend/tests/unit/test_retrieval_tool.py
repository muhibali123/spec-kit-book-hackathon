import pytest
from unittest.mock import AsyncMock, Mock
from src.tools.retrieval_tool import RetrievalTool
from src.clients.retrieval_client import RetrievalClient
from src.models.data_models import RetrievedContext, ContextChunk


class TestRetrievalTool:
    """Test the RetrievalTool class"""

    def test_retrieval_tool_properties(self):
        """Test that RetrievalTool has correct properties"""
        tool = RetrievalTool()

        assert tool.name == "retrieval_tool"
        assert "Retrieve relevant context" in tool.description
        assert "query" in tool.parameters["properties"]
        assert tool.parameters["required"] == ["query"]

    def test_retrieval_tool_initialization_with_custom_client(self):
        """Test that RetrievalTool can be initialized with a custom retrieval client"""
        mock_client = Mock()
        tool = RetrievalTool(retrieval_client=mock_client)

        assert tool.retrieval_client == mock_client

    def test_retrieval_tool_initialization_default_client(self):
        """Test that RetrievalTool creates a default retrieval client if none provided"""
        tool = RetrievalTool()

        assert tool.retrieval_client is not None
        assert isinstance(tool.retrieval_client, RetrievalClient)

    async def test_run_tool_success(self):
        """Test successful execution of the retrieval tool"""
        # Create a mock retrieval client
        mock_client = AsyncMock()
        mock_result = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="chunk_123",
                    content="Test content for renewable energy",
                    source_document="renewable_energy.pdf",
                    relevance_score=0.85
                )
            ],
            relevance_scores=[0.85],
            metadata={"search_time": 0.2}
        )
        mock_client.retrieve_context.return_value = mock_result

        tool = RetrievalTool(retrieval_client=mock_client)

        # Run the tool
        result = await tool.run(query="What is renewable energy?")

        # Verify the client method was called correctly
        mock_client.retrieve_context.assert_called_once_with(
            query="What is renewable energy?",
            top_k=5,  # default from settings
            score_threshold=0.5,  # default from settings
            filters={}
        )

        assert result == mock_result

    async def test_run_tool_with_custom_params(self):
        """Test retrieval tool execution with custom parameters"""
        # Create a mock retrieval client
        mock_client = AsyncMock()
        mock_result = RetrievedContext(
            context_chunks=[],
            relevance_scores=[],
            metadata={}
        )
        mock_client.retrieve_context.return_value = mock_result

        tool = RetrievalTool(retrieval_client=mock_client)

        # Run the tool with custom parameters
        result = await tool.run(
            query="What is solar power?",
            top_k=10,
            score_threshold=0.7,
            filters={"category": "renewable", "year": 2023}
        )

        # Verify the client method was called with custom parameters
        mock_client.retrieve_context.assert_called_once_with(
            query="What is solar power?",
            top_k=10,
            score_threshold=0.7,
            filters={"category": "renewable", "year": 2023}
        )

    async def test_run_tool_missing_query(self):
        """Test that retrieval tool raises error when query is missing"""
        tool = RetrievalTool()

        with pytest.raises(ValueError) as exc_info:
            await tool.run()

        assert "Query parameter is required for retrieval tool" in str(exc_info.value)

    async def test_run_tool_empty_query(self):
        """Test that retrieval tool raises error when query is empty"""
        tool = RetrievalTool()

        with pytest.raises(ValueError) as exc_info:
            await tool.run(query="")

        assert "Query parameter is required for retrieval tool" in str(exc_info.value)

    async def test_run_tool_whitespace_only_query(self):
        """Test that retrieval tool raises error when query is whitespace only"""
        tool = RetrievalTool()

        with pytest.raises(ValueError) as exc_info:
            await tool.run(query="   ")

        assert "Query parameter cannot be empty or whitespace only" in str(exc_info.value)

    async def test_run_tool_long_query(self):
        """Test that retrieval tool raises error when query is too long"""
        tool = RetrievalTool()

        with pytest.raises(ValueError) as exc_info:
            await tool.run(query="a" * 1001)  # More than 1000 characters

        assert "Query parameter exceeds maximum length of 1000 characters" in str(exc_info.value)

    async def test_run_tool_invalid_top_k(self):
        """Test that retrieval tool raises error with invalid top_k parameter"""
        mock_client = AsyncMock()
        tool = RetrievalTool(retrieval_client=mock_client)

        # Test with top_k less than 1
        with pytest.raises(ValueError) as exc_info:
            await tool.run(query="Test query", top_k=0)

        assert "top_k must be an integer between 1 and 20" in str(exc_info.value)

        # Test with top_k greater than 20
        with pytest.raises(ValueError) as exc_info:
            await tool.run(query="Test query", top_k=21)

        assert "top_k must be an integer between 1 and 20" in str(exc_info.value)

        # Test with non-integer top_k
        with pytest.raises(ValueError) as exc_info:
            await tool.run(query="Test query", top_k="5")

        assert "top_k must be an integer between 1 and 20" in str(exc_info.value)

    async def test_run_tool_invalid_score_threshold(self):
        """Test that retrieval tool raises error with invalid score_threshold parameter"""
        mock_client = AsyncMock()
        tool = RetrievalTool(retrieval_client=mock_client)

        # Test with score_threshold less than 0.0
        with pytest.raises(ValueError) as exc_info:
            await tool.run(query="Test query", score_threshold=-0.1)

        assert "score_threshold must be a number between 0.0 and 1.0" in str(exc_info.value)

        # Test with score_threshold greater than 1.0
        with pytest.raises(ValueError) as exc_info:
            await tool.run(query="Test query", score_threshold=1.1)

        assert "score_threshold must be a number between 0.0 and 1.0" in str(exc_info.value)

        # Test with non-numeric score_threshold
        with pytest.raises(ValueError) as exc_info:
            await tool.run(query="Test query", score_threshold="0.5")

        assert "score_threshold must be a number between 0.0 and 1.0" in str(exc_info.value)

    async def test_run_tool_invalid_filters(self):
        """Test that retrieval tool raises error with invalid filters parameter"""
        mock_client = AsyncMock()
        tool = RetrievalTool(retrieval_client=mock_client)

        # Test with non-dict filters
        with pytest.raises(ValueError) as exc_info:
            await tool.run(query="Test query", filters="invalid")

        assert "filters must be a dictionary" in str(exc_info.value)

    async def test_run_tool_client_error_propagation(self):
        """Test that retrieval tool properly propagates client errors"""
        mock_client = AsyncMock()
        mock_client.retrieve_context.side_effect = Exception("Client error")
        tool = RetrievalTool(retrieval_client=mock_client)

        with pytest.raises(Exception) as exc_info:
            await tool.run(query="Test query")

        assert "Error in retrieval tool" in str(exc_info.value)
        assert "Client error" in str(exc_info.value)

    def test_parameters_schema_correctness(self):
        """Test that the parameters schema is correctly structured"""
        tool = RetrievalTool()

        params = tool.parameters
        assert params["type"] == "object"
        assert "properties" in params
        assert "required" in params

        # Check individual properties
        properties = params["properties"]
        assert "query" in properties
        assert properties["query"]["type"] == "string"
        assert "top_k" in properties
        assert properties["top_k"]["type"] == "integer"
        assert "score_threshold" in properties
        assert properties["score_threshold"]["type"] == "number"
        assert "filters" in properties
        assert properties["filters"]["type"] == "object"

        # Check required fields
        assert "query" in params["required"]