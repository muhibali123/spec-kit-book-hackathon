#!/usr/bin/env python3
"""
Test script to verify RAG functionality after ingestion
"""
import requests
import json

def test_rag_query():
    # Test the RAG endpoint with a knowledge-based query
    url = "http://127.0.0.1:8000/v1/answer"

    # Test query about the book content
    payload = {
        "query": "tell me about the book",
        "top_k": 5,
        "score_threshold": 0.5
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print("Testing RAG query: 'tell me about the book'")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful! Status: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")

            # Check if the response contains retrieved context
            if result.get('results') and len(result.get('results', [])) > 0:
                print(f"✅ Found {len(result['results'])} relevant documents!")
                for i, doc in enumerate(result['results'][:2]):  # Show first 2 results
                    print(f"  Document {i+1}: {doc.get('text', '')[:200]}...")
            else:
                print("❌ No relevant documents retrieved")

        else:
            print(f"❌ Query failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Please ensure the backend server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")

if __name__ == "__main__":
    test_rag_query()