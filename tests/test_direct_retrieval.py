#!/usr/bin/env python3
"""
Test script to verify direct retrieval functionality
"""
import requests
import json

def test_direct_retrieval():
    """Test the retrieval endpoint directly"""
    url = "http://127.0.0.1:8000/v1/retrieve"

    payload = {
        "query": "Physical AI and Humanoid Robotics",
        "top_k": 5,
        "score_threshold": 0.3
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"Testing direct retrieval: '{payload['query']}'")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"Retrieval successful! Status: {response.status_code}")
            print(f"Number of retrieved documents: {result.get('total_results', 0)}")

            results = result.get('results', [])
            if results:
                print("\nRetrieved documents:")
                for i, doc in enumerate(results):
                    print(f"\nDocument {i+1}:")
                    print(f"  ID: {doc.get('id', 'N/A')}")
                    print(f"  Text preview: {doc.get('text', '')[:150]}...")
                    print(f"  Score: {doc.get('score', 'N/A')}")
                    print(f"  Source: {doc.get('source', 'N/A')}")
                    print(f"  Metadata keys: {list(doc.get('metadata', {}).keys())}")
            else:
                print("No documents retrieved")
        else:
            print(f"Retrieval failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Retrieval test failed: {str(e)}")

if __name__ == "__main__":
    test_direct_retrieval()