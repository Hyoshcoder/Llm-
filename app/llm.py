from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from .config import MODEL_NAME, MAX_NEW_TOKENS
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def load_model():
    # Lazy load model once
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    logger.info(f"Loading model {MODEL_NAME} with dtype={dtype}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=dtype,
        device_map='auto'
    )
    return tokenizer, model

def generate_response(prompt: str):
    tokenizer, model = load_model()
    inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
    out = model.generate(
        **inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        temperature=0.7,
        top_p=0.95
    )
    text = tokenizer.decode(out[0], skip_special_tokens=True)
    return text
