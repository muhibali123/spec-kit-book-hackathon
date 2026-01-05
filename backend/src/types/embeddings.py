"""
Type definitions for the embeddings generation module.
"""
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pydantic import BaseModel


class InputChunk(BaseModel):
    """
    Represents a content chunk from Module 01.

    Attributes:
        chunk_id: Unique identifier for the chunk
        text: Original content text that must remain unchanged
        metadata: Arbitrary metadata structure from Module 01
    """
    chunk_id: str
    text: str
    metadata: Dict[str, Any]


class EmbeddingRecord(BaseModel):
    """
    Represents a content chunk with its generated embedding vector.

    Attributes:
        chunk_id: Matches the input chunk_id exactly
        embedding: Numerical vector from Cohere API
        text: Original content text, preserved unchanged from input
        metadata: Preserved exactly from input chunk
        embedding_model: Name of the Cohere model used
        embedding_dimension: Dimension count of the embedding vector
    """
    chunk_id: str
    embedding: List[float]
    text: str
    metadata: Dict[str, Any]
    embedding_model: str
    embedding_dimension: int


class ProcessingResult(BaseModel):
    """
    Represents the result of the embedding generation process.

    Attributes:
        process_id: Unique identifier for the embedding process
        results: List of embedding records
        summary: Summary statistics for the processing
    """
    process_id: str
    results: List[EmbeddingRecord]
    summary: Dict[str, Any]


class ProcessSummary(BaseModel):
    """
    Represents summary statistics for the embedding generation process.

    Attributes:
        total_chunks: Total number of input chunks
        successful: Number of chunks successfully processed
        failed: Number of chunks that failed processing
        processing_time_ms: Time taken for processing in milliseconds
        model_used: The embedding model that was used
    """
    total_chunks: int
    successful: int
    failed: int
    processing_time_ms: int
    model_used: str