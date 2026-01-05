"""
Models package for the RAG Agent & Answer Generation Service
"""
from .request_models import QueryRequest
from .response_models import (
    AnswerResponse,
    Citation,
    DocumentChunk,
    QueryResponse,
    HealthCheckResponse,
    ErrorResponse
)
from .data_models import (
    ContextChunk,
    RetrievedContext,
    GeneratedAnswer,
    ConversationTurn,
    ConversationContext
)

__all__ = [
    # Request models
    "QueryRequest",

    # Response models
    "AnswerResponse",
    "Citation",
    "DocumentChunk",
    "QueryResponse",
    "HealthCheckResponse",
    "ErrorResponse",

    # Data models
    "ContextChunk",
    "RetrievedContext",
    "GeneratedAnswer",
    "ConversationTurn",
    "ConversationContext"
]
