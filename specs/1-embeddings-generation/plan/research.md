# Research: Embeddings Generation (Cohere)

**Feature**: 1-embeddings-generation
**Created**: 2025-12-14

## Decision: Cohere Embedding Model Selection

**Rationale**: After researching Cohere's embedding models, the `embed-english-v3.0` model is optimal for book content as it provides high-quality embeddings for English text with good performance characteristics. For multilingual content, `embed-multilingual-v3.0` would be appropriate.

**Alternatives considered**:
- `embed-english-light-v3.0` - lighter but lower quality
- `embed-multilingual-v3.0` - for non-English content
- Older v2 models - deprecated

**Chosen**: `embed-english-v3.0` as default with option for multilingual

## Decision: Batch Size for API Calls

**Rationale**: Cohere API supports up to 96 texts per request. Using 64 as the default batch size provides a good balance between efficiency and reliability, leaving headroom for API variations and reducing the risk of hitting limits.

**Alternatives considered**:
- 32: Smaller, more reliable but less efficient
- 96: Maximum allowed, most efficient but potentially less reliable
- 64: Balanced approach (selected)

**Chosen**: 64 as default batch size

## Decision: API Rate Limit Handling

**Rationale**: Cohere API rate limits vary by account type. Implementing exponential backoff with jitter provides robust handling of rate limits while being respectful of API resources.

**Alternatives considered**:
- Fixed delay: Simple but potentially inefficient
- Exponential backoff: Adaptive and respectful (selected)
- Circuit breaker: For extreme scenarios

**Chosen**: Exponential backoff with jitter starting at 1000ms