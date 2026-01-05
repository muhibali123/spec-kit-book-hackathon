# Quickstart Guide: Module 04 - Retrieval & Context Filtering Service

## 1. Prerequisites

### System Requirements
- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)
- Access to Cohere API (requires API key)
- Access to Qdrant vector database (requires connection details)

### External Dependencies
- Cohere API account with valid API key
- Qdrant vector database with populated document collection
- Network connectivity to external APIs

## 2. Environment Setup

### Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies
```bash
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt  # For development
```

## 3. Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```bash
# Cohere Configuration
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=embed-multilingual-v2.0

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

# Service Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEFAULT_TOP_K=5
DEFAULT_SCORE_THRESHOLD=0.5
MAX_QUERY_LENGTH=1000
MAX_TOP_K=100
```

### Required Environment Variables
- `COHERE_API_KEY`: Your Cohere API key (required)
- `QDRANT_HOST`: Qdrant database host (default: localhost)
- `QDRANT_PORT`: Qdrant database port (default: 6333)
- `QDRANT_COLLECTION`: Collection name in Qdrant (default: documents)

## 4. Running the Service

### Development Mode
```bash
cd backend
python -m src.main
```

### Using Uvicorn (Recommended for Development)
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Using Docker
```bash
docker build -t retrieval-service .
docker run -p 8000:8000 -e COHERE_API_KEY=your_key_here retrieval-service
```

## 5. API Usage Examples

### Basic Query
```bash
curl -X POST http://localhost:8000/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the benefits of renewable energy?"
  }'
```

### Advanced Query with Parameters
```bash
curl -X POST http://localhost:8000/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does solar panel efficiency compare to wind turbines?",
    "top_k": 10,
    "score_threshold": 0.7,
    "filters": {
      "source_type": "research_paper",
      "year": "2023"
    }
  }'
```

### Health Check
```bash
curl -X GET http://localhost:8000/v1/health
```

## 6. Response Format

### Successful Query Response
```json
{
  "query": "What are the benefits of renewable energy?",
  "results": [
    {
      "id": "doc_123_chunk_456",
      "text": "Renewable energy sources like solar and wind provide clean electricity without greenhouse gas emissions during operation.",
      "score": 0.89,
      "metadata": {
        "source": "renewable_energy_benefits.pdf",
        "page": 12,
        "section": "environmental_impact"
      },
      "source": "renewable_energy_benefits.pdf"
    }
  ],
  "total_results": 1,
  "processing_time": 0.45
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2023-12-16T10:30:00Z",
  "dependencies": {
    "cohere_api": true,
    "qdrant_db": true
  }
}
```

## 7. Testing

### Run Unit Tests
```bash
cd backend
python -m pytest tests/unit/ -v
```

### Run Integration Tests
```bash
cd backend
python -m pytest tests/integration/ -v
```

### Run All Tests
```bash
cd backend
python -m pytest tests/ -v
```

## 8. Configuration Options

### API Configuration
- `API_HOST`: Host address to bind (default: 0.0.0.0)
- `API_PORT`: Port to listen on (default: 8000)

### Cohere Configuration
- `COHERE_API_KEY`: API key for Cohere service (required)
- `COHERE_MODEL`: Embedding model to use (default: embed-multilingual-v2.0)

### Qdrant Configuration
- `QDRANT_HOST`: Qdrant database host (default: localhost)
- `QDRANT_PORT`: Qdrant database port (default: 6333)
- `QDRANT_COLLECTION`: Collection name in Qdrant (default: documents)

### Service Configuration
- `DEFAULT_TOP_K`: Default number of results to return (default: 5)
- `DEFAULT_SCORE_THRESHOLD`: Default minimum similarity score (default: 0.5)
- `MAX_QUERY_LENGTH`: Maximum query length in characters (default: 1000)
- `MAX_TOP_K`: Maximum allowed top_k value (default: 100)

## 9. Troubleshooting

### Common Issues

#### Cohere API Connection Issues
- Verify `COHERE_API_KEY` is correctly set
- Check network connectivity to Cohere API
- Ensure API key has appropriate permissions

#### Qdrant Connection Issues
- Verify Qdrant service is running
- Check `QDRANT_HOST` and `QDRANT_PORT` settings
- Ensure the specified collection exists

#### High Memory Usage
- Reduce `MAX_TOP_K` value
- Implement result streaming for large queries
- Monitor and optimize embedding cache size

### Health Check Failures
- Check logs for specific error messages
- Verify external dependencies are accessible
- Review configuration settings

## 10. Next Steps

### Production Deployment
- Set up proper monitoring and alerting
- Configure load balancing for high availability
- Implement proper security measures (authentication, rate limiting)
- Set up automated backups for configuration

### Performance Optimization
- Implement embedding caching for frequent queries
- Add result caching for common queries
- Optimize Qdrant collection indexing
- Consider implementing async processing for long-running queries