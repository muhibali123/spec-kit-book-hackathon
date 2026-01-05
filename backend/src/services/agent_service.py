import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from src.agents.rag_agent import RAGAgent
from src.tools.retrieval_tool import RetrievalTool
from src.models.request_models import QueryRequest
from src.models.response_models import AnswerResponse, Citation
from src.models.data_models import RetrievedContext, ConversationContext, ConversationTurn
from src.services.conversation_service import ConversationService
from src.config.settings import settings


class AgentService:
    """
    Service class for orchestrating agent operations including retrieval, generation,
    and response formatting for the RAG system.
    """

    def __init__(
        self,
        rag_agent: RAGAgent = None,
        retrieval_tool: RetrievalTool = None,
        conversation_service: ConversationService = None
    ):
        """
        Initialize the AgentService

        Args:
            rag_agent: Optional RAG agent instance. If not provided, creates a default one.
            retrieval_tool: Optional retrieval tool instance. If not provided, creates a default one.
            conversation_service: Optional conversation service instance. If not provided, creates a default one.
        """
        # Use provided agent or create a default one based on configuration
        if rag_agent is not None:
            self.rag_agent = rag_agent
        else:
            # Create agent based on settings
            from src.config.settings import settings
            from src.agents.agent_config import AgentConfig

            # Create agent config based on the configured LLM provider
            agent_config = AgentConfig(
                llm_provider=settings.llm_provider,
                model_name=settings.openai_model if settings.llm_provider == "openai" else settings.gemini_model
            )

            self.rag_agent = RAGAgent(config=agent_config)

        self.retrieval_tool = retrieval_tool or RetrievalTool()
        self.conversation_service = conversation_service or ConversationService()

    async def process_query(self, query_request: QueryRequest) -> AnswerResponse:
        """
        Process a user query through the RAG pipeline

        Args:
            query_request: The query request containing the user's query and parameters

        Returns:
            AnswerResponse containing the generated answer with citations
        """
        start_time = datetime.now()

        # Get conversation context if provided
        conversation_context = None
        if query_request.conversation_id:
            conversation_context = await self.conversation_service.get_conversation(
                query_request.conversation_id
            )

        # Retrieve relevant context from knowledge base
        retrieved_context = await self._retrieve_context(query_request)

        # Get conversation history for context
        conversation_history = []
        if conversation_context:
            conversation_history = [
                {
                    "user_query": turn.user_query,
                    "system_response": turn.system_response
                }
                for turn in conversation_context.turns[-5:]  # Use last 5 turns for context
            ]

        # Generate answer using the RAG agent
        generated_answer = await self.rag_agent.generate_answer(
            query=query_request.query,
            retrieved_context=retrieved_context,
            conversation_history=conversation_history
        )

        # Validate the generated answer
        is_valid = await self.rag_agent.validate_answer(
            query=query_request.query,
            answer=generated_answer,
            retrieved_context=retrieved_context
        )

        # Note: The validation now always returns True to prevent throwing away valid answers
        # The validation is used for logging and metrics purposes only

        # Extract citations from the generated answer
        citations = await self.rag_agent.extract_citations(
            answer=generated_answer,
            retrieved_context=retrieved_context
        )

        # Create citation objects from the extracted data
        citation_objects = []
        for citation_data in citations:
            citation_obj = Citation(
                source_id=citation_data.get("source_id", ""),
                source_title=citation_data.get("source_title", ""),
                excerpt=citation_data.get("excerpt", ""),
                page_number=citation_data.get("page_number"),
                section_reference=citation_data.get("section_reference"),
                relevance_score=citation_data.get("relevance_score", 0.0)
            )
            citation_objects.append(citation_obj)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Determine conversation ID
        conversation_id = query_request.conversation_id or str(uuid.uuid4())

        # Create the response
        response = AnswerResponse(
            query=query_request.query,
            answer=generated_answer,
            citations=citation_objects,
            conversation_id=conversation_id,
            confidence_score=0.85,  # Placeholder - in a real implementation this would come from the agent
            processing_time=processing_time
        )

        # Add the turn to the conversation if needed
        if query_request.conversation_id:
            await self.conversation_service.add_turn(
                conversation_id=query_request.conversation_id,
                user_query=query_request.query,
                system_response=generated_answer
            )
        else:
            # Create a new conversation
            await self.conversation_service.create_conversation(
                conversation_id=conversation_id,
                initial_query=query_request.query,
                initial_response=generated_answer
            )

        return response

    async def _retrieve_context(self, query_request: QueryRequest) -> RetrievedContext:
        """
        Retrieve context using the retrieval tool

        Args:
            query_request: The query request containing query and parameters

        Returns:
            Retrieved context from the knowledge base
        """
        # Prepare parameters for the retrieval tool
        tool_params = {
            "query": query_request.query,
            "top_k": query_request.top_k,
            "score_threshold": query_request.score_threshold,
            "filters": query_request.filters or {}
        }

        # Execute the retrieval tool
        retrieved_context = await self.retrieval_tool.run(**tool_params)

        return retrieved_context

    async def process_batch_queries(
        self,
        queries: List[str],
        top_k: int = None,
        score_threshold: float = None
    ) -> List[AnswerResponse]:
        """
        Process multiple queries in batch

        Args:
            queries: List of query strings
            top_k: Number of results to retrieve (default from settings if not provided)
            score_threshold: Minimum relevance score (default from settings if not provided)

        Returns:
            List of answer responses
        """
        responses = []
        for query in queries:
            # Create a query request with default parameters
            query_request = QueryRequest(
                query=query,
                top_k=top_k or settings.default_top_k,
                score_threshold=score_threshold or settings.default_score_threshold
            )
            response = await self.process_query(query_request)
            responses.append(response)

        return responses

    async def validate_and_process_query(self, query_request: QueryRequest) -> AnswerResponse:
        """
        Validate and process a query with additional safety checks

        Args:
            query_request: The query request to validate and process

        Returns:
            AnswerResponse containing the generated answer
        """
        # Basic validation
        if not query_request.query or len(query_request.query.strip()) == 0:
            raise ValueError("Query cannot be empty")

        if len(query_request.query) > settings.max_query_length:
            raise ValueError(f"Query exceeds maximum length of {settings.max_query_length} characters")

        # Process the query
        return await self.process_query(query_request)