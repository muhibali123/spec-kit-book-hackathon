from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class EmbeddingRecord(BaseModel):
    """
    Represents a single chunk of text with its vector representation and associated metadata.
    """
    chunk_id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]
    model: str
    dimension: int

    class Config:
        # Allow extra fields in metadata but validate the core structure
        extra = "allow"


class QdrantPoint(BaseModel):
    """
    Represents a vector storage entity in Qdrant containing the embedding vector and payload.
    """
    id: str
    vector: List[float]
    payload: Dict[str, Any]

    class Config:
        # Allow flexible payload structure
        extra = "allow"


class IngestionJob(BaseModel):
    """
    Represents a process that loads embeddings from JSON, validates them, and uploads them to Qdrant with error tracking.
    """
    file_path: str
    total_records: int
    processed_records: int = 0
    successful_uploads: int = 0
    failed_uploads: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    class Config:
        # Allow additional fields for tracking
        extra = "allow"