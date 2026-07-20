"""
backend/main.py

Syllabot FastAPI application entrypoint.

Configured with:
  - Structured JSON logging (initialised on startup)
  - Rate limiting via slowapi (100 req/min global, 20 req/min for AI endpoints)
  - CORS locked to FRONTEND_URL in production (open in dev if not set)
  - All API routers registered under /api/v1
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.core.config import settings
from backend.core.logging_config import setup_logging
import backend.models.base
from backend.api.v1 import auth, syllabi, plans, progress
from backend.ai import router as ai_router

# ── Logging ───────────────────────────────────────────────────────────────────
setup_logging()
logger = logging.getLogger("syllabot.main")

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Agentic AI Study Planning Platform — "
        "LangGraph-powered adaptive syllabus management and study scheduling API."
    ),
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Attach rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
# In production, FRONTEND_URL must be set in .env to restrict origins.
# In development (FRONTEND_URL not set), all origins are allowed.
if settings.FRONTEND_URL:
    base_origin = settings.FRONTEND_URL.rstrip("/")
    allowed_origins = [base_origin]
    
    # Automatically support both localhost and 127.0.0.1 local development variants
    if "localhost" in base_origin:
        allowed_origins.append(base_origin.replace("localhost", "127.0.0.1"))
    elif "127.0.0.1" in base_origin:
        allowed_origins.append(base_origin.replace("127.0.0.1", "localhost"))
        
    logger.info("CORS locked to origins", extra={"origins": allowed_origins})
else:
    allowed_origins = ["*"]
    logger.warning("CORS is open to all origins — set FRONTEND_URL in .env for production")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"]
)
app.include_router(
    syllabi.router,
    prefix=f"{settings.API_V1_STR}/syllabi",
    tags=["Syllabi Ingestion"]
)
app.include_router(
    plans.router,
    prefix=f"{settings.API_V1_STR}/plans",
    tags=["Study Plans"]
)
app.include_router(
    progress.router,
    prefix=f"{settings.API_V1_STR}/progress",
    tags=["Daily Progress & Tracking"]
)
app.include_router(
    ai_router.router,
    prefix=f"{settings.API_V1_STR}/ai",
    tags=["AI Study Assistant"]
)

# ── Lifecycle Events ──────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    """
    Runs on application startup.
    Initialises the LangGraph workflow singleton and logs provider status.
    """
    logger.info(f"Starting {settings.PROJECT_NAME} v2.0.0")

    # Warm up the LangGraph graph (compiles the StateGraph once)
    try:
        from backend.ai.graph.workflow import get_compiled_graph
        get_compiled_graph()
        logger.info("LangGraph workflow compiled and ready")
    except Exception as e:
        logger.warning("LangGraph compilation failed on startup — will retry on first request", extra={"error": str(e)})

    # Log provider availability status
    try:
        from backend.ai.providers.router import get_model_router
        router = get_model_router()
        status = router.status()
        logger.info("AI provider status", extra={"providers": status})
    except Exception as e:
        logger.warning("Could not check AI provider status", extra={"error": str(e)})


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health Check"])
def root():
    """
    Root health-check endpoint.
    Returns basic application status and AI provider availability.
    """
    try:
        from backend.ai.providers.router import get_model_router
        provider_status = get_model_router().status()
    except Exception:
        provider_status = {"any_available": False}

    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": "2.0.0",
        "docs_url": "/docs",
        "ai_providers": provider_status,
    }
