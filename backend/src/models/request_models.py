from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID


class QueryRequest(BaseModel):
    """
    Request model for the answer generation endpoint
    """
    query: str = Field(
        ...,
        description="The user's natural language query",
        min_length=1,
        max_length=1000
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID for multi-turn interactions",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional filters to apply when retrieving context"
    )
    top_k: Optional[int] = Field(
        5,
        description="Number of context chunks to retrieve",
        ge=1,
        le=20
    )
    score_threshold: Optional[float] = Field(
        0.5,
        description="Minimum relevance score threshold",
        ge=0.0,
        le=1.0
    )
