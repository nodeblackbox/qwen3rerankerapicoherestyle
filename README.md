# Qwen3 Reranking API

A standalone reranking API using Qwen3-Reranker-0.6B that provides a Cohere-compatible interface for document reranking tasks.

## Files

- **`qwen_rerank_api.py`** - Main FastAPI application with GPU-accelerated Qwen3 reranker
- **`test_rerank_api.sh`** - Bash script with comprehensive API tests
- **`python_test_rerank.py`** - Python script with the same test functionality

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn torch transformers pydantic
```

For GPU support, ensure you have CUDA installed and PyTorch with CUDA support.

### 2. Start the API

```bash
python qwen_rerank_api.py
```

The API will start on `http://localhost:8888` and automatically download the Qwen3-Reranker-0.6B model on first run.

### 3. Test the API

#### Option A: Bash Script
```bash
chmod +x test_rerank_api.sh
./test_rerank_api.sh
```

#### Option B: Python Script
```bash
pip install requests
python python_test_rerank.py
```

#### Option C: Manual Test
```bash
curl -X POST http://localhost:8888/v2/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rerank-v3.5",
    "query": "What is the capital of the United States?",
    "top_n": 3,
    "documents": [
      "Washington, D.C. is the capital of the United States.",
      "New York City is the largest city in the United States.",
      "Los Angeles is a major city on the west coast."
    ]
  }'
```

## API Endpoints

### POST `/v2/rerank`
Cohere-compatible reranking endpoint.

**Request:**
```json
{
  "model": "rerank-v3.5",
  "query": "What is the capital of the United States?",
  "documents": [
    "Washington, D.C. is the capital of the United States.",
    "New York City is the largest city in the United States."
  ],
  "top_n": 3
}
```

**Response:**
```json
{
  "results": [
    {"index": 0, "relevance_score": 0.9876},
    {"index": 1, "relevance_score": 0.5432}
  ],
  "id": "uuid-here",
  "meta": {
    "api_version": {"version": "2", "is_experimental": false},
    "billed_units": {"search_units": 1}
  }
}
```

### GET `/health`
Health check endpoint that returns API status and model information.

## Features

- **GPU Acceleration**: Automatically uses CUDA when available with FP16 optimization
- **Cohere Compatibility**: Matches Cohere's reranking API interface exactly
- **Batch Processing**: Processes multiple documents efficiently
- **Error Handling**: Comprehensive validation and error responses
- **CORS Support**: Ready for web application integration

## Configuration

The API uses the following default settings:
- **Model**: Qwen/Qwen3-Reranker-0.6B
- **Port**: 8888
- **Max Length**: 8192 tokens
- **GPU**: Auto-detected with FP16 when available

## Model Details

The Qwen3-Reranker-0.6B is a cross-encoder model specifically designed for reranking tasks. It provides more accurate relevance scores than embedding-based approaches by considering the full query-document interaction.

## Troubleshooting

### Error: "Cannot handle batch sizes > 1 if no padding token is defined"

**Solution:** This was fixed by properly configuring the padding token:
- Set `tokenizer.pad_token = tokenizer.eos_token`
- Set `tokenizer.pad_token_id = tokenizer.eos_token_id` (ID: 151643)
- Pass `pad_token_id` parameter to model initialization
- Enable `return_attention_mask=True` in tokenizer.pad()

### Error: "IndexError: too many indices for tensor"

**Solution:** Use `AutoModelForCausalLM` instead of `AutoModelForSequenceClassification`. The Qwen3-Reranker uses a causal LM architecture, not a sequence classification head.

### Warning: "`torch_dtype` is deprecated"

**Note:** This is a non-critical warning. Future versions should use `dtype` instead of `torch_dtype` parameter.

## Technical Implementation Notes

### Padding Configuration
- **Pad Token:** `<|endoftext|>` (ID: 151643)
- **Padding Side:** Left (required for causal LM)
- **Max Length:** 8192 tokens
- **Embedding Dimension:** 1024

### Scoring Method
The model evaluates "yes" vs "no" token probabilities:
1. Format input with system prompt asking yes/no question
2. Get logits at final position: `model(**inputs).logits[:, -1, :]`
3. Extract "yes" and "no" token logits
4. Apply log-softmax and return probability of "yes" as relevance score

### Reference Implementation
Based on the official Qwen3-Reranker usage from Hugging Face model card.
