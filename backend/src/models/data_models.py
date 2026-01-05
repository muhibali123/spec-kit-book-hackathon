from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ContextChunk(BaseModel):
    """
    A segment of content from the knowledge base that is relevant to the query
    """
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    content: str = Field(..., description="The actual text content", max_length=10000)
    source_document: str = Field(..., description="Reference to the original document")
    source_section: Optional[str] = Field(None, description="Section within the document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata like page number, chapter, etc.")
    relevance_score: float = Field(..., description="How relevant this chunk is to the query", ge=0.0, le=1.0)


class RetrievedContext(BaseModel):
    """
    The relevant document chunks and metadata retrieved from Module 04
    """
    context_chunks: List[ContextChunk] = Field(..., description="List of relevant document segments")
    relevance_scores: List[float] = Field(..., description="Confidence scores for each chunk")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional information about the retrieval")


class GeneratedAnswer(BaseModel):
    """
    The AI-produced response that addresses the user's query
    """
    answer_id: str = Field(..., description="Unique identifier for the answer")
    answer_text: str = Field(..., description="The generated answer text")
    confidence_score: Optional[float] = Field(None, description="Confidence in the answer's accuracy", ge=0.0, le=1.0)
    citations: List[Dict[str, Any]] = Field(..., description="References to source documents", max_items=20)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional information about the generation process")
    timestamp: datetime = Field(..., description="When the answer was generated")


class ConversationTurn(BaseModel):
    """
    A single exchange in a conversation
    """
    turn_id: str = Field(..., description="Unique identifier for the turn")
    user_query: str = Field(..., description="The user's input query")
    system_response: str = Field(..., description="The system's response text")
    timestamp: datetime = Field(..., description="When the exchange occurred")
    context_summary: Optional[str] = Field(None, description="Brief summary of context for this turn")


class ConversationContext(BaseModel):
    """
    History of interactions between the user and system
    """
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    turns: List[ConversationTurn] = Field(..., description="Chronological list of exchanges", max_items=25)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context like user preferences")
    created_at: datetime = Field(..., description="When the conversation started")
    last_activity: datetime = Field(..., description="When the last interaction occurred")
    is_active: bool = Field(default=True, description="Whether the conversation is still active")


class EmbeddingRequest(BaseModel):
    """
    Internal model for Cohere API requests
    """
    texts: List[str] = Field(..., description="Texts to generate embeddings for")
    model: str = Field(default="embed-multilingual-v2.0", description="Cohere embedding model to use")


class EmbeddingResponse(BaseModel):
    """
    Internal model for Cohere API responses
    """
    embeddings: List[List[float]] = Field(..., description="Generated embeddings as lists of floats")
    texts_count: int = Field(..., description="Number of texts that were embedded")


class QdrantSearchRequest(BaseModel):
    """
    Internal model for Qdrant search requests
    """
    vector: List[float] = Field(..., description="Query vector for similarity search")
    top_k: int = Field(..., description="Number of results to retrieve")
    score_threshold: Optional[float] = Field(None, description="Minimum similarity score threshold")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters to apply during search")


class RetrievedDocument(BaseModel):
    """
    A document or chunk retrieved from the knowledge base
    """
    id: str = Field(..., description="Unique identifier for the retrieved document/chunk")
    payload: Dict[str, Any] = Field(..., description="The document content and metadata")
    score: float = Field(..., description="Similarity score for the retrieved document", ge=0.0, le=1.0)
