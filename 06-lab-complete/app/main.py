"""
Production AI Agent — Final Assembly (Lab 06 Complete)
Combining Security, Reliability, and Scaling.
"""
import os
import time
import signal
import logging
import json
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Security, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from app.config import settings
from app.auth import verify_api_key, verify_token, verify_any_auth, authenticate_user, create_token
from app.rate_limiter import rate_limiter
from app.cost_guard import cost_guard
from app.session import session_manager
from utils.mock_llm import ask as llm_ask

# ─────────────────────────────────────────────────────────
# Logging & Stats
# ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
INSTANCE_ID = os.getenv("INSTANCE_ID", f"instance-{uuid.uuid4().hex[:6]}")
_is_ready = False
_in_flight_requests = 0

# ─────────────────────────────────────────────────────────
# Lifespan (Startup/Shutdown)
# ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info(json.dumps({
        "event": "startup",
        "instance": INSTANCE_ID,
        "env": settings.environment,
        "redis": "connected" if settings.redis_url else "none"
    }))
    # Initialization logic here (e.g. warming up models)
    _is_ready = True
    yield
    _is_ready = False
    logger.info(json.dumps({"event": "shutdown", "instance": INSTANCE_ID}))

from fastapi.staticfiles import StaticFiles

# ─────────────────────────────────────────────────────────
# App & Middleware
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url=None,    # Hide Swagger UI
    redoc_url=None,   # Hide Redoc
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

@app.middleware("http")
async def monitor_middleware(request: Request, call_next):
    global _in_flight_requests
    start = time.time()
    _in_flight_requests += 1
    try:
        response: Response = await call_next(request)
        # Security Hardening
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        if "server" in response.headers:
            del response.headers["server"]
        
        duration = round((time.time() - start) * 1000, 1)
        logger.info(json.dumps({
            "event": "http",
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "ms": duration,
            "instance": INSTANCE_ID
        }))
        return response
    finally:
        _in_flight_requests -= 1

# ─────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)

class AskResponse(BaseModel):
    question: str
    answer: str
    session_id: str
    instance: str
    timestamp: str

# ─────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────



@app.post("/login", response_model=TokenResponse, tags=["Security"])
async def login(body: LoginRequest):
    """Authenticate user and return a JWT token."""
    user = authenticate_user(body.username, body.password)
    token = create_token(user["username"], user["role"])
    return {"access_token": token, "token_type": "bearer"}

@app.post("/ask", response_model=AskResponse, tags=["Agent"])
async def ask_agent(
    body: AskRequest,
    # Priority 1: JWT Auth, Fallback: API Key
    user: dict = Depends(verify_any_auth), 
):
    user_id = user["username"]
    
    # 1. Rate Limiting (Redis-backed if available)
    rate_limiter.check(user_id)

    # 2. Budget Check
    cost_guard.check_budget(user_id)

    # 3. Process LLM Call with History
    history = session_manager.get_history(user_id)
    input_tokens = len(body.question.split()) * 2
    
    # Ask LLM with context
    answer = llm_ask(body.question, history=history)
    output_tokens = len(answer.split()) * 2

    # 4. Record Usage & Update History (Redis)
    cost_guard.record_usage(user_id, input_tokens, output_tokens)
    session_manager.add_message(user_id, "user", body.question)
    session_manager.add_message(user_id, "bot", answer)

    return AskResponse(
        question=body.question,
        answer=answer,
        session_id=user_id,
        instance=INSTANCE_ID,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.get("/health", tags=["Operations"])
def health():
    return {
        "status": "ok",
        "instance": INSTANCE_ID,
        "uptime": round(time.time() - START_TIME, 1)
    }

@app.get("/ready", tags=["Operations"])
def ready():
    if not _is_ready:
        raise HTTPException(503, "Service starting up...")
    return {"status": "ready", "instance": INSTANCE_ID}

@app.get("/metrics", tags=["Operations"])
def metrics(auth: str = Depends(verify_api_key)):
    """Secret endpoint for monitoring (API Key required)."""
    return {
        "in_flight": _in_flight_requests,
        "uptime": time.time() - START_TIME,
        "budget_stats": cost_guard.get_stats("global") # Simplified stats
    }

# ─────────────────────────────────────────────────────────
# Signal Handling (SIGTERM)
# ─────────────────────────────────────────────────────────
def handle_sigterm(*args):
    global _is_ready
    logger.info(f"Received SIGTERM. Transitioning to unready...")
    _is_ready = False # Stop receiving new traffic from Load Balancer

signal.signal(signal.SIGTERM, handle_sigterm)

# ─────────────────────────────────────────────────────────
# Static Files (UI)
# ─────────────────────────────────────────────────────────
# Mount at root / so index.html is served automatically
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        timeout_graceful_shutdown=30
    )
