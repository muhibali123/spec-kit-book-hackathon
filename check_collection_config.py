#!/usr/bin/env python3
"""
Script to check which collection name is configured in the backend
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.config.settings import settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

def check_collection_config():
    print("Checking collection configuration...")
    print(f"Settings qdrant_collection: {settings.qdrant_collection}")
    print(f"Environment QDRANT_COLLECTION: {os.getenv('QDRANT_COLLECTION', 'NOT SET')}")
    print(f"Environment QDRANT_COLLECTION_NAME: {os.getenv('QDRANT_COLLECTION_NAME', 'NOT SET')}")
    print(f"Environment QDRANT_URL: {os.getenv('QDRANT_URL', 'NOT SET')}")
    print(f"Environment QDRANT_API_KEY exists: {'YES' if os.getenv('QDRANT_API_KEY') else 'NO'}")

    # Check what collection the Qdrant client would use
    from backend.src.api.dependencies import get_qdrant_client
    import asyncio

    async def test_client():
        client_gen = get_qdrant_client()
        client = await client_gen.__anext__()  # Get the client
        print(f"Qdrant client collection name: {client.collection_name}")

    # asyncio.run(test_client())  # Commented out to avoid async issues

if __name__ == "__main__":
    check_collection_config()