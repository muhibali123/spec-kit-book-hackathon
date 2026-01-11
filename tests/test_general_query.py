#!/usr/bin/env python3
"""
Test with general queries to see if retrieval works at all
"""
import requests
import json

def test_general_queries():
    """Test with various general queries"""
    url = "http://127.0.0.1:8000/v1/retrieve"

    queries = [
        "Physical AI",  # Main topic
        "Humanoid Robotics",  # Main topic
        "robot",  # Common term
        "artificial intelligence",  # Common term
        "chapter",  # Common term in docs
        "modular",  # From our earlier test
        "architecture",  # From our earlier test
    ]

    headers = {
        "Content-Type": "application/json"
    }

    for query in queries:
        print(f"\nTesting query: '{query}'")

        payload = {
            "query": query,
            "top_k": 3,
            "score_threshold": 0.1  # Lower threshold
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()
                total_results = result.get('total_results', 0)
                print(f"  Status: {response.status_code}")
                print(f"  Results: {total_results}")

                if total_results > 0:
                    print("  ✅ Found results!")
                    for i, doc in enumerate(result.get('results', [])):
                        print(f"    Result {i+1}: Score={doc.get('score', 'N/A')}")
                        print(f"      Text preview: {doc.get('text', '')[:100]}...")
                    return True  # Found results
            else:
                print(f"  ❌ Failed with status: {response.status_code}")

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    return False

def test_with_high_score_threshold():
    """Test with higher score threshold to see if we get results"""
    url = "http://127.0.0.1:8000/v1/retrieve"

    payload = {
        "query": "Physical AI",  # Main topic
        "top_k": 5,
        "score_threshold": 0.0  # Very low threshold to catch anything
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"\nTesting with very low threshold for 'Physical AI':")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            total_results = result.get('total_results', 0)
            print(f"  Status: {response.status_code}")
            print(f"  Results: {total_results}")

            if total_results > 0:
                print("  ✅ Found results with low threshold!")
                for i, doc in enumerate(result.get('results', [])):
                    print(f"    Result {i+1}: Score={doc.get('score', 'N/A')}")
                    print(f"      Text preview: {doc.get('text', '')[:150]}...")
            else:
                print("  ❌ Still no results with very low threshold")
        else:
            print(f"  ❌ Failed with status: {response.status_code}")

    except Exception as e:
        print(f"  ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("Testing general queries to check if retrieval works...")

    found_results = test_general_queries()

    if not found_results:
        test_with_high_score_threshold()

    if found_results:
        print(f"\n✅ Retrieval is working! Found results for at least one query.")
    else:
        print(f"\n❌ Retrieval still not finding results.")