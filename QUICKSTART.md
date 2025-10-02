# Quick Start Guide

## 🚀 Start the API (Do this first!)

```bash
source /c/Users/nasan/Miniconda3/etc/profile.d/conda.sh
conda activate rag
python qwen_rerank_api.py
```

**Wait for this message:**
```
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

---

## ✅ Test Basic Reranking

Open a **new terminal** and run:

```bash
conda activate rag
python python_test_rerank.py
```

**Expected:** 7 tests pass (5 successful, 2 intentional errors)

---

## 🖱️ Test UI Element Reranking

With the API still running, in a **new terminal**:

```bash
conda activate rag
python test_claude_ui.py
```

**Expected:** 10 UI interaction tests with accuracy report

---

## 📝 What Got Fixed

1. **Padding token** now properly configured (ID: 151643)
2. **Model architecture** changed to `AutoModelForCausalLM`
3. **Attention masks** enabled for proper batching

---

## 🎯 Use Cases

### Document Reranking
```python
import requests

requests.post("http://localhost:8888/v2/rerank", json={
    "query": "Python machine learning",
    "documents": ["PyTorch tutorial", "Java basics", "ML with Python"],
    "top_n": 3
})
```

### UI Element Prediction
```python
from test_ui_reranking import rerank_ui_elements

ranked = rerank_ui_elements(
    task="Type a message",
    elements=ui_elements,
    top_n=5
)

best_element = ranked[0]['element']  # Click this!
```

---

## 📚 Documentation

- **`README.md`** - Main API documentation
- **`README_UI_RERANKING.md`** - UI reranking guide
- **`SUMMARY.md`** - Complete implementation details

---

## 🐛 Troubleshooting

**API won't start?**
- Check if port 8888 is in use
- Ensure conda environment `rag` is activated
- Verify CUDA/PyTorch installation

**Tests fail with connection error?**
- Make sure API is running first
- Check firewall isn't blocking port 8888

**Low accuracy on UI tests?**
- Element descriptions might need improvement
- Try with different/clearer task descriptions

---

**Status:** ✅ **All Systems Working**

Your Qwen3 reranking API is ready to use!
