#!/usr/bin/env python3
"""
Test to check if the Qdrant client can access the collection correctly
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from the backend
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Add backend to path to import the Qdrant client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_qdrant_client():
    """Test the Qdrant client used by the backend"""
    from backend.src.clients.qdrant_client import QdrantClient
    from backend.src.config.settings import settings

    print(f"Settings collection: {settings.qdrant_collection}")
    print(f"Settings URL: {settings.qdrant_url}")

    # Create Qdrant client using the same approach as the backend dependencies
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection
    )

    print(f"Client collection name: {client.collection_name}")

    try:
        # Test connection by getting collection info
        collection_info = await client.client.get_collection(client.collection_name)
        print(f"SUCCESS: Successfully connected to collection: {client.collection_name}")
        print(f"Points count: {collection_info.points_count}")
        print(f"Vector size: {collection_info.config.params.vectors.size}")

        # Try to search with a simple vector (this would be used in actual retrieval)
        # Use a simple test vector for search
        test_vector = [0.1] * collection_info.config.params.vectors.size  # Create a test vector of correct size

        # Perform a search to see if we can retrieve documents
        search_results = await client.client.search(
            collection_name=client.collection_name,
            query=test_vector,
            limit=2
        )

        print(f"Search results count: {len(search_results)}")
        if search_results:
            for i, result in enumerate(search_results):
                print(f"  Result {i+1}: ID={result.id}, Score={result.score}")
                print(f"    Text preview: {result.payload.get('text', '')[:100]}...")

        return True

    except Exception as e:
        print(f"ERROR: Error connecting to Qdrant collection: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_sync_client():
    """Test using sync client to see if the issue is async-related"""
    from qdrant_client import QdrantClient as SyncQdrantClient

    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')
    collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'documents')

    print(f"Sync client - URL: {qdrant_url}")
    print(f"Sync client - Collection: {collection_name}")

    try:
        # Initialize sync client
        client = SyncQdrantClient(
            url=qdrant_url.replace("https://", "").replace(":6333", ""),
            api_key=qdrant_api_key,
            https=True
        )

        # Get collection info
        collection_info = client.get_collection(collection_name)
        print(f"SUCCESS: Sync client connected to collection: {collection_name}")
        print(f"Points count: {collection_info.points_count}")

        # Scroll to see some points
        scroll_result = client.scroll(collection_name=collection_name, limit=2)
        points = scroll_result[0]
        print(f"Sample points retrieved: {len(points)}")
        for i, point in enumerate(points):
            print(f"  Point {i+1}: ID={point.id}")
            print(f"    Text preview: {point.payload.get('text', '')[:100]}...")

        return True

    except Exception as e:
        print(f"ERROR: Sync client error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Qdrant client connection...")

    print("\n--- Testing Sync Client ---")
    sync_success = test_sync_client()

    print("\n--- Testing Async Client (Backend Style) ---")
    import asyncio
    async_success = asyncio.run(test_qdrant_client())

    print(f"\n--- Results ---")
    print(f"Sync client: {'SUCCESS' if sync_success else 'FAILED'}")
    print(f"Async client: {'SUCCESS' if async_success else 'FAILED'}")