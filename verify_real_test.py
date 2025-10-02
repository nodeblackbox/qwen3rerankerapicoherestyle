"""
VERIFICATION TEST - Proving the reranking actually works
Using completely different UI elements and tasks
"""

import requests
import json

def test_reranking_api():
    """Test with brand new data to prove it's working"""
    
    print("="*80)
    print("VERIFICATION TEST - Proving Real Functionality")
    print("="*80)
    print()
    
    # Test 1: Different application - File Explorer
    print("TEST 1: File Explorer UI")
    print("-" * 80)
    
    file_explorer_elements = [
        "Button: 'Delete File'",
        "Button: 'Copy'",
        "Button: 'Paste'",
        "Text field: 'Search files'",
        "Button: 'New Folder'",
        "Menu: 'File'",
        "Button: 'Upload'",
        "Button: 'Download'"
    ]
    
    task1 = "I want to search for a document"
    
    response = requests.post("http://localhost:8888/v2/rerank", json={
        "query": task1,
        "documents": file_explorer_elements,
        "top_n": 3
    })
    
    if response.status_code == 200:
        results = response.json()['results']
        print(f"Task: {task1}")
        print(f"Top 3 predictions:")
        for i, r in enumerate(results, 1):
            idx = r['index']
            score = r['relevance_score']
            print(f"  {i}. [{score:.4f}] {file_explorer_elements[idx]}")
        
        # Check if search field is #1
        top_elem = file_explorer_elements[results[0]['index']]
        if 'Search' in top_elem:
            print("✅ CORRECT! Identified search field")
        else:
            print(f"❌ WRONG! Got: {top_elem}")
    else:
        print(f"❌ API Error: {response.status_code}")
    
    print()
    
    # Test 2: Email application
    print("TEST 2: Email Application UI")
    print("-" * 80)
    
    email_elements = [
        "Button: 'Send Email'",
        "Button: 'Reply'",
        "Button: 'Forward'",
        "Text area: 'Compose message'",
        "Button: 'Attach file'",
        "Button: 'Delete Email'",
        "Link: 'Inbox'",
        "Link: 'Sent'",
        "Button: 'Mark as Read'"
    ]
    
    task2 = "I need to write a new email"
    
    response = requests.post("http://localhost:8888/v2/rerank", json={
        "query": task2,
        "documents": email_elements,
        "top_n": 3
    })
    
    if response.status_code == 200:
        results = response.json()['results']
        print(f"Task: {task2}")
        print(f"Top 3 predictions:")
        for i, r in enumerate(results, 1):
            idx = r['index']
            score = r['relevance_score']
            print(f"  {i}. [{score:.4f}] {email_elements[idx]}")
        
        top_elem = email_elements[results[0]['index']]
        if 'Compose' in top_elem or 'Send' in top_elem:
            print("✅ CORRECT! Identified compose/send")
        else:
            print(f"❌ WRONG! Got: {top_elem}")
    else:
        print(f"❌ API Error: {response.status_code}")
    
    print()
    
    # Test 3: E-commerce site
    print("TEST 3: Shopping Website UI")
    print("-" * 80)
    
    shopping_elements = [
        "Button: 'Add to Cart'",
        "Button: 'Buy Now'",
        "Link: 'View Cart'",
        "Button: 'Wishlist'",
        "Input: 'Promo Code'",
        "Button: 'Proceed to Checkout'",
        "Link: 'Continue Shopping'",
        "Button: 'Remove Item'"
    ]
    
    task3 = "I want to finalize my purchase"
    
    response = requests.post("http://localhost:8888/v2/rerank", json={
        "query": task3,
        "documents": shopping_elements,
        "top_n": 3
    })
    
    if response.status_code == 200:
        results = response.json()['results']
        print(f"Task: {task3}")
        print(f"Top 3 predictions:")
        for i, r in enumerate(results, 1):
            idx = r['index']
            score = r['relevance_score']
            print(f"  {i}. [{score:.4f}] {shopping_elements[idx]}")
        
        top_elem = shopping_elements[results[0]['index']]
        if 'Checkout' in top_elem or 'Buy Now' in top_elem:
            print("✅ CORRECT! Identified checkout/buy")
        else:
            print(f"❌ WRONG! Got: {top_elem}")
    else:
        print(f"❌ API Error: {response.status_code}")
    
    print()
    
    # Test 4: Random text - proving it's actually ranking
    print("TEST 4: Completely Random Content")
    print("-" * 80)
    
    random_elements = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning involves training models on data",
        "Python is a popular programming language",
        "Pizza is a delicious Italian food",
        "The capital of France is Paris",
        "Neural networks are inspired by the human brain"
    ]
    
    task4 = "Tell me about artificial intelligence and deep learning"
    
    response = requests.post("http://localhost:8888/v2/rerank", json={
        "query": task4,
        "documents": random_elements,
        "top_n": 3
    })
    
    if response.status_code == 200:
        results = response.json()['results']
        print(f"Task: {task4}")
        print(f"Top 3 predictions:")
        for i, r in enumerate(results, 1):
            idx = r['index']
            score = r['relevance_score']
            print(f"  {i}. [{score:.4f}] {random_elements[idx]}")
        
        top_elem = random_elements[results[0]['index']]
        if 'learning' in top_elem.lower() or 'neural' in top_elem.lower():
            print("✅ CORRECT! Identified ML/AI content")
        else:
            print(f"⚠️  Got: {top_elem}")
    else:
        print(f"❌ API Error: {response.status_code}")
    
    print()
    print("="*80)
    print("VERIFICATION COMPLETE")
    print("If you see correct predictions above, the system is REALLY working!")
    print("="*80)


if __name__ == "__main__":
    try:
        # First check if API is running
        health = requests.get("http://localhost:8888/health", timeout=2)
        if health.status_code != 200:
            print("❌ API is not healthy!")
            exit(1)
        
        print("✅ API is running and healthy\n")
        test_reranking_api()
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: API is not running!")
        print("Start it with: python qwen_rerank_api.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")
