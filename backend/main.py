#!/usr/bin/env python3
"""
Railway deployment entry point for the backend.
This file serves as the entry point for Railway to start the FastAPI application.
"""

import os
import uvicorn
from src.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )