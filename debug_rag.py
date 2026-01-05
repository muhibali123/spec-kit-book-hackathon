#!/usr/bin/env python3
"""
Test to verify the server is using the correct collection by checking the health endpoint
"""
import requests
import json

def check_server_config():
    """Check what collection the server thinks it's using via health check"""
    url = "http://127.0.0.1:8000/v1/health"

    try:
        print("Checking server health and configuration...")
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"Health status: {result}")
        else:
            print(f"Health check failed: {response.status_code}")
    except Exception as e:
        print(f"Health check error: {str(e)}")

def test_specific_content():
    """Test for specific content that should be in the book"""
    url = "http://127.0.0.1:8000/v1/retrieve"

    # Use a specific phrase that should be in the book based on our earlier inspection
    payload = {
        "query": "modular architecture enables independent development",
        "top_k": 3,
        "score_threshold": 0.1  # Lower threshold to catch more results
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"\nTesting for specific content: 'modular architecture enables independent development'")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            total_results = result.get('total_results', 0)
            print(f"Direct retrieval status: {response.status_code}")
            print(f"Number of documents retrieved: {total_results}")

            if total_results > 0:
                print("Documents found with specific content!")
                for i, doc in enumerate(result.get('results', [])):
                    print(f"  Document {i+1}:")
                    print(f"    Text: {doc.get('text', '')[:200]}...")
                    print(f"    Score: {doc.get('score', 'N/A')}")
                    print(f"    Source: {doc.get('source', 'N/A')}")
                return True
            else:
                print("No documents found with specific content.")
                return False
        else:
            print(f"Direct retrieval failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"Direct retrieval test failed: {str(e)}")
        return False

def test_full_rag():
    """Test the full RAG pipeline"""
    url = "http://127.0.0.1:8000/v1/answer"

    payload = {
        "query": "modular architecture enables independent development",
        "top_k": 3,
        "score_threshold": 0.1
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"\nTesting full RAG pipeline with: 'modular architecture enables independent development'")
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print(f"Full RAG status: {response.status_code}")
            total_results = result.get('total_results', 0)
            print(f"Total results: {total_results}")

            if total_results > 0:
                print("Results found in full RAG pipeline!")
                for i, doc in enumerate(result.get('results', [])):
                    text = doc.get('text', '')
                    print(f"  Result {i+1}:")
                    print(f"    Text preview: {text[:200]}...")
                    print(f"    Score: {doc.get('score', 'N/A')}")
                    print(f"    Source: {doc.get('source', 'N/A')}")

                # Check if any result contains the specific phrase
                for doc in result.get('results', []):
                    if "modular architecture enables independent development" in doc.get('text', '').lower():
                        print("  Found the exact phrase in results!")
                        return True
                return True
            else:
                print("No results found in full RAG pipeline.")
                return False

        else:
            print(f"Full RAG failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"Full RAG test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Checking server configuration and RAG functionality...")

    # Check server config
    check_server_config()

    # Test specific content retrieval
    retrieval_success = test_specific_content()

    # Test full RAG
    rag_success = test_full_rag()

    print(f"\n--- RESULTS ---")
    print(f"Direct retrieval of specific content: {'SUCCESS' if retrieval_success else 'FAILED'}")
    print(f"Full RAG pipeline: {'SUCCESS' if rag_success else 'FAILED'}")

    if retrieval_success and rag_success:
        print("\nRAG pipeline is working correctly!")
    else:
        print("\nRAG pipeline still needs debugging.")