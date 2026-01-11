# RAG Agent & Answer Generation Service

This is the backend service for the RAG (Retrieval Augmented Generation) agent that generates grounded, context-aware answers using AI models and retrieved context.

## Backend Structure
```
backend/
├── src/                    # Source code
│   ├── main.py            # FastAPI app instance
│   ├── api/               # API routes
│   │   └── v1/            # API v1 endpoints
│   │       └── endpoints/ # Individual endpoint files
│   ├── models/            # Data models and schemas
│   ├── services/          # Business logic services
│   ├── config/            # Configuration settings
│   ├── utils/             # Utility functions
│   ├── agents/            # AI agents
│   ├── adapters/          # LLM adapters
│   └── clients/           # External API clients
├── main.py               # Railway deployment entry point
├── requirements.txt      # Python dependencies
├── run_server.py         # Development server script
├── validate_backend.py   # Backend validation script
└── railway.json          # Railway configuration
```

## Running the Backend

### Local Development
```bash
# Navigate to backend directory
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the development server
python run_server.py
```

### Railway Deployment
The backend is configured for Railway deployment:
- Entry point: `main.py`
- Start command: `python main.py`
- Port: Uses `PORT` environment variable (defaults to 8000)

## API Endpoints
- Root: `http://localhost:8000/` - Health check and basic info
- Docs: `http://localhost:8000/docs` - Interactive API documentation
- API: `http://localhost:8000/v1/` - Version 1 API endpoints

## Environment Variables
The backend uses the following environment variables:
- `COHERE_API_KEY` - Cohere API key for embeddings
- `QDRANT_API_KEY` - Qdrant API key for vector database
- `OPENAI_API_KEY` - OpenAI API key (if using OpenAI adapter)
- `GEMINI_API_KEY` - Google Gemini API key (if using Gemini adapter)
- `QDRANT_HOST` - Qdrant host URL
- `QDRANT_PORT` - Qdrant port (default: 6333)

## Validation
To validate the backend is working correctly:
```bash
python validate_backend.py
```

## Dependencies
All dependencies are listed in `requirements.txt` and managed by pip.