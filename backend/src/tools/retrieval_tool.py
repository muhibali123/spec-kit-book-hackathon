from typing import Any, Dict
from src.tools.base_tool import BaseTool
from src.clients.retrieval_client import RetrievalClient
from src.config.settings import settings


class RetrievalTool(BaseTool):
    """
    Tool for retrieving relevant context from the knowledge base
    """

    def __init__(self, retrieval_client: RetrievalClient = None):
        """
        Initialize the retrieval tool

        Args:
            retrieval_client: Optional retrieval client. If not provided, creates a new one.
        """
        self.retrieval_client = retrieval_client or RetrievalClient()

    @property
    def name(self) -> str:
        return "retrieval_tool"

    @property
    def description(self) -> str:
        return (
            "Retrieve relevant context from the knowledge base to answer user queries. "
            "Use this tool when you need to find information to answer a question. "
            "The tool takes a query string and optional parameters for filtering and result limits."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant documents"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                    "minimum": 1,
                    "maximum": 20
                },
                "score_threshold": {
                    "type": "number",
                    "description": "Minimum relevance score threshold (default: 0.5)",
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters to apply to the search"
                }
            },
            "required": ["query"]
        }

    async def run(self, **kwargs) -> Any:
        """
        Execute the retrieval tool

        Args:
            **kwargs: Tool parameters including query, top_k, score_threshold, and filters

        Returns:
            Retrieved context from the knowledge base
        """
        query = kwargs.get("query")
        if not query:
            raise ValueError("Query parameter is required for retrieval tool")

        # Validate query length
        if len(query.strip()) == 0:
            raise ValueError("Query parameter cannot be empty or whitespace only")

        if len(query) > 1000:  # Assuming max query length of 1000
            raise ValueError("Query parameter exceeds maximum length of 1000 characters")

        # Extract optional parameters
        top_k = kwargs.get("top_k", settings.default_top_k)
        score_threshold = kwargs.get("score_threshold", settings.default_score_threshold)
        filters = kwargs.get("filters", {})

        # Validate top_k parameter
        if top_k is not None:
            if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
                raise ValueError("top_k must be an integer between 1 and 20")

        # Validate score_threshold parameter
        if score_threshold is not None:
            if not isinstance(score_threshold, (int, float)) or score_threshold < 0.0 or score_threshold > 1.0:
                raise ValueError("score_threshold must be a number between 0.0 and 1.0")

        # Validate filters parameter
        if filters is not None and not isinstance(filters, dict):
            raise ValueError("filters must be a dictionary")

        # Perform the retrieval
        try:
            result = await self.retrieval_client.retrieve_context(
                query=query,
                top_k=top_k,
                score_threshold=score_threshold,
                filters=filters
            )
            return result
        except Exception as e:
            # Log the error and re-raise with more context
            raise Exception(f"Error in retrieval tool: {str(e)}")