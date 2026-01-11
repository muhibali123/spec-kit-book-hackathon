#!/usr/bin/env python3
"""
Production-ready backend server startup.
"""

import os
import sys
from src.main import app
import uvicorn

def main():
    """
    Main entry point for the backend server.
    """
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")  # Use 0.0.0.0 for external access

    print("=" * 60)
    print("RAG Agent & Answer Generation Service")
    print("=" * 60)
    print(f"Starting server on {host}:{port}")
    print(f"API available at: http://{host}:{port}")
    print(f"Documentation: http://{host}:{port}/docs")
    print(f"Health check: http://{host}:{port}/")
    print("=" * 60)

    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,  # False for production
        log_level="info"
    )

if __name__ == "__main__":
    main()