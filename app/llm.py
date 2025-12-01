from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from .config import MODEL_NAME, MAX_NEW_TOKENS, HF_TOKEN
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def load_model():
    """
    Charge le modèle et le tokenizer depuis HuggingFace.
    Utilise le token HF_TOKEN si le modèle est gated.
    """
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    logger.info(f"Loading model {MODEL_NAME} with dtype={dtype}")

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            use_fast=True,
            use_auth_token=HF_TOKEN
        )
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=dtype,
            device_map='auto',
            use_auth_token=HF_TOKEN
        )
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model {MODEL_NAME}: {e}")
        raise

    return tokenizer, model

def generate_response(prompt: str) -> str:
    """
    Génère une réponse à partir du prompt donné en utilisant le modèle chargé.
    """
    tokenizer, model = load_model()
    inputs = tokenizer(prompt, return_tensors='pt').to(model.device)

    try:
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.7,
            top_p=0.95
        )
        text = tokenizer.decode(output[0], skip_special_tokens=True)
        return text
    except Exception as e:
        logger.exception("Generation failed")
        raise