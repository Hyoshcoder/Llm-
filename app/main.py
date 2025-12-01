from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import logging

from .config import RATE_LIMIT, MODEL_NAME
from .auth import verify_token
from .llm import generate_response, load_model
from .schemas import ChatRequest, ChatResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llama-secure-api")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Llama Secure API")

app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Preload model async-safe by calling load_model once (it uses lru_cache)
    try:
        load_model()
        logger.info("Model preloaded")
    except Exception as e:
        logger.warning(f"Model preload failed: {e}")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/model")
async def model_info():
    return {"model": MODEL_NAME}

@app.post("/chat", response_model=ChatResponse)
@limiter.limit(RATE_LIMIT)
async def chat(req: ChatRequest, ok: bool = Depends(verify_token)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")
    try:
        resp = generate_response(req.message)
        return {"response": resp}
    except Exception as e:
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=str(e))
