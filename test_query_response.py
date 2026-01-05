#!/usr/bin/env python3
"""
Test to see the actual format of query_points response
"""
import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_query_response():
    """Test the actual response format from query_points"""
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

    # Get collection info to know vector size
    collection_info = await client.get_collection(settings.qdrant_collection)
    vector_size = collection_info.config.params.vectors.size
    print(f"Vector size: {vector_size}")

    # Create a test vector
    test_vector = [0.1] * vector_size

    # Try the query_points method directly
    try:
        response = await client.query_points(
            collection_name=settings.qdrant_collection,
            query=test_vector,
            limit=2,
            with_payload=True,
            with_vectors=False
        )

        print(f"Response type: {type(response)}")
        print(f"Response dir: {dir(response)}")
        print(f"Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")

        # Check if it has 'points' attribute
        if hasattr(response, 'points'):
            print(f"Has 'points' attribute: {len(response.points)} results")
            for i, point in enumerate(response.points):
                print(f"  Point {i+1}: id={point.id}, score={point.score}, payload keys={list(point.payload.keys()) if hasattr(point.payload, 'keys') else 'N/A'}")
        else:
            print(f"Does NOT have 'points' attribute")
            # Print the response to see its structure
            print(f"Response content: {response}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_query_response())