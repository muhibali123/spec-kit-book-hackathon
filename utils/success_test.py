#!/usr/bin/env python3
"""
Simple test to confirm RAG is working
"""
import requests
import json

def test():
    print("Testing RAG functionality...")

    # Test direct retrieval
    url = "http://127.0.0.1:8000/v1/retrieve"
    payload = {"query": "Physical AI", "top_k": 1, "score_threshold": 0.0}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Direct retrieval status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Direct retrieval results: {result.get('total_results', 0)}")

        if result.get('total_results', 0) > 0:
            first_result = result['results'][0]
            print(f"Sample text: {first_result.get('text', '')[:100]}...")
            print("SUCCESS: Retrieval is working!")
        else:
            print("No results found but no error")
    else:
        print(f"Direct retrieval failed: {response.text}")

    # Test RAG answer
    url = "http://127.0.0.1:8000/v1/answer"
    payload = {"query": "What is Physical AI?", "top_k": 1, "score_threshold": 0.0}

    response = requests.post(url, json=payload, headers=headers, timeout=60)
    print(f"RAG answer status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"RAG answer results: {result.get('total_results', 0)}")

        if result.get('total_results', 0) > 0:
            first_result = result['results'][0]
            print(f"Sample answer text: {first_result.get('text', '')[:100]}...")
            print("SUCCESS: Full RAG pipeline is working!")
        else:
            print("RAG returned no results but no error")
    else:
        print(f"RAG answer failed: {response.text}")

    print("Test completed!")

if __name__ == "__main__":
    test()