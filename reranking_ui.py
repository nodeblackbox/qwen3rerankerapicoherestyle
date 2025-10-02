from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import time
import logging
from contextlib import asynccontextmanager

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QwenReranker:
    """GPU-accelerated reranker using Qwen3-Reranker-0.6B"""

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

        self.use_gpu = torch.cuda.is_available()
        self.device = "cuda" if self.use_gpu else "cpu"

        logger.info(f"Initializing reranker on: {self.device}")
        if self.use_gpu:
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    def format_instruction(self, instruction: str, query: str, doc: str) -> str:
        if instruction is None:
            instruction = 'Given a web search query, retrieve relevant passages that answer the query'
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

        # Pad with explicit pad_token_id
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
        
        # Set padding token - use eos_token (<|endoftext|> token ID 151643)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        logger.info(f"✓ Tokenizer loaded (pad_token_id: {self.tokenizer.pad_token_id})")

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
        logger.info(f"✓ Model loaded in {time.time() - start_time:.2f}s")

        # Warmup
        logger.info("Warming up...")
        await self.rank("test", ["doc1", "doc2"])
        logger.info("✓ Ready")

    def preprocess_ui_elements(self, ui_json: Dict, clickable_only: bool = True) -> List[Dict]:
        """Preprocess UI elements: filter, enrich with features"""
        elements = ui_json.get("elements", [])
        if not elements:
            raise ValueError("No elements found in UI JSON")

        clickable_types = {"ButtonControl", "HyperlinkControl", "TabItemControl", "EditControl"}
        processed = []
        max_depth = max(e.get("depth", 0) for e in elements)
        window_bounds = ui_json.get("window", {}).get("bounds", {"left": 0, "top": 0, "right": 1920, "bottom": 1080})
        window_center_x = (window_bounds.get("left", 0) + window_bounds.get("right", 1920)) / 2
        window_center_y = (window_bounds.get("top", 0) + window_bounds.get("bottom", 1080)) / 2
        max_area = 0
        max_dist = ((window_bounds.get("right", 1920) - window_bounds.get("left", 0)) ** 2 + 
                    (window_bounds.get("bottom", 1080) - window_bounds.get("top", 0)) ** 2) ** 0.5

        for idx, elem in enumerate(elements):
            elem_type = elem.get("type")
            name = elem.get("name", "").strip()
            if clickable_only and (elem_type not in clickable_types or not name):
                continue

            bounds = elem.get("bounds", {})
            left, top, right, bottom = bounds.get("left", 0), bounds.get("top", 0), bounds.get("right", 0), bounds.get("bottom", 0)
            area = max(0, (right - left) * (bottom - top))
            max_area = max(max_area, area)

            center_x = (left + right) / 2
            center_y = (top + bottom) / 2
            dist_to_center = ((center_x - window_center_x) ** 2 + (center_y - window_center_y) ** 2) ** 0.5
            position_score = max(0, 1 - (dist_to_center / max_dist if max_dist > 0 else 0))

            depth = elem.get("depth", 0)
            depth_norm = depth / max_depth if max_depth > 0 else 0

            processed.append({
                "index": idx,
                "element": elem,
                "area": area,
                "position_score": position_score,
                "depth_norm": depth_norm,
            })

        self._max_area = max_area  # Store for later normalization
        return processed

    async def rank(self, query: str, documents: Union[List[str], Dict], instruction: Optional[str] = None,
                   top_n: Optional[int] = None, ui_mode: bool = False, min_threshold: float = 0.5,
                   clickable_only: bool = True) -> List[Dict]:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        if ui_mode:
            # If documents is ui_json dict
            processed_elements = self.preprocess_ui_elements(documents, clickable_only)
            docs = [self.element_to_doc(el) for el in processed_elements]
            original_elements = processed_elements
        else:
            docs = documents
            original_elements = None

        if not docs:
            return []

        # Augment query for UI mode
        if ui_mode:
            query = f"The task is to {query}. Find the most relevant clickable UI element to perform the next action."
            if instruction is None:
                instruction = "Rank UI elements by how likely they are the next to click based on the query. Consider name relevance, type (buttons preferred), position (centered/large better)."

        # Batch processing
        batch_size = 32
        all_scores = []
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i:i+batch_size]
            pairs = [self.format_instruction(instruction, query, doc) for doc in batch_docs]
            inputs = self.process_inputs(pairs)
            scores = self.compute_scores(inputs)
            all_scores.extend(scores)

        results = []
        max_area = getattr(self, '_max_area', 1)
        for idx, score in enumerate(all_scores):
            if ui_mode:
                el = original_elements[idx]
                area_norm = el["area"] / max_area if max_area > 0 else 0
                final_score = score * (1 + el["position_score"] * 0.3 + area_norm * 0.2 - el["depth_norm"] * 0.1)
                suggested_action = "click" if el["element"]["type"] in {"ButtonControl", "HyperlinkControl", "TabItemControl"} else "type"
                element_details = el["element"]
                bounds = element_details.get("bounds", {})
                impl_tip = f"Click at center: x={(bounds.get('left',0) + bounds.get('right',0))/2}, y={(bounds.get('top',0) + bounds.get('bottom',0))/2}"
            else:
                final_score = score
                suggested_action = None
                element_details = None
                impl_tip = None

            if final_score >= min_threshold:
                results.append({
                    "index": idx if not ui_mode else el["index"],
                    "relevance_score": score,
                    "final_score": final_score,
                    "element_details": element_details,
                    "suggested_action": suggested_action,
                    "implementation_tip": impl_tip
                })

        results.sort(key=lambda x: x["final_score"], reverse=True)
        if top_n:
            results = results[:top_n]

        return results

    def element_to_doc(self, processed_elem: Dict) -> str:
        elem = processed_elem["element"]
        bounds = elem.get("bounds", {})
        return (f"Type: {elem.get('type')}, Name: {elem.get('name')}, "
                f"Position: left={bounds.get('left')},top={bounds.get('top')},right={bounds.get('right')},bottom={bounds.get('bottom')}, "
                f"Depth: {elem.get('depth')}, Area: {processed_elem['area']} pixels, Centrality: {processed_elem['position_score']:.2f}")

reranker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global reranker
    logger.info("Starting reranking API...")
    reranker = QwenReranker()
    await reranker.load_model()
    logger.info("API ready")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="Qwen3 Reranking API",
    description="Cohere-compatible reranking API using Qwen3-Reranker-0.6B with UI support",
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

class RerankRequest(BaseModel):
    model: str = Field(default="rerank-v3.5")
    query: str = Field(..., description="Search query")
    documents: List[str] = Field(..., description="Documents to rank")
    top_n: Optional[int] = Field(default=None, description="Number of results")

class RerankResult(BaseModel):
    index: int
    relevance_score: float

class ApiVersion(BaseModel):
    version: str = "2"
    is_experimental: bool = False

class BilledUnits(BaseModel):
    search_units: int = 1

class MetaInfo(BaseModel):
    api_version: ApiVersion
    billed_units: BilledUnits

class RerankResponse(BaseModel):
    results: List[RerankResult]
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meta: MetaInfo = Field(default_factory=lambda: MetaInfo(
        api_version=ApiVersion(),
        billed_units=BilledUnits()
    ))

class UiRerankRequest(BaseModel):
    model: str = Field(default="rerank-v3.5")
    query: str = Field(..., description="UI task query")
    ui_elements: Dict[str, Any] = Field(..., description="UI JSON structure")
    top_n: Optional[int] = Field(default=None)
    min_threshold: float = Field(default=0.5)
    clickable_only: bool = Field(default=True)
    instruction: Optional[str] = None

class UiRerankResult(BaseModel):
    index: int
    relevance_score: float
    final_score: float
    element_details: Optional[Dict]
    suggested_action: Optional[str]
    implementation_tip: Optional[str]

class UiRerankResponse(BaseModel):
    results: List[UiRerankResult]
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meta: MetaInfo = Field(default_factory=lambda: MetaInfo(
        api_version=ApiVersion(),
        billed_units=BilledUnits()
    ))

@app.post("/v2/rerank", response_model=RerankResponse)
async def rerank(request: RerankRequest):
    """Rerank documents by relevance to query (Cohere-compatible endpoint)"""
    if not request.documents:
        raise HTTPException(400, "Documents list cannot be empty")
    if not request.query.strip():
        raise HTTPException(400, "Query cannot be empty")

    try:
        results = await reranker.rank(
            query=request.query,
            documents=request.documents,
            top_n=request.top_n
        )

        rerank_results = [
            RerankResult(index=r["index"], relevance_score=r["relevance_score"])
            for r in results
        ]

        return RerankResponse(results=rerank_results)

    except Exception as e:
        logger.error(f"Rerank failed: {e}")
        raise HTTPException(500, f"Internal error: {str(e)}")

@app.post("/v2/ui_rerank", response_model=UiRerankResponse)
async def ui_rerank(request: UiRerankRequest):
    """Rerank UI elements for next action prediction"""
    if not request.ui_elements:
        raise HTTPException(400, "UI elements cannot be empty")
    if not request.query.strip():
        raise HTTPException(400, "Query cannot be empty")

    try:
        results = await reranker.rank(
            query=request.query,
            documents=request.ui_elements,
            instruction=request.instruction,
            top_n=request.top_n,
            ui_mode=True,
            min_threshold=request.min_threshold,
            clickable_only=request.clickable_only
        )

        ui_results = [
            UiRerankResult(
                index=r["index"],
                relevance_score=r["relevance_score"],
                final_score=r["final_score"],
                element_details=r["element_details"],
                suggested_action=r["suggested_action"],
                implementation_tip=r["implementation_tip"]
            )
            for r in results
        ]

        if not ui_results:
            logger.warning("No matching UI elements found above threshold")

        return UiRerankResponse(results=ui_results)

    except Exception as e:
        logger.error(f"UI Rerank failed: {e}")
        raise HTTPException(500, f"Internal error: {str(e)}")

@app.get("/health")
async def health():
    if reranker is None or not reranker.is_loaded:
        raise HTTPException(503, "Model not loaded")

    return {
        "status": "healthy",
        "model": "Qwen/Qwen3-Reranker-0.6B",
        "device": reranker.device
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, workers=1, log_level="info")