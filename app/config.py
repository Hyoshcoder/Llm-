from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY", "dev_key")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "256"))
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")
