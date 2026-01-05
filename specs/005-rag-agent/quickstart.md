# Quickstart Guide: RAG Agent & Answer Generation Service

## Overview
The RAG Agent service generates grounded, context-aware answers by retrieving relevant information from your knowledge base and using an LLM to synthesize responses with proper citations.

## Prerequisites
- Access to Module 04 (Retrieval & Context Filtering Service)
- OpenAI API key for LLM integration
- Basic understanding of REST API calls

## Getting Started

### 1. Environment Setup
```bash
# Set required environment variables
export OPENAI_API_KEY="your-openai-api-key"
export RETRIEVAL_SERVICE_URL="http://localhost:8000"  # Module 04 endpoint
export API_KEY="your-service-api-key"  # For service authentication
```

### 2. Generate Your First Answer
Make a POST request to the `/v1/answer` endpoint:

```bash
curl -X POST "http://localhost:8000/v1/answer" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-service-api-key" \
  -d '{
    "query": "What are the benefits of renewable energy?"
  }'
```

Expected response:
```json
{
  "query": "What are the benefits of renewable energy?",
  "answer": "Renewable energy offers several key benefits...",
  "citations": [
    {
      "source_id": "doc_12345",
      "source_title": "Renewable Energy Benefits Report 2023",
      "excerpt": "Renewable energy sources such as solar and wind power...",
      "relevance_score": 0.92
    }
  ],
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "confidence_score": 0.85,
  "processing_time": 2.34
}
```

### 3. Multi-turn Conversations
To maintain context across multiple queries, use the `conversation_id` from the response:

```bash
curl -X POST "http://localhost:8000/v1/answer" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-service-api-key" \
  -d '{
    "query": "Can you elaborate on the environmental benefits?",
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

### 4. Using Filters
You can apply filters to retrieve more targeted context:

```bash
curl -X POST "http://localhost:8000/v1/answer" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-service-api-key" \
  -d '{
    "query": "What do recent studies say about solar efficiency?",
    "filters": {
      "year": 2023,
      "category": "solar_technology"
    },
    "top_k": 3
  }'
```

## Key Features

### Source Citations
Every answer includes citations showing exactly which documents informed the response, allowing you to verify information.

### Context Awareness
The service maintains conversation context for up to 25 turns within a 2-hour window, enabling natural multi-turn interactions.

### Confidence Scoring
Each answer includes a confidence score to help you assess the reliability of the response.

### Rate Limiting
The service implements rate limiting (30 queries per minute per user) to ensure fair usage and prevent abuse.

## Health Check
Monitor service health with the `/v1/health` endpoint:

```bash
curl "http://localhost:8000/v1/health"
```

## Troubleshooting

### Common Issues
- **429 Rate Limit**: Wait before making additional requests
- **400 Validation Error**: Check query length and format
- **500 Internal Error**: Verify OpenAI API key and Module 04 availability

### Performance Tips
- Keep queries specific and focused for better results
- Use filters to narrow down relevant context
- Monitor processing times to optimize query patterns