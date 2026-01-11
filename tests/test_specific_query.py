#!/usr/bin/env python3
"""
Test script to verify RAG functionality with specific queries
"""
import requests
import json

def test_specific_query(query_text, description):
    """Test a specific query against the RAG system"""
    url = "http://127.0.0.1:8000/v1/answer"

    payload = {
        "query": query_text,
        "top_k": 5,
        "score_threshold": 0.3
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"\nTesting specific query: '{query_text}' ({description})")
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print(f"Status: {response.status_code}")

            # Check if we got results
            results = result.get('results', [])
            print(f"Number of results: {len(results)}")

            if results:
                print("First result preview:")
                first_result = results[0]
                print(f"  Text: {first_result.get('text', '')[:200]}...")
                print(f"  Score: {first_result.get('score', 'N/A')}")
                print(f"  Source: {first_result.get('source', 'N/A')}")

                # Check if the response contains actual retrieved content vs. generic response
                text = first_result.get('text', '').lower()
                if "don't have enough information" in text or "no information from the provided context" in text:
                    print("  ❌ Result appears to be a generic response, not from retrieved context")
                else:
                    print("  ✅ Result appears to contain actual retrieved content")
            else:
                print("  No results returned")

        else:
            print(f"Query failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")

def test_retrieval_only():
    """Test the retrieval service directly if available"""
    url = "http://127.0.0.1:8000/v1/retrieval/search"  # Try retrieval endpoint

    payload = {
        "query": "Physical AI and Humanoid Robotics",
        "top_k": 3,
        "score_threshold": 0.3
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"\nTesting retrieval endpoint: '{payload['query']}'")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"Retrieval successful! Status: {response.status_code}")
            print(f"Number of retrieved documents: {len(result.get('documents', []))}")
        else:
            print(f"Retrieval endpoint not available or failed with status {response.status_code}")

    except Exception as e:
        print(f"Retrieval test failed: {str(e)}")

if __name__ == "__main__":
    # Test various queries that should match content from the book
    test_specific_query("Physical AI and Humanoid Robotics", "Main book topic")
    test_specific_query("defining Physical AI", "Specific chapter title")
    test_specific_query("humanoid robotics", "Key concept")
    test_specific_query("chapter 1", "Chapter reference")
    test_specific_query("what are the main topics covered", "General book content")

    # Test the retrieval endpoint if it exists
    test_retrieval_only()