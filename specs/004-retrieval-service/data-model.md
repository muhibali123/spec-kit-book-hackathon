# Data Models: Module 04 - Retrieval & Context Filtering Service

## 1. Request Models

### QueryRequest
**Purpose**: Represents the input to the retrieval service

```python
class QueryRequest(BaseModel):
    query: str
        description: "The user query text to be processed"
        constraints: "Required, minimum 1 character, maximum 1000 characters"

    top_k: int = 5
        description: "Number of top results to return"
        constraints: "Optional, default 5, minimum 1, maximum 100"

    score_threshold: float = 0.5
        description: "Minimum similarity score threshold for results"
        constraints: "Optional, default 0.5, range 0.0-1.0"

    filters: Optional[Dict[str, Any]] = None
        description: "Metadata filters to apply to results"
        constraints: "Optional, key-value pairs for filtering"

    include_metadata: bool = True
        description: "Whether to include document metadata in results"
        constraints: "Optional, default True"
```

### HealthCheckRequest
**Purpose**: Simple request model for health check endpoint

```python
class HealthCheckRequest(BaseModel):
    # No fields required for health check
```

## 2. Response Models

### QueryResponse
**Purpose**: Represents the output from the retrieval service

```python
class DocumentChunk(BaseModel):
    id: str
        description: "Unique identifier for the document chunk"
        constraints: "Required, UUID format"

    text: str
        description: "The text content of the document chunk"
        constraints: "Required"

    score: float
        description: "Similarity score between query and document"
        constraints: "Required, range 0.0-1.0"

    metadata: Dict[str, Any]
        description: "Metadata associated with the document"
        constraints: "Required, key-value pairs"

    source: str
        description: "Source document identifier"
        constraints: "Required"

class QueryResponse(BaseModel):
    query: str
        description: "Original query text"
        constraints: "Required"

    results: List[DocumentChunk]
        description: "List of retrieved document chunks"
        constraints: "Required, can be empty"

    total_results: int
        description: "Total number of results before filtering"
        constraints: "Required"

    processing_time: float
        description: "Time taken to process the query in seconds"
        constraints: "Required"
```

### HealthCheckResponse
**Purpose**: Response model for health check endpoint

```python
class HealthCheckResponse(BaseModel):
    status: str
        description: "Service health status"
        constraints: "Required, 'healthy' when service is operational"

    timestamp: datetime
        description: "Timestamp of the health check"
        constraints: "Required, ISO format"

    dependencies: Dict[str, bool]
        description: "Status of external dependencies"
        constraints: "Required, service name to status mapping"
```

### ErrorResponse
**Purpose**: Standard error response format

```python
class ErrorResponse(BaseModel):
    error: str
        description: "Error message"
        constraints: "Required"

    error_code: str
        description: "Machine-readable error code"
        constraints: "Required"

    timestamp: datetime
        description: "Time when error occurred"
        constraints: "Required, ISO format"

    details: Optional[Dict[str, Any]]
        description: "Additional error details"
        constraints: "Optional"
```

## 3. Internal Data Models

### EmbeddingRequest
**Purpose**: Internal model for Cohere API requests

```python
class EmbeddingRequest(BaseModel):
    texts: List[str]
        description: "Texts to generate embeddings for"
        constraints: "Required, list of strings"

    model: str = "embed-multilingual-v2.0"
        description: "Cohere embedding model to use"
        constraints: "Optional, default model"
```

### EmbeddingResponse
**Purpose**: Internal model for Cohere API responses

```python
class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
        description: "Generated embeddings as lists of floats"
        constraints: "Required, list of embedding vectors"

    texts_count: int
        description: "Number of texts that were embedded"
        constraints: "Required"
```

### QdrantSearchRequest
**Purpose**: Internal model for Qdrant search requests

```python
class QdrantSearchRequest(BaseModel):
    vector: List[float]
        description: "Query vector for similarity search"
        constraints: "Required, embedding vector"

    top_k: int
        description: "Number of results to retrieve"
        constraints: "Required"

    score_threshold: Optional[float]
        description: "Minimum similarity score threshold"
        constraints: "Optional"

    filters: Optional[Dict[str, Any]]
        description: "Filters to apply during search"
        constraints: "Optional"
```

### RetrievedDocument
**Purpose**: Internal model for documents retrieved from Qdrant

```python
class RetrievedDocument(BaseModel):
    id: str
        description: "Document ID from Qdrant"
        constraints: "Required"

    payload: Dict[str, Any]
        description: "Document payload from Qdrant"
        constraints: "Required"

    score: float
        description: "Similarity score from Qdrant"
        constraints: "Required"
```

## 4. Configuration Models

### Settings
**Purpose**: Application configuration settings

```python
class Settings(BaseModel):
    # API Settings
    api_host: str = "0.0.0.0"
        description: "Host for the API server"
        constraints: "Optional, default '0.0.0.0'"

    api_port: int = 8000
        description: "Port for the API server"
        constraints: "Optional, default 8000"

    # Cohere Settings
    cohere_api_key: str
        description: "Cohere API key"
        constraints: "Required, must be provided as environment variable"

    cohere_model: str = "embed-multilingual-v2.0"
        description: "Cohere embedding model to use"
        constraints: "Optional, default model"

    # Qdrant Settings
    qdrant_host: str = "localhost"
        description: "Qdrant host address"
        constraints: "Optional, default 'localhost'"

    qdrant_port: int = 6333
        description: "Qdrant port number"
        constraints: "Optional, default 6333"

    qdrant_collection: str = "documents"
        description: "Qdrant collection name for document storage"
        constraints: "Optional, default 'documents'"

    # Service Settings
    default_top_k: int = 5
        description: "Default number of results to return"
        constraints: "Optional, default 5"

    default_score_threshold: float = 0.5
        description: "Default minimum similarity score"
        constraints: "Optional, default 0.5"

    max_query_length: int = 1000
        description: "Maximum allowed query length in characters"
        constraints: "Optional, default 1000"

    max_top_k: int = 100
        description: "Maximum allowed top_k value"
        constraints: "Optional, default 100"

    class Config:
        env_file = ".env"
        case_sensitive = True
```

## 5. Relationship Diagram

```
QueryRequest
    ↓ (validation)
    ↓ (processing)
Service Layer
    ↓ (embedding generation)
EmbeddingRequest → Cohere API → EmbeddingResponse
    ↓ (similarity search)
QdrantSearchRequest → Qdrant DB → RetrievedDocument
    ↓ (filtering)
    ↓ (formatting)
QueryResponse
```

## 6. Validation Rules

### QueryRequest Validation
- Query text must be 1-1000 characters
- top_k must be between 1-100
- score_threshold must be between 0.0-1.0
- filters must be valid JSON object if provided

### DocumentChunk Validation
- Score must be between 0.0-1.0
- All required fields must be present
- ID must be a valid identifier

### Configuration Validation
- API keys must be provided
- Hostnames and ports must be valid
- Default values must be within acceptable ranges