from pydantic import BaseModel, Field
from typing import Optional


class AgentConfig(BaseModel):
    """
    Configuration parameters for the RAG Agent
    """
    # LLM Model Configuration - now supports multiple providers
    model_name: str = Field(
        default="qwen/qwen-2.5-7b-instruct",
        description="Model to use for answer generation (can be OpenAI, OpenRouter, or other model name)"
    )
    llm_provider: str = Field(
        default="openrouter",
        description="LLM provider to use: 'openai', 'openrouter', etc."
    )
    temperature: float = Field(
        default=0.3,
        description="Temperature parameter for answer generation (0.0-2.0)",
        ge=0.0,
        le=2.0
    )
    max_tokens: int = Field(
        default=1000,
        description="Maximum tokens to generate in the answer",
        ge=100,
        le=4000
    )

    # Agent-specific Configuration
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for agent operations",
        ge=1,
        le=10
    )
    timeout: int = Field(
        default=30,
        description="Timeout for agent operations in seconds",
        ge=5,
        le=120
    )

    # Context and Answer Configuration
    min_context_relevance: float = Field(
        default=0.3,
        description="Minimum relevance score for context chunks to be considered",
        ge=0.0,
        le=1.0
    )
    answer_confidence_threshold: float = Field(
        default=0.7,
        description="Minimum confidence threshold for generated answers",
        ge=0.0,
        le=1.0
    )

    # Citation Configuration
    citation_extraction_enabled: bool = Field(
        default=True,
        description="Whether to extract and include citations in answers"
    )

    class Config:
        # Allow extra fields to make it easier to extend
        extra = "allow"