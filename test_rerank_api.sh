#!/bin/bash

# Test script for Qwen3 Reranking API
# Make sure the API is running on http://localhost:8888

API_URL="http://localhost:8888"

echo "=========================================="
echo "Testing Qwen3 Reranking API"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "1. Health Check"
echo "---"
curl -s "${API_URL}/health" | jq '.'
echo ""
echo ""

# Test 2: US Capital Example (matching Cohere's example)
echo "2. US Capital Query"
echo "---"
curl -s -X POST "${API_URL}/v2/rerank" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | jq '.'
echo ""
echo ""

# Test 3: Tech Query
echo "3. Tech Query (Python vs JavaScript)"
echo "---"
curl -s -X POST "${API_URL}/v2/rerank" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rerank-v3.5",
    "query": "What are the benefits of Python for machine learning?",
    "documents": [
      "Python has extensive machine learning libraries like scikit-learn, TensorFlow, and PyTorch.",
      "JavaScript is primarily used for web development and creating interactive websites.",
      "Machine learning requires significant computational resources and data processing capabilities.",
      "Python'\''s simple syntax makes it ideal for data scientists and researchers.",
      "JavaScript has gained popularity for server-side development with Node.js."
    ]
  }' | jq '.'
echo ""
echo ""

# Test 4: Without top_n (return all ranked)
echo "4. Query without top_n (all results)"
echo "---"
curl -s -X POST "${API_URL}/v2/rerank" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rerank-v3.5",
    "query": "best pizza in New York",
    "documents": [
      "Joe'\''s Pizza has been serving authentic New York slices since 1975.",
      "The weather in New York is cold in winter and hot in summer.",
      "Lombardi'\''s is America'\''s first pizzeria, opened in 1905 in Little Italy.",
      "New York City has a population of over 8 million people.",
      "Prince Street Pizza is famous for its pepperoni square slices."
    ]
  }' | jq '.'
echo ""
echo ""

# Test 5: Scientific Query
echo "5. Scientific Query"
echo "---"
curl -s -X POST "${API_URL}/v2/rerank" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does photosynthesis work?",
    "documents": [
      "Photosynthesis is the process by which plants convert light energy into chemical energy, using carbon dioxide and water to produce glucose and oxygen.",
      "The mitochondria is the powerhouse of the cell, producing ATP through cellular respiration.",
      "Chloroplasts contain chlorophyll, the green pigment that captures light energy for photosynthesis.",
      "DNA stores genetic information in sequences of nucleotides.",
      "Plants require sunlight, water, and carbon dioxide for photosynthesis to occur."
    ],
    "top_n": 3
  }' | jq '.'
echo ""
echo ""

# Test 6: Empty query (error test)
echo "6. Error Test: Empty Query"
echo "---"
curl -s -X POST "${API_URL}/v2/rerank" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "",
    "documents": ["test document"]
  }' | jq '.'
echo ""
echo ""

# Test 7: Empty documents (error test)
echo "7. Error Test: Empty Documents"
echo "---"
curl -s -X POST "${API_URL}/v2/rerank" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test query",
    "documents": []
  }' | jq '.'
echo ""
echo ""

echo "=========================================="
echo "Testing Complete!"
echo "=========================================="
