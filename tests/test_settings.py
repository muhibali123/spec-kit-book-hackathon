#!/usr/bin/env python3
"""
Test to check if settings are reading environment variables correctly
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from the backend
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Add backend to path to import settings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_settings():
    # Import settings after loading environment
    from backend.src.config.settings import settings

    print("=== Environment Variables ===")
    print(f"QDRANT_COLLECTION: {os.getenv('QDRANT_COLLECTION')}")
    print(f"QDRANT_COLLECTION_NAME: {os.getenv('QDRANT_COLLECTION_NAME')}")
    print(f"QDRANT_URL: {os.getenv('QDRANT_URL')}")
    print(f"QDRANT_API_KEY: {'SET' if os.getenv('QDRANT_API_KEY') else 'NOT SET'}")

    print("\n=== Settings Values ===")
    print(f"settings.qdrant_collection: {settings.qdrant_collection}")
    print(f"settings.qdrant_url: {settings.qdrant_url}")
    print(f"settings.qdrant_api_key: {'SET' if settings.qdrant_api_key else 'NOT SET'}")

    # Check if the environment variables match the settings
    env_collection = os.getenv('QDRANT_COLLECTION') or os.getenv('QDRANT_COLLECTION_NAME', 'documents')
    print(f"\nExpected collection from environment: {env_collection}")
    print(f"Actual collection in settings: {settings.qdrant_collection}")
    print(f"Match: {env_collection == settings.qdrant_collection}")

if __name__ == "__main__":
    test_settings()