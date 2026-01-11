#!/usr/bin/env python3
"""
Final test to verify RAG functionality after server restart
"""
import requests
import json

def test_rag_with_knowledge():
    """Test RAG with a knowledge-based query"""
    url = "http://127.0.0.1:8000/v1/answer"

    # Test query about the book content
    payload = {
        "query": "What is Physical AI and Humanoid Robotics about?",
        "top_k": 3,
        "score_threshold": 0.3
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print("Testing knowledge-based query: 'What is Physical AI and Humanoid Robotics about?'")
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")

            # Check if the response contains retrieved context
            results = result.get('results', [])
            if results and len(results) > 0:
                print(f"\n✅ SUCCESS: Found {len(results)} relevant documents!")

                # Check if results contain actual content vs. generic responses
                has_real_content = False
                for i, doc in enumerate(results):
                    text = doc.get('text', '').lower()
                    if ("don't have enough information" not in text and
                        "no information from the provided context" not in text and
                        "no relevant documents" not in text):
                        has_real_content = True
                        print(f"\nDocument {i+1}:")
                        print(f"  Text preview: {doc.get('text', '')[:300]}...")
                        print(f"  Score: {doc.get('score', 'N/A')}")
                        print(f"  Source: {doc.get('source', 'N/A')}")

                if has_real_content:
                    print("\n🎉 RAG pipeline is working correctly! The system is retrieving relevant context from the ingested documents.")
                    return True
                else:
                    print("\n❌ The system is returning generic responses instead of using retrieved context.")
                    return False
            else:
                print("\n❌ No documents were retrieved.")
                return False

        else:
            print(f"❌ Query failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return False

def test_direct_retrieval():
    """Test direct retrieval to see if documents are found"""
    url = "http://127.0.0.1:8000/v1/retrieve"

    payload = {
        "query": "Physical AI and Humanoid Robotics",
        "top_k": 3,
        "score_threshold": 0.3
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print("\nTesting direct retrieval: 'Physical AI and Humanoid Robotics'")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"Direct retrieval status: {response.status_code}")
            print(f"Number of documents retrieved: {result.get('total_results', 0)}")

            if result.get('total_results', 0) > 0:
                print("Documents found in direct retrieval!")
                for i, doc in enumerate(result.get('results', [])[:2]):
                    print(f"  Document {i+1}: {doc.get('text', '')[:150]}...")
                return True
            else:
                print("No documents found in direct retrieval.")
                return False
        else:
            print(f"Direct retrieval failed with status {response.status_code}")
            return False

    except Exception as e:
        print(f"Direct retrieval test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running final RAG functionality test...")

    # Test direct retrieval first
    retrieval_success = test_direct_retrieval()

    # Test full RAG pipeline
    rag_success = test_rag_with_knowledge()

    print(f"\n--- FINAL RESULTS ---")
    print(f"Direct retrieval: {'✅ WORKING' if retrieval_success else '❌ NOT WORKING'}")
    print(f"Full RAG pipeline: {'✅ WORKING' if rag_success else '❌ NOT WORKING'}")

    if retrieval_success and rag_success:
        print("\n🎉 SUCCESS: RAG pipeline is fully functional!")
    else:
        print("\n⚠️  RAG pipeline needs further debugging.")