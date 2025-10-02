"""
UI Element Reranking API
Specifically designed for ranking UI elements for agent interactions
Includes logging and accuracy tracking
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import time
import logging
from contextlib import asynccontextmanager
from datetime import datetime
import json

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ui_reranking.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UIReranker:
    """GPU-accelerated reranker for UI elements"""

    def __init__(self, model_name: str = "Qwen/Qwen3-Reranker-0.6B"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.token_false_id = None
        self.token_true_id = None
        self.max_length = 8192
        self.prefix_tokens = None
        self.suffix_tokens = None
        self.is_loaded = False
        
        # Statistics tracking
        self.total_requests = 0
        self.total_elements_ranked = 0
        self.request_history = []

        self.use_gpu = torch.cuda.is_available()
        self.device = "cuda" if self.use_gpu else "cpu"

        logger.info(f"Initializing UI reranker on: {self.device}")
        if self.use_gpu:
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    def format_ui_element(self, element: Dict[str, Any]) -> str:
        """Format UI element for reranking"""
        parts = []
        
        if 'type' in element:
            elem_type = element['type'].replace('Control', '')
            parts.append(f"Type: {elem_type}")
        
        if 'name' in element and element['name']:
            parts.append(f"Name: '{element['name']}'")
        
        if 'bounds' in element:
            bounds = element['bounds']
            if bounds.get('left', 0) > 0:
                parts.append(f"Position: ({bounds.get('left')}, {bounds.get('top')})")
        
        if 'action' in element:
            parts.append(f"Action: {element['action']}")
        
        return " | ".join(parts) if parts else str(element)

    def format_instruction(self, instruction: str, query: str, doc: str) -> str:
        if instruction is None:
            instruction = 'Identify which UI element the user should interact with for this task'
        return f"<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}"

    def process_inputs(self, pairs: List[str]) -> Dict:
        inputs = self.tokenizer(
            pairs,
            padding=False,
            truncation='longest_first',
            return_attention_mask=False,
            max_length=self.max_length - len(self.prefix_tokens) - len(self.suffix_tokens)
        )

        for i, ele in enumerate(inputs['input_ids']):
            inputs['input_ids'][i] = self.prefix_tokens + ele + self.suffix_tokens

        inputs = self.tokenizer.pad(
            inputs,
            padding=True,
            return_tensors="pt",
            max_length=self.max_length,
            pad_to_multiple_of=None,
            return_attention_mask=True
        )

        for key in inputs:
            inputs[key] = inputs[key].to(self.device)

        return inputs

    @torch.no_grad()
    def compute_scores(self, inputs: Dict) -> List[float]:
        batch_scores = self.model(**inputs).logits[:, -1, :]
        true_vector = batch_scores[:, self.token_true_id]
        false_vector = batch_scores[:, self.token_false_id]
        batch_scores = torch.stack([false_vector, true_vector], dim=1)
        batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
        scores = batch_scores[:, 1].exp().tolist()
        return scores

    async def load_model(self):
        logger.info(f"Loading model: {self.model_name}")
        start_time = time.time()

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            padding_side='left',
            revision="main"
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        logger.info(f"[OK] Tokenizer loaded (pad_token_id: {self.tokenizer.pad_token_id})")

        if self.use_gpu:
            logger.info("Loading with FP16 + GPU...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                revision="main",
                pad_token_id=self.tokenizer.pad_token_id
            ).cuda().eval()
        else:
            logger.info("Loading on CPU...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                revision="main",
                pad_token_id=self.tokenizer.pad_token_id
            ).eval()

        self.token_false_id = self.tokenizer.convert_tokens_to_ids("no")
        self.token_true_id = self.tokenizer.convert_tokens_to_ids("yes")

        prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
        suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        self.prefix_tokens = self.tokenizer.encode(prefix, add_special_tokens=False)
        self.suffix_tokens = self.tokenizer.encode(suffix, add_special_tokens=False)

        self.is_loaded = True
        logger.info(f"[OK] Model loaded in {time.time() - start_time:.2f}s")

        # Warmup
        logger.info("Warming up...")
        await self.rank_ui_elements("test task", [{"name": "test", "type": "Button"}])
        logger.info("[OK] Ready for UI element reranking")

    async def rank_ui_elements(
        self,
        task: str,
        ui_elements: List[Dict[str, Any]],
        instruction: Optional[str] = None,
        top_n: Optional[int] = None,
        expected_element: Optional[str] = None
    ) -> Dict[str, Any]:
        """Rank UI elements for a given task"""
        
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Format elements
        element_descriptions = [self.format_ui_element(elem) for elem in ui_elements]
        
        # Create query
        query = f"User task: {task}. Which UI element should be interacted with?"
        
        # Create pairs for ranking
        pairs = [self.format_instruction(instruction, query, desc) for desc in element_descriptions]
        
        # Rank
        inputs = self.process_inputs(pairs)
        scores = self.compute_scores(inputs)

        # Create results
        results = [
            {
                "index": i,
                "element": ui_elements[i],
                "description": element_descriptions[i],
                "relevance_score": score
            }
            for i, score in enumerate(scores)
        ]
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        if top_n:
            results = results[:top_n]

        inference_time = time.time() - start_time
        
        # Check accuracy if expected element provided
        accuracy = None
        correct = False
        if expected_element:
            top_element_name = results[0]['element'].get('name', '')
            correct = expected_element.lower() in top_element_name.lower()
            accuracy = 1.0 if correct else 0.0
        
        # Log request
        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "num_elements": len(ui_elements),
            "top_element": results[0]['element'].get('name', 'Unknown'),
            "top_score": results[0]['relevance_score'],
            "expected_element": expected_element,
            "correct": correct,
            "accuracy": accuracy,
            "inference_time_ms": inference_time * 1000
        }
        
        self.request_history.append(log_entry)
        self.total_requests += 1
        self.total_elements_ranked += len(ui_elements)
        
        # Log with accuracy info
        if accuracy is not None:
            status = "[OK] CORRECT" if correct else "[FAIL] WRONG"
            logger.info(
                f"[{request_id[:8]}] {status} | Task: '{task}' | "
                f"Predicted: '{results[0]['element'].get('name')}' ({results[0]['relevance_score']:.4f}) | "
                f"Expected: '{expected_element}' | Time: {inference_time*1000:.1f}ms"
            )
        else:
            logger.info(
                f"[{request_id[:8]}] Task: '{task}' | "
                f"Top: '{results[0]['element'].get('name')}' ({results[0]['relevance_score']:.4f}) | "
                f"Time: {inference_time*1000:.1f}ms"
            )

        return {
            "request_id": request_id,
            "results": results,
            "inference_time_ms": inference_time * 1000,
            "accuracy": accuracy
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get API statistics"""
        recent_requests = self.request_history[-100:]  # Last 100 requests
        
        with_accuracy = [r for r in recent_requests if r['accuracy'] is not None]
        avg_accuracy = sum(r['accuracy'] for r in with_accuracy) / len(with_accuracy) if with_accuracy else None
        
        correct_count = sum(1 for r in with_accuracy if r['correct'])
        
        return {
            "total_requests": self.total_requests,
            "total_elements_ranked": self.total_elements_ranked,
            "recent_accuracy": avg_accuracy,
            "recent_correct": correct_count,
            "recent_total": len(with_accuracy),
            "avg_inference_time_ms": sum(r['inference_time_ms'] for r in recent_requests) / len(recent_requests) if recent_requests else 0,
            "model": self.model_name,
            "device": self.device
        }


reranker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global reranker
    logger.info("Starting UI Reranking API...")
    reranker = UIReranker()
    await reranker.load_model()
    logger.info("API ready for UI element reranking")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="UI Element Reranking API",
    description="Rank UI elements by relevance to user tasks",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UIElement(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    bounds: Optional[Dict[str, int]] = None
    action: Optional[str] = None
    
    class Config:
        extra = "allow"

class UIRerankRequest(BaseModel):
    task: str = Field(..., description="The user's task description")
    elements: List[UIElement] = Field(..., description="List of UI elements to rank")
    top_n: Optional[int] = Field(default=None, description="Number of results to return")
    expected_element: Optional[str] = Field(default=None, description="Expected element name for accuracy tracking")

class UIRerankResult(BaseModel):
    index: int
    element: Dict[str, Any]
    description: str
    relevance_score: float

class UIRerankResponse(BaseModel):
    request_id: str
    results: List[UIRerankResult]
    inference_time_ms: float
    accuracy: Optional[float] = None

@app.post("/ui/rerank", response_model=UIRerankResponse)
async def rerank_ui_elements(request: UIRerankRequest):
    """Rank UI elements by relevance to task"""
    if not request.elements:
        raise HTTPException(400, "Elements list cannot be empty")
    if not request.task.strip():
        raise HTTPException(400, "Task cannot be empty")

    try:
        result = await reranker.rank_ui_elements(
            task=request.task,
            ui_elements=[elem.dict() for elem in request.elements],
            top_n=request.top_n,
            expected_element=request.expected_element
        )

        return UIRerankResponse(**result)

    except Exception as e:
        logger.error(f"Rerank failed: {e}", exc_info=True)
        raise HTTPException(500, f"Internal error: {str(e)}")

@app.get("/ui/stats")
async def get_stats():
    """Get API statistics and accuracy metrics"""
    if reranker is None or not reranker.is_loaded:
        raise HTTPException(503, "Model not loaded")

    stats = reranker.get_stats()
    return stats

@app.get("/ui/history")
async def get_history(limit: int = 20):
    """Get recent ranking history"""
    if reranker is None or not reranker.is_loaded:
        raise HTTPException(503, "Model not loaded")
    
    return {
        "history": reranker.request_history[-limit:]
    }

@app.get("/health")
async def health():
    if reranker is None or not reranker.is_loaded:
        raise HTTPException(503, "Model not loaded")

    return {
        "status": "healthy",
        "model": "Qwen/Qwen3-Reranker-0.6B",
        "device": reranker.device,
        "purpose": "UI Element Reranking"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8889, workers=1, log_level="info")
