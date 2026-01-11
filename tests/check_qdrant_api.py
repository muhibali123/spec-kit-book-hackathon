#!/usr/bin/env python3
"""
Check the actual Qdrant async client API
"""
import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def check_async_client_api():
    """Check what methods are available on the async Qdrant client"""
    from qdrant_client import AsyncQdrantClient
    from backend.src.config.settings import settings

    print(f"Qdrant URL: {settings.qdrant_url}")
    print(f"Qdrant API Key: {'SET' if settings.qdrant_api_key else 'NOT SET'}")
    print(f"Collection: {settings.qdrant_collection}")

    # Create async client
    client = AsyncQdrantClient(
        url=settings.qdrant_url.replace("https://", "").replace(":6333", ""),
        api_key=settings.qdrant_api_key,
        https=True
    )

    # List available methods
    methods = [method for method in dir(client) if not method.startswith('_') and callable(getattr(client, method))]
    print(f"\nAvailable methods on AsyncQdrantClient:")
    for method in sorted(methods):
        print(f"  - {method}")

    # Check specifically for search-related methods
    search_methods = [method for method in methods if 'search' in method.lower()]
    print(f"\nSearch-related methods: {search_methods}")

    # Check if 'search' method exists and its signature
    if hasattr(client, 'search') and callable(getattr(client, 'search')):
        print(f"\nThe 'search' method exists")
        import inspect
        sig = inspect.signature(client.search)
        print(f"Signature: {sig}")
    else:
        print(f"\nNo 'search' method found")

    # Test connection to ensure it works
    try:
        collection_info = await client.get_collection(settings.qdrant_collection)
        print(f"\n✅ Successfully connected to collection: {settings.qdrant_collection}")
        print(f"Points count: {collection_info.points_count}")
    except Exception as e:
        print(f"❌ Error connecting to collection: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_async_client_api())