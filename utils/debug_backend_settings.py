#!/usr/bin/env python3
"""
Debug script to check the actual settings loaded by the backend
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.config.settings import settings

print("Backend Configuration Check:")
print(f"Qdrant URL: {settings.qdrant_url}")
print(f"Qdrant Host: {settings.qdrant_host}")
print(f"Qdrant Port: {settings.qdrant_port}")
print(f"Qdrant Collection: {settings.qdrant_collection}")
print(f"Qdrant API Key: {'SET' if settings.qdrant_api_key else 'NOT SET'}")
print(f"Cohere API Key: {'SET' if settings.cohere_api_key else 'NOT SET'}")
print(f"Cohere Model: {settings.cohere_model}")
print(f"Default Score Threshold: {settings.default_score_threshold}")
print(f"Default Top K: {settings.default_top_k}")