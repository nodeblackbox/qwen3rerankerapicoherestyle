import requests
import json

# Test the reranking API
def test_rerank():
    url = "http://localhost:8888/v2/rerank"
    
    payload = {
        "model": "rerank-v3.5",
        "query": "What is the capital of China?",
        "documents": [
            "The capital of China is Beijing.",
            "China is a large country in Asia.",
            "Gravity is a force that attracts two bodies towards each other.",
            "Beijing is a major city with a rich history."
        ],
        "top_n": 3
    }
    
    print("Testing reranking API...")
    print(f"Query: {payload['query']}")
    print(f"Documents: {len(payload['documents'])} documents")
    print()
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Success!")
        print(json.dumps(result, indent=2))
        print()
        print("Top ranked documents:")
        for i, r in enumerate(result['results'], 1):
            doc_idx = r['index']
            score = r['relevance_score']
            print(f"{i}. [Score: {score:.4f}] {payload['documents'][doc_idx]}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)

def test_health():
    url = "http://localhost:8888/health"
    print("\nTesting health endpoint...")
    response = requests.get(url)
    if response.status_code == 200:
        print("✓ Health check passed!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"✗ Health check failed: {response.status_code}")

if __name__ == "__main__":
    test_health()
    print("\n" + "="*60 + "\n")
    test_rerank()
