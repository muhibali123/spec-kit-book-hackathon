from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class Citation(BaseModel):
    """
    Model for source citations in generated answers
    """
    source_id: str = Field(..., description="Unique identifier for the source document")
    source_title: str = Field(..., description="Title of the source document")
    excerpt: str = Field(..., description="Relevant excerpt from the source")
    page_number: Optional[int] = Field(None, description="Page number in the original document")
    section_reference: Optional[str] = Field(None, description="Section identifier in the document")
    relevance_score: float = Field(..., description="Relevance of this citation to the query", ge=0.0, le=1.0)


class DocumentChunk(BaseModel):
    """
    Model for document chunks returned by the retrieval endpoint
    """
    id: str = Field(..., description="Unique identifier for the document chunk")
    text: str = Field(..., description="The text content of the chunk")
    score: float = Field(..., description="Relevance score for the chunk", ge=0.0, le=1.0)
    metadata: dict = Field(..., description="Additional metadata for the chunk")
    source: str = Field(..., description="Source identifier for the chunk")


class QueryResponse(BaseModel):
    """
    Response model for the document retrieval endpoint
    """
    query: str = Field(..., description="The original query")
    results: List[DocumentChunk] = Field(..., description="List of retrieved document chunks")
    total_results: int = Field(..., description="Total number of results returned")
    processing_time: float = Field(..., description="Time taken to process the query in seconds")


class AnswerResponse(BaseModel):
    """
    Response model for the answer generation endpoint
    """
    query: str = Field(..., description="The original user query")
    answer: str = Field(..., description="The generated answer text")
    citations: List[Citation] = Field(..., description="Source citations for the information in the answer")
    conversation_id: str = Field(..., description="The conversation ID for this interaction")
    confidence_score: Optional[float] = Field(None, description="Confidence in the answer's accuracy", ge=0.0, le=1.0)
    processing_time: float = Field(..., description="Time taken to process the query in seconds")


class HealthCheckResponse(BaseModel):
    """
    Response model for the health check endpoint
    """
    status: str = Field(..., description="Overall health status", example="healthy")
    timestamp: datetime = Field(..., description="When the health check was performed")
    dependencies: dict = Field(..., description="Health status of external dependencies")


class ErrorResponse(BaseModel):
    """
    Response model for error responses
    """
    error: str = Field(..., description="Human-readable error message")
    error_code: str = Field(..., description="Machine-readable error code")
    timestamp: datetime = Field(..., description="When the error occurred")
    details: Optional[dict] = Field(None, description="Additional error details")
