#!/usr/bin/env python3
"""
Backend startup script for development.
"""

import os
import sys
from src.main import app
import uvicorn

if __name__ == "__main__":
    # Use environment variable for port, default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")

    print(f"Starting backend server on {host}:{port}")
    print(f"Access the API at: http://{host}:{port}")
    print(f"API documentation available at: http://{host}:{port}/docs")

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,  # Set to True for development
        log_level="info"
    )