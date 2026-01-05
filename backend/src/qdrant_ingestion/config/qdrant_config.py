import os
from typing import Optional
from pydantic import BaseModel, validator

# Load environment variables from .env file if it exists
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))


class QdrantConfig(BaseModel):
    """
    Configuration model for Qdrant connection settings.
    """
    url: str
    api_key: str
    collection_name: str
    batch_size: int = 100
    vector_distance: str = "Cosine"
    retry_attempts: int = 3
    retry_delay_ms: int = 1000

    @validator('url')
    def validate_url(cls, v):
        if not v:
            raise ValueError('QDRANT_URL is required')
        if not v.startswith(('http://', 'https://')):
            raise ValueError('QDRANT_URL must start with http:// or https://')
        return v

    @validator('api_key')
    def validate_api_key(cls, v):
        if not v:
            raise ValueError('QDRANT_API_KEY is required')
        return v

    @validator('collection_name')
    def validate_collection_name(cls, v):
        if not v:
            raise ValueError('QDRANT_COLLECTION_NAME is required')
        return v

    @validator('batch_size')
    def validate_batch_size(cls, v):
        if v <= 0:
            raise ValueError('BATCH_SIZE must be a positive integer')
        if v > 1000:  # Reasonable upper limit
            raise ValueError('BATCH_SIZE should not exceed 1000 for optimal performance')
        return v

    @validator('vector_distance')
    def validate_vector_distance(cls, v):
        valid_distances = ['Cosine', 'Euclid', 'Dot']
        if v not in valid_distances:
            raise ValueError(f'VECTOR_DISTANCE must be one of {valid_distances}')
        return v.title()  # Normalize to title case


def load_qdrant_config() -> QdrantConfig:
    """
    Load Qdrant configuration from environment variables.
    """
    # Use QDRANT_COLLECTION_NAME if available, otherwise fall back to QDRANT_COLLECTION
    collection_name = os.getenv('QDRANT_COLLECTION_NAME') or os.getenv('QDRANT_COLLECTION', 'documents')

    return QdrantConfig(
        url=os.getenv('QDRANT_URL', ''),
        api_key=os.getenv('QDRANT_API_KEY', ''),
        collection_name=collection_name,
        batch_size=int(os.getenv('BATCH_SIZE', '100')),
        vector_distance=os.getenv('VECTOR_DISTANCE', 'Cosine'),
        retry_attempts=int(os.getenv('RETRY_ATTEMPTS', '3')),
        retry_delay_ms=int(os.getenv('RETRY_DELAY_MS', '1000'))
    )


def validate_environment() -> bool:
    """
    Validate that all required environment variables are set.
    """
    required_vars = ['QDRANT_URL', 'QDRANT_API_KEY', 'QDRANT_COLLECTION_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return True