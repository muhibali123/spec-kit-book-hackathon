#!/usr/bin/env python3
"""
Final test script to verify RAG functionality after ingestion with longer timeout
"""
import requests
import json

def test_rag_query():
    # Test the RAG endpoint with a knowledge-based query
    url = "http://127.0.0.1:8000/v1/answer"

    # Test query about the book content
    payload = {
        "query": "tell me about the book",
        "top_k": 3,
        "score_threshold": 0.3
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print("Testing RAG query: 'tell me about the book'")
        print("This may take a while as it involves embedding generation, vector search, and LLM processing...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)  # 60 second timeout

        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Query successful! Status: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")

            # Check if the response contains retrieved context
            if result.get('results') and len(result.get('results', [])) > 0:
                print(f"SUCCESS: Found {len(result['results'])} relevant documents!")
                print("\nRetrieved context snippets:")
                for i, doc in enumerate(result['results']):
                    print(f"\nDocument {i+1}:")
                    print(f"  Text preview: {doc.get('text', '')[:200]}...")
                    print(f"  Score: {doc.get('score', 'N/A')}")
                    print(f"  Source: {doc.get('source', 'N/A')}")
                print("\nRAG pipeline is working correctly! The system is retrieving relevant context from the ingested documents.")
            else:
                print("No relevant documents retrieved - this suggests the RAG pipeline isn't working properly")

        elif response.status_code == 500:
            print(f"Server error: {response.text}")
        else:
            print(f"Query failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print("Request timed out after 60 seconds. This might indicate the RAG pipeline is working but taking very long.")
    except requests.exceptions.ConnectionError:
        print("Cannot connect to backend. Please ensure the backend server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

def test_simple_greeting():
    """Test with a simple greeting to ensure the API is responsive"""
    url = "http://127.0.0.1:8000/v1/answer"

    payload = {
        "query": "hi",
        "top_k": 1,
        "score_threshold": 0.1
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print("\nTesting simple greeting: 'hi'")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"Greeting query successful! Status: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Greeting query failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Greeting test failed: {str(e)}")

if __name__ == "__main__":
    test_simple_greeting()
    test_rag_query()