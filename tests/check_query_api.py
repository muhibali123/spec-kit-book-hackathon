#!/usr/bin/env python3
"""
Check the exact API for query_points method
"""
import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def check_query_points_api():
    """Check the exact signature and usage of query_points method"""
    from qdrant_client import AsyncQdrantClient
    from backend.src.config.settings import settings

    print(f"Qdrant URL: {settings.qdrant_url}")
    print(f"Collection: {settings.qdrant_collection}")

    # Create async client
    client = AsyncQdrantClient(
        url=settings.qdrant_url.replace("https://", "").replace(":6333", ""),
        api_key=settings.qdrant_api_key,
        https=True
    )

    # Check the query_points method signature
    import inspect
    if hasattr(client, 'query_points'):
        sig = inspect.signature(client.query_points)
        print(f"\nquery_points signature: {sig}")

        # Get method documentation
        method = getattr(client, 'query_points')
        print(f"Method docstring: {method.__doc__[:500] if method.__doc__ else 'No docstring'}...")
    else:
        print("query_points method not found")

    # Also check the query method
    if hasattr(client, 'query'):
        sig = inspect.signature(client.query)
        print(f"\nquery signature: {sig}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_query_points_api())