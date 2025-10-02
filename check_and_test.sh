#!/bin/bash

echo "========================================"
echo "Qwen3 Reranking API Test Runner"
echo "========================================"
echo ""

# Check if API is running
if curl -s http://localhost:8888/health > /dev/null 2>&1; then
    echo "✅ API is running!"
    echo ""
    echo "Running UI reranking tests..."
    echo ""
    python test_claude_ui.py
else
    echo "❌ API is NOT running!"
    echo ""
    echo "Please start the API first:"
    echo ""
    echo "  Open a NEW terminal and run:"
    echo "  ---------------------------------"
    echo "  cd /c/Users/nasan/Downloads/qwen3rerankerapicoherestyle"
    echo "  conda activate rag"
    echo "  python qwen_rerank_api.py"
    echo "  ---------------------------------"
    echo ""
    echo "Wait for this message:"
    echo "  INFO:     Uvicorn running on http://0.0.0.0:8888"
    echo ""
    echo "Then run this script again:"
    echo "  bash check_and_test.sh"
    echo ""
fi
