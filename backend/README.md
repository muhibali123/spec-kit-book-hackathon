# Qdrant Vector Database Ingestion Module

This module handles the ingestion of embedding vectors into a Qdrant vector database, providing a robust and scalable solution for RAG (Retrieval-Augmented Generation) systems.

## Features

- **Idempotent Ingestion**: Uses chunk_id as unique identifiers to prevent duplicates during re-ingestion
- **Batch Processing**: Configurable batch sizes for efficient ingestion
- **Error Handling**: Comprehensive error handling with retry logic and exponential backoff
- **Validation**: Input schema validation, dimension consistency checks, and payload integrity verification
- **Resume Functionality**: Ability to resume interrupted ingestion processes
- **Metrics & Logging**: Detailed metrics and structured logging for monitoring

## Requirements

- Python 3.8+
- Qdrant Cloud account (or self-hosted Qdrant instance)
- Embeddings in JSON format with the following structure:
  ```json
  [
    {
      "chunk_id": "unique-identifier",
      "text": "Content text...",
      "embedding": [0.1, 0.2, 0.3, ...],
      "metadata": {"source": "document.pdf", "page": 1},
      "model": "embed-english-v3.0",
      "dimension": 1024
    }
  ]
  ```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

```bash
export QDRANT_URL="https://your-cluster.qdrant.tech:6333"
export QDRANT_API_KEY="your-api-key"
export QDRANT_COLLECTION_NAME="your-collection-name"
export BATCH_SIZE=100
export VECTOR_DISTANCE="Cosine"
export RETRY_ATTEMPTS=3
export RETRY_DELAY_MS=1000
```

## Usage

### Command Line Interface

```bash
python -m src.cli --input embeddings.json
```

### Direct Python Usage

```python
from src.qdrant_ingestion.index import main_ingestion_workflow

result = main_ingestion_workflow("path/to/embeddings.json")
print(f"Successfully ingested {result['successful_count']} records")
```

## Environment Variables

- `QDRANT_URL`: URL of the Qdrant instance
- `QDRANT_API_KEY`: API key for authentication
- `QDRANT_COLLECTION_NAME`: Name of the collection to use
- `BATCH_SIZE`: Number of records to process in each batch (default: 100)
- `VECTOR_DISTANCE`: Distance metric to use (default: Cosine)
- `RETRY_ATTEMPTS`: Number of retry attempts for failed operations (default: 3)
- `RETRY_DELAY_MS`: Initial delay between retries in milliseconds (default: 1000)

## Architecture

The module is organized into the following components:

- `clients/`: Qdrant client wrapper with connection management
- `config/`: Configuration loading and validation
- `managers/`: Business logic for collection management and ingestion
- `types/`: Data models and type definitions
- `utils/`: Utility functions for logging and metrics
- `validators/`: Input validation logic

## Error Handling

The system implements comprehensive error handling:

- Network failure handling with exponential backoff
- Individual record validation with detailed error reporting
- Batch processing with partial failure tolerance
- Idempotent operations to handle retries safely

## Performance

- Configurable batch sizes for optimal performance
- Asynchronous operations where possible
- Efficient memory usage for large datasets
- Detailed performance metrics

## Testing

To run the ingestion with a sample file:

```bash
python -m src.cli --input sample_embeddings.json
```

## Troubleshooting

- **Connection Issues**: Verify QDRANT_URL and QDRANT_API_KEY are correct
- **Authentication Errors**: Check API key validity and permissions
- **Schema Validation Errors**: Ensure input files match the expected structure
- **Performance Issues**: Adjust BATCH_SIZE based on your Qdrant instance capacity