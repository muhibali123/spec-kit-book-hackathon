#!/usr/bin/env python3
"""
Simple test to verify RAG functionality after Qdrant client fix
"""
import requests
import json

def test_direct_retrieval():
    """Test direct retrieval to see if documents are found"""
    url = "http://127.0.0.1:8000/v1/retrieve"

    # Use a specific phrase that should be in the book based on our earlier inspection
    payload = {
        "query": "modular architecture enables independent development",
        "top_k": 3,
        "score_threshold": 0.1
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print("Testing direct retrieval with: 'modular architecture enables independent development'")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            total_results = result.get('total_results', 0)
            print(f"Number of documents retrieved: {total_results}")

            if total_results > 0:
                print("SUCCESS: Documents found in direct retrieval!")
                for i, doc in enumerate(result.get('results', [])):
                    print(f"  Document {i+1}:")
                    print(f"    Text preview: {doc.get('text', '')[:200]}...")
                    print(f"    Score: {doc.get('score', 'N/A')}")
                    print(f"    Source: {doc.get('source', 'N/A')}")
                return True
            else:
                print("ERROR: No documents found in direct retrieval.")
                print(f"Full response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"ERROR: Direct retrieval failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"ERROR: Direct retrieval test failed: {str(e)}")
        return False

def test_rag_answer():
    """Test the full RAG answer endpoint"""
    url = "http://127.0.0.1:8000/v1/answer"

    payload = {
        "query": "What is Physical AI?",
        "top_k": 3,
        "score_threshold": 0.3
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"\nTesting RAG answer with: 'What is Physical AI?'")
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            total_results = result.get('total_results', 0)
            print(f"Total results: {total_results}")

            if total_results > 0:
                print("SUCCESS: Results found in RAG pipeline!")
                for i, doc in enumerate(result.get('results', [])):
                    text = doc.get('text', '')
                    print(f"  Result {i+1}:")
                    print(f"    Text preview: {text[:300]}...")
                    print(f"    Score: {doc.get('score', 'N/A')}")
                    print(f"    Source: {doc.get('source', 'N/A')}")

                    # Check if it's actual book content vs generic response
                    if "don't have enough information" not in text.lower() and "no information" not in text.lower():
                        print("    This appears to be actual book content!")

                return True
            else:
                print("ERROR: No results found in RAG pipeline.")
                print(f"Full response: {json.dumps(result, indent=2)}")
                return False

        else:
            print(f"ERROR: RAG answer failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"ERROR: RAG answer test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Simple RAG functionality test after Qdrant client fix...")

    # Test direct retrieval
    retrieval_success = test_direct_retrieval()

    # Test full RAG pipeline
    rag_success = test_rag_answer()

    print(f"\n--- RESULTS ---")
    print(f"Direct retrieval: {'SUCCESS' if retrieval_success else 'FAILED'}")
    print(f"Full RAG pipeline: {'SUCCESS' if rag_success else 'FAILED'}")

    if retrieval_success and rag_success:
        print("SUCCESS: RAG pipeline is fully functional!")
    else:
        print("RAG pipeline still has issues.")