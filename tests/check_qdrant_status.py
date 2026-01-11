#!/usr/bin/env python3
"""
Script to check if Qdrant collection has been populated with vectors.
"""
import os
import sys
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

def check_qdrant_status():
    # Get Qdrant configuration from environment
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')
    collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'documents')

    print(f"Qdrant URL: {qdrant_url}")
    print(f"Collection name: {collection_name}")

    if not qdrant_url or not qdrant_api_key:
        print("Error: QDRANT_URL and QDRANT_API_KEY must be set in environment variables")
        return False

    try:
        # Initialize Qdrant client
        client = QdrantClient(
            url=qdrant_url.replace("https://", "").replace(":6333", ""),  # Remove protocol and port for cloud
            api_key=qdrant_api_key,
            port=6333 if "localhost" in qdrant_url else None,
            https=True if "https://" in qdrant_url else False
        )

        # List all collections
        collections = client.get_collections()
        print(f"Available collections: {[col.name for col in collections.collections]}")

        # Check if our collection exists
        collection_exists = any(col.name == collection_name for col in collections.collections)

        if collection_exists:
            # Get collection info
            collection_info = client.get_collection(collection_name)
            print(f"Collection '{collection_name}' exists")
            print(f"Points count: {collection_info.points_count}")
            print(f"Vector size: {collection_info.config.params.vectors.size if collection_info.config.params.vectors else 'N/A'}")
            print(f"Distance: {collection_info.config.params.vectors.distance if collection_info.config.params.vectors else 'N/A'}")

            if collection_info.points_count > 0:
                print(f"✅ Collection has {collection_info.points_count} vectors - RAG should work!")

                # Sample a few points to verify content
                sample_points = client.scroll(
                    collection_name=collection_name,
                    limit=2
                )
                print("\nSample points:")
                for i, (point, _) in enumerate(sample_points[0]):
                    print(f"Point {i+1}:")
                    print(f"  ID: {point.id}")
                    print(f"  Text preview: {point.payload.get('text', '')[:100]}...")
                    print(f"  Metadata: {point.payload.get('metadata', {})}")
            else:
                print(f"❌ Collection exists but has 0 vectors - ingestion needed")
        else:
            print(f"❌ Collection '{collection_name}' does not exist - ingestion needed")

        return collection_exists and collection_info.points_count > 0 if collection_exists else False

    except Exception as e:
        print(f"Error connecting to Qdrant: {str(e)}")
        return False

if __name__ == "__main__":
    check_qdrant_status()