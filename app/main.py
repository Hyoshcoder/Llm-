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

# ------------------------------
# Initialize FastAPI & Limiter
# ------------------------------
app = FastAPI(title="Llama Secure API")

# Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter  # ⚡ fix slowapi error

# Middleware
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à limiter en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Startup event: preload model
# ------------------------------
@app.on_event("startup")
async def startup_event():
    try:
        load_model(dtype="float16", use_auth_token=None)  # ⚡ fix warnings
        logger.info("Model preloaded")
    except Exception as e:
        logger.warning(f"Model preload failed: {e}")

# ------------------------------
# Health check
# ------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# ------------------------------
# Model info
# ------------------------------
@app.get("/model")
async def model_info():
    return {"model": MODEL_NAME}

# ------------------------------
# Chat endpoint
# ------------------------------
@app.post("/chat", response_model=ChatResponse)
@limiter.limit(RATE_LIMIT)
async def chat(request: Request, req: ChatRequest, ok: bool = Depends(verify_token)):
    """
    POST /chat
    Body: {"message": "..."}
    Header: Authorization: Bearer <API_KEY>
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")
    try:
        resp = generate_response(req.message)
        return {"response": resp}
    except Exception as e:
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=str(e))
