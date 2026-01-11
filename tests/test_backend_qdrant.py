#!/usr/bin/env python3
"""
Test script to check the backend's Qdrant client directly
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.clients.qdrant_client import QdrantClient
from src.config.settings import settings

async def test_backend_qdrant_client():
    print(f"Testing backend Qdrant client configuration...")
    print(f"Qdrant URL: {settings.qdrant_url}")
    print(f"Qdrant Collection: {settings.qdrant_collection}")
    print(f"Qdrant API Key: {'SET' if settings.qdrant_api_key else 'NOT SET'}")

    # Create the same client as used in the backend
    qdrant_client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection
    )

    try:
        # Test search with a simple vector
        # We'll use a dummy vector of the right size - this is just to test connectivity
        # In practice, we'd need a real embedding, but this tests if the connection works
        test_vector = [0.0] * 768  # Default size for embed-multilingual-v2.0

        print(f"Attempting to query with test vector of size {len(test_vector)}...")

        # This should call the query_points method in the QdrantClient
        results = await qdrant_client.search(
            vector=test_vector,
            top_k=1,
            score_threshold=0.0
        )

        print(f"✅ Successfully connected to Qdrant!")
        print(f"Retrieved {len(results)} results")

        if results:
            for result in results:
                print(f"Sample result - ID: {result.id}, Score: {result.score}")
                print(f"Payload keys: {list(result.payload.keys()) if result.payload else 'None'}")

    except Exception as e:
        print(f"❌ Error connecting to Qdrant: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_backend_qdrant_client())