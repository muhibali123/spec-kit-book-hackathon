# API Contracts: Module 06 - Chat UI & Frontend Integration

## 1. Overview

This document defines the API contracts for the Chat UI & Frontend Integration module. These contracts specify how the frontend communicates with the backend services from Module 05 (RAG Agent).

## 2. Request/Response Models

### Query Request Model
**Purpose**: Request format for submitting user questions to the RAG Agent
- **Method**: POST
- **Endpoint**: `/api/v1/query` (consumes from Module 05)
- **Content-Type**: application/json

**Request Body**:
```json
{
  "query": "string (user's question)",
  "conversation_id": "string (optional, for maintaining conversation context)",
  "top_k": "integer (optional, number of results to retrieve)",
  "score_threshold": "float (optional, minimum relevance score)",
  "filters": "object (optional, additional filters for retrieval)"
}
```

**Response Body (Success)**:
```json
{
  "query": "string (original query)",
  "answer": "string (AI-generated answer)",
  "citations": [
    {
      "source_id": "string",
      "source_title": "string",
      "excerpt": "string",
      "page_number": "integer (optional)",
      "section_reference": "string (optional)",
      "relevance_score": "float (0.0-1.0)"
    }
  ],
  "conversation_id": "string",
  "confidence_score": "float (0.0-1.0)",
  "processing_time": "float (seconds)"
}
```

**Response Body (Error)**:
```json
{
  "error": {
    "code": "string (error code)",
    "message": "string (user-friendly error message)",
    "details": "object (optional, additional error details)"
  }
}
```

### Health Check Request Model
**Purpose**: Check backend service availability
- **Method**: GET
- **Endpoint**: `/api/v1/health` (consumes from Module 05)
- **Content-Type**: application/json

**Response Body (Success)**:
```json
{
  "status": "string (overall system status)",
  "services": {
    "retrieval_service": "string (status)",
    "llm_service": "string (status)",
    "database": "string (status)"
  },
  "timestamp": "string (ISO 8601 timestamp)"
}
```

## 3. Frontend API Endpoints

### Chat Service Interface
The frontend will implement a ChatService interface to abstract API communication:

**Methods**:
- `submitQuery(query: string, conversationId?: string)`: Promise<QueryResponse>
- `getConversation(conversationId: string)`: Promise<Conversation>
- `createNewConversation()`: Promise<Conversation>
- `checkHealth()`: Promise<HealthStatus>

### Error Response Handling
All API responses follow the same error format:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "timestamp": "string (ISO 8601)",
    "request_id": "string (for tracking)"
  }
}
```

**Standard Error Codes**:
- `INVALID_INPUT`: User input failed validation
- `SERVICE_UNAVAILABLE`: Backend service is temporarily unavailable
- `RATE_LIMIT_EXCEEDED`: Request rate limit has been exceeded
- `NO_RELEVANT_ANSWER`: No relevant answer found in knowledge base
- `REQUEST_TIMEOUT`: Request timed out waiting for response
- `SESSION_EXPIRED`: User session has expired

## 4. Request Headers

### Standard Headers for All Requests
- `Content-Type`: application/json
- `Accept`: application/json
- `User-Agent`: Custom user agent identifying the chat UI
- `X-Request-ID`: UUID for request tracking (generated client-side)
- `Authorization`: Bearer token (if authentication is required)

### Timeout Configuration
- **Connection Timeout**: 10 seconds
- **Read Timeout**: 30 seconds
- **Overall Request Timeout**: 60 seconds

## 5. Response Status Codes

### Success Responses
- `200 OK`: Request successful
- `201 Created`: New resource created (e.g., new conversation)

### Client Error Responses
- `400 Bad Request`: Invalid request format or parameters
- `401 Unauthorized`: Authentication required but not provided
- `422 Unprocessable Entity`: Request format valid but semantic validation failed
- `429 Too Many Requests`: Rate limit exceeded

### Server Error Responses
- `500 Internal Server Error`: General server error
- `502 Bad Gateway`: Upstream service error
- `503 Service Unavailable`: Service temporarily unavailable
- `504 Gateway Timeout`: Upstream service timeout

## 6. Data Validation Rules

### Input Validation
- Query length: 1-1000 characters
- Conversation ID: Valid UUID format if provided
- Top-k parameter: 1-20 range if provided
- Score threshold: 0.0-1.0 range if provided

### Response Validation
- Answer must not be empty when status is success
- Citations array must contain valid citation objects when present
- Confidence score must be in 0.0-1.0 range
- Processing time must be positive number

## 7. Session Management Contracts

### Session State
The frontend maintains session state with the following contract:

**Session Object**:
```json
{
  "sessionId": "string (unique session identifier)",
  "userId": "string (optional, user identifier)",
  "activeConversationId": "string",
  "preferences": {
    "theme": "string (light/dark)",
    "autoScroll": "boolean",
    "showCitations": "boolean"
  },
  "createdAt": "string (ISO 8601)",
  "expiresAt": "string (ISO 8601)"
}
```

### Session Expiration
- Sessions expire after 8 hours of inactivity
- Frontend should warn user 5 minutes before expiration
- Conversation history preserved in local storage after session expiration