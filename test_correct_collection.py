#!/usr/bin/env python3
"""
Test script to verify the correct collection is being used
"""
import os
from qdrant_client import QdrantClient as SyncQdrantClient

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

def test_correct_collection():
    # Get configuration from environment
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')
    collection_name = os.getenv('QDRANT_COLLECTION_NAME', os.getenv('QDRANT_COLLECTION', 'documents'))

    print(f"Using Qdrant URL: {qdrant_url}")
    print(f"Using collection name: {collection_name}")
    print(f"Using API key (first 10 chars): {qdrant_api_key[:10] if qdrant_api_key else 'NOT SET'}...")

    # Initialize Qdrant client with the correct collection
    try:
        # For Qdrant Cloud, we need to use the host without protocol and port
        host = qdrant_url.replace("https://", "").replace(":6333", "")

        client = SyncQdrantClient(
            url=host,
            api_key=qdrant_api_key,
            https=True
        )

        # List collections to see what's available
        collections = client.get_collections()
        print(f"\nAvailable collections in Qdrant:")
        for col in collections.collections:
            print(f"  - {col.name}")

        # Check if our target collection exists
        target_collection_exists = any(col.name == collection_name for col in collections.collections)
        print(f"\nTarget collection '{collection_name}' exists: {target_collection_exists}")

        if target_collection_exists:
            # Get info about our collection
            collection_info = client.get_collection(collection_name)
            print(f"\nCollection '{collection_name}' details:")
            print(f"  Points count: {collection_info.points_count}")
            print(f"  Vector size: {collection_info.config.params.vectors.size}")
            print(f"  Distance: {collection_info.config.params.vectors.distance}")

            if collection_info.points_count > 0:
                # Sample a few points to verify content
                scroll_result = client.scroll(
                    collection_name=collection_name,
                    limit=2
                )

                print(f"\nSample points from '{collection_name}':")
                for i, point in enumerate(scroll_result[0]):
                    print(f"  Point {i+1}:")
                    print(f"    ID: {point.id}")
                    print(f"    Text preview: {point.payload.get('text', '')[:100]}...")
                    print(f"    Source: {point.payload.get('metadata', {}).get('source_file', 'N/A')}")
        else:
            print(f"\nCollection '{collection_name}' does not exist!")
            print("This explains why the RAG system is not finding any documents.")

    except Exception as e:
        print(f"Error connecting to Qdrant: {str(e)}")

if __name__ == "__main__":
    test_correct_collection()