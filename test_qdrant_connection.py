#!/usr/bin/env python3
"""
Test script to check Qdrant connection and collection contents
"""
import asyncio
from qdrant_client import AsyncQdrantClient
from src.config.settings import settings

async def test_qdrant_connection():
    print(f"Qdrant URL: {settings.qdrant_url}")
    print(f"Qdrant Collection: {settings.qdrant_collection}")
    print(f"Qdrant API Key: {'SET' if settings.qdrant_api_key else 'NOT SET'}")

    # Create client with the same configuration as the backend
    if settings.qdrant_url:
        client = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key, prefer_grpc=False)
    else:
        client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, api_key=settings.qdrant_api_key, prefer_grpc=False)

    try:
        # Get collection info
        collection_info = await client.get_collection(collection_name=settings.qdrant_collection)
        print(f"Collection '{settings.qdrant_collection}' exists")
        print(f"Points count: {collection_info.points_count}")
        print(f"Vector size: {collection_info.config.params.vectors.size}")
        print(f"Distance: {collection_info.config.params.vectors.distance}")

        # Try a simple search to see if we get results
        print("\nTesting search with a simple vector...")
        # Use a simple embedding for "test" - this is just a placeholder vector
        test_vector = [0.1] * collection_info.config.params.vectors.size  # Create a test vector of correct size

        search_results = await client.query_points(
            collection_name=settings.qdrant_collection,
            query=test_vector,
            limit=3,
            with_payload=True,
            with_vectors=False
        )

        print(f"Search returned {len(search_results.points)} results")
        if search_results.points:
            for i, point in enumerate(search_results.points):
                print(f"  Result {i+1}: Score={point.score}, ID={point.id}")
                print(f"    Payload keys: {list(point.payload.keys()) if point.payload else 'None'}")
                if 'text' in point.payload:
                    print(f"    Text preview: {point.payload['text'][:100]}...")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_qdrant_connection())