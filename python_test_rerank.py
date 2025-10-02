import requests
import json

API_URL = "http://localhost:8888"

def test_health():
    """Test health endpoint"""
    print("=" * 50)
    print("1. Health Check")
    print("=" * 50)
    response = requests.get(f"{API_URL}/health")
    print(json.dumps(response.json(), indent=2))
    print("\n")

def test_us_capital():
    """Test with US capital query (Cohere's example)"""
    print("=" * 50)
    print("2. US Capital Query")
    print("=" * 50)

    payload = {
        "model": "rerank-v3.5",
        "query": "What is the capital of the United States?",
        "top_n": 3,
        "documents": [
            "Carson City is the capital city of the American state of Nevada.",
            "The Commonwealth of the Northern Mariana Islands is a group of islands in the Pacific Ocean. Its capital is Saipan.",
            "Washington, D.C. (also known as simply Washington or D.C., and officially as the District of Columbia) is the capital of the United States. It is a federal district.",
            "Capitalization or capitalisation in English grammar is the use of a capital letter at the start of a word. English usage varies from capitalization in other languages.",
            "Capital punishment has existed in the United States since before the United States was a country. As of 2017, capital punishment is legal in 30 of the 50 states."
        ]
    }

    response = requests.post(f"{API_URL}/v2/rerank", json=payload)
    print(json.dumps(response.json(), indent=2))
    print("\n")

def test_tech_query():
    """Test with tech-related query"""
    print("=" * 50)
    print("3. Tech Query (Python ML)")
    print("=" * 50)

    payload = {
        "model": "rerank-v3.5",
        "query": "What are the benefits of Python for machine learning?",
        "documents": [
            "Python has extensive machine learning libraries like scikit-learn, TensorFlow, and PyTorch.",
            "JavaScript is primarily used for web development and creating interactive websites.",
            "Machine learning requires significant computational resources and data processing capabilities.",
            "Python's simple syntax makes it ideal for data scientists and researchers.",
            "JavaScript has gained popularity for server-side development with Node.js."
        ]
    }

    response = requests.post(f"{API_URL}/v2/rerank", json=payload)
    print(json.dumps(response.json(), indent=2))
    print("\n")

def test_no_top_n():
    """Test without top_n parameter"""
    print("=" * 50)
    print("4. Query without top_n (all results)")
    print("=" * 50)

    payload = {
        "model": "rerank-v3.5",
        "query": "best pizza in New York",
        "documents": [
            "Joe's Pizza has been serving authentic New York slices since 1975.",
            "The weather in New York is cold in winter and hot in summer.",
            "Lombardi's is America's first pizzeria, opened in 1905 in Little Italy.",
            "New York City has a population of over 8 million people.",
            "Prince Street Pizza is famous for its pepperoni square slices."
        ]
    }

    response = requests.post(f"{API_URL}/v2/rerank", json=payload)
    print(json.dumps(response.json(), indent=2))
    print("\n")

def test_scientific_query():
    """Test with scientific query"""
    print("=" * 50)
    print("5. Scientific Query")
    print("=" * 50)

    payload = {
        "query": "How does photosynthesis work?",
        "documents": [
            "Photosynthesis is the process by which plants convert light energy into chemical energy, using carbon dioxide and water to produce glucose and oxygen.",
            "The mitochondria is the powerhouse of the cell, producing ATP through cellular respiration.",
            "Chloroplasts contain chlorophyll, the green pigment that captures light energy for photosynthesis.",
            "DNA stores genetic information in sequences of nucleotides.",
            "Plants require sunlight, water, and carbon dioxide for photosynthesis to occur."
        ],
        "top_n": 3
    }

    response = requests.post(f"{API_URL}/v2/rerank", json=payload)
    print(json.dumps(response.json(), indent=2))
    print("\n")

def test_error_empty_query():
    """Test error handling for empty query"""
    print("=" * 50)
    print("6. Error Test: Empty Query")
    print("=" * 50)

    payload = {
        "query": "",
        "documents": ["test document"]
    }

    response = requests.post(f"{API_URL}/v2/rerank", json=payload)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("\n")

def test_error_empty_docs():
    """Test error handling for empty documents"""
    print("=" * 50)
    print("7. Error Test: Empty Documents")
    print("=" * 50)

    payload = {
        "query": "test query",
        "documents": []
    }

    response = requests.post(f"{API_URL}/v2/rerank", json=payload)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("\n")

if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════╗")
    print("║   Testing Qwen3 Reranking API                  ║")
    print("╚════════════════════════════════════════════════╝")
    print("\n")

    try:
        test_health()
        test_us_capital()
        test_tech_query()
        test_no_top_n()
        test_scientific_query()
        test_error_empty_query()
        test_error_empty_docs()

        print("=" * 50)
        print("✓ Testing Complete!")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Make sure the API is running on http://localhost:8888")
        print("Run: python qwen_rerank_api.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
