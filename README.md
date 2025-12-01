# 🦙 Llama Secure API — FastAPI + Meta-Llama (Quickstart)

API sécurisée pour interagir avec un modèle Meta-Llama (ex: Llama-3.x) via FastAPI.

Features:
- FastAPI REST endpoints: /health, /model, /chat
- Simple Bearer API Key auth (configurable via .env)
- Rate limiting with slowapi
- CORS middleware
- Dockerfile for containerized deployment
- Example .env.example

Quickstart:
1) git clone <your-repo>
2) cp .env.example .env
3) pip install -r requirements.txt
4) uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Environment:
- Set API_KEY in .env
- Set MODEL_NAME to the desired model (HuggingFace or local path)

Endpoints:
- GET /health — status
- GET /model — current model name
- POST /chat — { "message": "..." } -> protected, requires Authorization: Bearer <API_KEY>

Docker:
1) docker build -t llama-secure-api .
2) docker run --env-file .env -p 8000:8000 llama-secure-api

Notes:
- This repo is a quickstart. For production: enable secure secret storage, use GPU-optimized image,
  better auth (JWT/OAuth2), monitoring and process manager (gunicorn/uvicorn workers).
