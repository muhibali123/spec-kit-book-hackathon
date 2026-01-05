#!/bin/bash
# Startup script for RAG backend with proper environment loading

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "Environment variables loaded from .env"
else
    echo "Warning: .env file not found in backend directory"
fi

# Start the uvicorn server
echo "Starting RAG backend server on port 8000..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload