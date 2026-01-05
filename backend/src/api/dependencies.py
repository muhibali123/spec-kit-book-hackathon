from typing import Generator
from fastapi import Depends
from src.config.settings import settings
from src.services.retrieval_service import RetrievalService
from src.services.filtering_service import FilteringService
from src.services.agent_service import AgentService
from src.clients.cohere_client import CohereClient
from src.clients.qdrant_client import QdrantClient
from src.utils.logging import get_logger


def get_cohere_client() -> Generator[CohereClient, None, None]:
    """Dependency to provide Cohere client instance"""
    client = CohereClient(api_key=settings.cohere_api_key, model=settings.cohere_model)
    yield client


def get_qdrant_client() -> Generator[QdrantClient, None, None]:
    """Dependency to provide Qdrant client instance"""
    # Use URL if provided, otherwise use host/port
    if settings.qdrant_url:
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            collection_name=settings.qdrant_collection
        )
    else:
        client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
            collection_name=settings.qdrant_collection
        )
    yield client


def get_filtering_service() -> FilteringService:
    """Dependency to provide filtering service instance"""
    return FilteringService()


def get_retrieval_service(
    cohere_client: CohereClient = Depends(get_cohere_client),
    qdrant_client: QdrantClient = Depends(get_qdrant_client),
    filtering_service: FilteringService = Depends(get_filtering_service)
) -> RetrievalService:
    """Dependency to provide retrieval service instance with its dependencies"""
    logger = get_logger("retrieval_service.api")
    return RetrievalService(
        cohere_client=cohere_client,
        qdrant_client=qdrant_client,
        filtering_service=filtering_service,
        logger=logger
    )


def get_agent_service() -> AgentService:
    """Dependency to provide agent service instance"""
    from src.agents.rag_agent import RAGAgent
    from src.tools.retrieval_tool import RetrievalTool
    from src.services.conversation_service import ConversationService

    # Create the RAG agent
    from src.agents.agent_config import AgentConfig
    agent_config = AgentConfig(
        llm_provider=settings.llm_provider,
        model_name=settings.openai_model if settings.llm_provider == "openai" else settings.openrouter_model
    )
    rag_agent = RAGAgent(config=agent_config)

    # Create the retrieval tool
    retrieval_tool = RetrievalTool()

    # Create the conversation service
    conversation_service = ConversationService()

    # Create and return the agent service
    return AgentService(
        rag_agent=rag_agent,
        retrieval_tool=retrieval_tool,
        conversation_service=conversation_service
    )