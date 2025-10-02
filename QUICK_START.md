# UI Element Reranking API - Quick Start Guide

## Starting the API Server

```bash
source /c/Users/nasan/Miniconda3/etc/profile.d/conda.sh
conda activate rag
python ui_rerank_api.py
```

The API will start on `http://localhost:8889`

---

## API Endpoints

### 1. Rerank UI Elements
**POST** `/ui/rerank`

Ranks UI elements based on a natural language task description.

**Request Body:**
```json
{
  "task": "click on sign up button",
  "elements": [
    {
      "type": "ButtonControl",
      "name": "Sign up",
      "bounds": {"left": 1144, "top": 97, "right": 1215, "bottom": 125}
    },
    {
      "type": "ButtonControl", 
      "name": "Preview",
      "bounds": {"left": 1218, "top": 97, "right": 1293, "bottom": 125}
    }
  ],
  "top_n": 5,
  "expected_element": "Sign up"  // Optional: for accuracy tracking
}
```

**Response:**
```json
{
  "request_id": "abc123...",
  "results": [
    {
      "index": 0,
      "element": {
        "type": "ButtonControl",
        "name": "Sign up",
        "bounds": {"left": 1144, "top": 97, "right": 1215, "bottom": 125}
      },
      "description": "Type: Button | Name: 'Sign up' | Position: (1144, 97)",
      "relevance_score": 0.9912
    }
  ],
  "inference_time_ms": 313.7,
  "accuracy": 1.0
}
```

---

### 2. Get Statistics
**GET** `/ui/stats`

Returns API performance statistics.

**Response:**
```json
{
  "total_requests": 150,
  "total_elements_ranked": 6450,
  "recent_accuracy": 0.95,
  "recent_correct": 19,
  "recent_total": 20,
  "avg_inference_time_ms": 270.5,
  "model": "Qwen/Qwen3-Reranker-0.6B",
  "device": "cuda"
}
```

---

### 3. Get Request History
**GET** `/ui/history?limit=20`

Returns recent ranking requests.

**Response:**
```json
{
  "history": [
    {
      "request_id": "abc123...",
      "timestamp": "2025-10-02T14:21:45.123456",
      "task": "click on sign up button",
      "num_elements": 43,
      "top_element": "Sign up",
      "top_score": 0.9912,
      "expected_element": "Sign up",
      "correct": true,
      "accuracy": 1.0,
      "inference_time_ms": 313.7
    }
  ]
}
```

---

### 4. Health Check
**GET** `/health`

Check if the API is ready.

**Response:**
```json
{
  "status": "healthy",
  "model": "Qwen/Qwen3-Reranker-0.6B",
  "device": "cuda",
  "purpose": "UI Element Reranking"
}
```

---

## Python Client Example

```python
import requests

# API configuration
API_URL = "http://localhost:8889/ui/rerank"

# Your UI elements
elements = [
    {
        "type": "ButtonControl",
        "name": "Sign up",
        "bounds": {"left": 1144, "top": 97, "right": 1215, "bottom": 125}
    },
    {
        "type": "ButtonControl",
        "name": "Preview",
        "bounds": {"left": 1218, "top": 97, "right": 1293, "bottom": 125}
    }
]

# Create request
payload = {
    "task": "click on sign up button",
    "elements": elements,
    "top_n": 5
}

# Send request
response = requests.post(API_URL, json=payload)
result = response.json()

# Get top result
top_element = result['results'][0]
print(f"Best match: {top_element['element']['name']}")
print(f"Confidence: {top_element['relevance_score']:.2%}")
print(f"Processing time: {result['inference_time_ms']:.1f}ms")
```

**Output:**
```
Best match: Sign up
Confidence: 99.12%
Processing time: 313.7ms
```

---

## Task Examples

### Good Task Descriptions ✅
- "click on sign up button"
- "publish the form"
- "edit form title"
- "use a template"
- "get help and documentation"
- "preview the form"
- "customize the form"
- "create a new form from scratch"

### Task Tips 💡
1. **Be specific:** "click on sign up button" is better than "sign up"
2. **Use natural language:** Write like you're instructing a human
3. **Include context:** "edit form title" is clearer than just "edit"
4. **Action-oriented:** Start with verbs (click, open, edit, etc.)

---

## Element Format

The API supports flexible element schemas. Minimum required:
- `name` or `type` (at least one)

Optional but recommended:
- `type`: Element type (ButtonControl, TextControl, etc.)
- `name`: Element label/text
- `bounds`: Position (left, top, right, bottom)
- `action`: Possible action (click, input, etc.)
- Any custom fields (they'll be preserved in the response)

**Example minimal element:**
```json
{
  "name": "Sign up"
}
```

**Example detailed element:**
```json
{
  "type": "ButtonControl",
  "name": "Sign up",
  "bounds": {"left": 1144, "top": 97, "right": 1215, "bottom": 125},
  "depth": 13,
  "action": "click",
  "custom_id": "signup-btn-123"
}
```

---

## Integration Examples

### With Selenium
```python
import requests
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://example.com")

# Get all buttons
buttons = driver.find_elements_by_tag_name("button")

# Format for API
elements = [
    {
        "type": "button",
        "name": btn.text,
        "bounds": {
            "left": btn.location['x'],
            "top": btn.location['y'],
            "right": btn.location['x'] + btn.size['width'],
            "bottom": btn.location['y'] + btn.size['height']
        }
    }
    for btn in buttons
]

# Rank elements
response = requests.post("http://localhost:8889/ui/rerank", json={
    "task": "click on sign up",
    "elements": elements,
    "top_n": 1
})

# Click the best match
best_match_index = response.json()['results'][0]['index']
buttons[best_match_index].click()
```

### With Windows UI Automation (pywinauto)
```python
import requests
from pywinauto import Application

app = Application(backend="uia").connect(title="Your App")
window = app.window(title="Your App")

# Get all controls
controls = window.descendants()

# Format for API
elements = [
    {
        "type": ctrl.element_info.control_type,
        "name": ctrl.window_text(),
        "bounds": ctrl.rectangle()._asdict()
    }
    for ctrl in controls if ctrl.is_visible()
]

# Rank and interact
response = requests.post("http://localhost:8889/ui/rerank", json={
    "task": "click on submit button",
    "elements": elements,
    "top_n": 1
})

best_match_index = response.json()['results'][0]['index']
controls[best_match_index].click()
```

---

## Performance Tips 🚀

1. **Batch Processing:** Send all elements at once rather than one-by-one
2. **Filter First:** Remove obviously irrelevant elements (hidden, system controls)
3. **Use top_n:** Only request the number of results you need
4. **GPU Acceleration:** Ensure CUDA is available for best performance
5. **Connection Pooling:** Reuse HTTP connections for multiple requests

---

## Troubleshooting

### API not starting
- Check if conda environment is activated: `conda activate rag`
- Verify dependencies: `pip install fastapi uvicorn transformers torch`
- Check CUDA availability: `python -c "import torch; print(torch.cuda.is_available())"`

### Slow inference
- First request is always slower (model warmup)
- Check GPU utilization: Task Manager → Performance → GPU
- Reduce number of elements if possible
- Ensure FP16 is enabled (automatic with CUDA)

### Low confidence scores
- Improve task descriptions (be more specific)
- Ensure element names/types are meaningful
- Add more context to elements (bounds, actions, etc.)
- Verify elements are actually visible/relevant

---

## Running Tests

```bash
# Run the comprehensive test suite
python test_ui_rerank.py

# View test results
cat TEST_RESULTS.md
```

---

## Further Reading

- See `TEST_RESULTS.md` for detailed performance analysis
- Check `ui_rerank_api.py` for API implementation details
- Model info: [Qwen3-Reranker-0.6B on HuggingFace](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B)

---

**Need help?** Check the API logs in `ui_reranking.log`
